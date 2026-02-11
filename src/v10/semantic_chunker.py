"""
BALE V11 Semantic Chunker
Splits contract text into semantically coherent chunks using embedding similarity.

Innovation: Replaces regex number-matching with semantic boundary detection.
Uses the same MiniLM encoder already loaded — zero additional model cost.
"""
import re
import numpy as np
from typing import List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger("bale_v11_chunker")


@dataclass
class SemanticChunk:
    """A semantically coherent chunk of contract text."""
    id: str
    text: str
    start_pos: int  # character position in original text
    end_pos: int
    header: str  # extracted or inferred header
    boundary_scores: List[float]  # similarity drops at boundaries
    coherence_score: float  # internal coherence (0-1)


class SemanticChunker:
    """
    Splits contract text into semantically coherent chunks.
    
    How it works:
    1. Split text into sentences (lightweight regex)
    2. Compute embeddings for sliding windows of N sentences
    3. Calculate cosine similarity between consecutive windows
    4. SPLIT where similarity drops below threshold (= topic shift)
    
    Result: Each chunk contains text about ONE legal topic,
    regardless of how the contract is formatted.
    """

    def __init__(
        self,
        encoder=None,
        window_size: int = 3,
        threshold: float = 0.40,
        min_chunk_chars: int = 80,
        max_chunk_chars: int = 3000,
    ):
        self._encoder = encoder
        self.window_size = window_size
        self.threshold = threshold
        self.min_chunk_chars = min_chunk_chars
        self.max_chunk_chars = max_chunk_chars
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy init to avoid loading model if not needed."""
        if self._initialized:
            return
        if self._encoder is None:
            from src.v10.classifier_v10 import get_classifier
            classifier = get_classifier(multilingual=True)
            self._encoder = classifier.model
        self._initialized = True

    def chunk(self, text: str) -> List[SemanticChunk]:
        """
        Split contract text into semantic chunks.
        Falls back to regex chunking for very short texts.
        """
        self._ensure_initialized()

        # Try regex first for well-structured contracts
        regex_chunks = self._try_regex_chunking(text)
        if regex_chunks and len(regex_chunks) >= 4:
            return regex_chunks

        # Semantic chunking
        sentences = self._split_sentences(text)

        if len(sentences) < self.window_size * 2:
            # Too short for semantic chunking, use paragraph splitting
            return self._paragraph_fallback(text)

        # Compute windowed embeddings
        windows = []
        for i in range(len(sentences) - self.window_size + 1):
            window_text = " ".join(sentences[i:i + self.window_size])
            windows.append(window_text)

        if not windows:
            return self._paragraph_fallback(text)

        embeddings = self._encoder.encode(
            windows, normalize_embeddings=True,
            show_progress_bar=False, batch_size=32,
        )

        # Calculate similarity between consecutive windows
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = float(np.dot(embeddings[i], embeddings[i + 1]))
            similarities.append(sim)

        # Find split points: where similarity drops below threshold
        split_indices = self._find_boundaries(similarities, sentences)

        # Build chunks from split points
        chunks = self._build_chunks(text, sentences, split_indices, similarities)

        logger.info(
            f"Semantic chunking: {len(sentences)} sentences -> "
            f"{len(chunks)} chunks (threshold={self.threshold})"
        )

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Handle common abbreviations to avoid false splits
        text_clean = text.replace("e.g.", "eg").replace("i.e.", "ie")
        text_clean = text_clean.replace("etc.", "etc").replace("vs.", "vs")
        text_clean = text_clean.replace("No.", "No").replace("Art.", "Art")
        text_clean = text_clean.replace("Sec.", "Sec").replace("Ltd.", "Ltd")

        # Split on sentence boundaries
        sentences = re.split(
            r'(?<=[.!?;])\s+(?=[A-Z0-9("])',
            text_clean
        )

        # Also split on numbered sections
        expanded = []
        for sent in sentences:
            parts = re.split(r'(?=\n\s*\d{1,2}\.\s+[A-Z])', sent)
            expanded.extend(parts)

        # Filter out very short fragments
        result = [s.strip() for s in expanded if len(s.strip()) > 15]
        return result

    def _find_boundaries(
        self,
        similarities: List[float],
        sentences: List[str],
    ) -> List[int]:
        """Find optimal boundary positions using adaptive threshold."""
        if not similarities:
            return []

        # Use local minimum detection with adaptive threshold
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities) if len(similarities) > 2 else 0.1

        # Threshold: below mean - 0.5 * std, or absolute threshold
        adaptive_threshold = min(self.threshold, mean_sim - 0.5 * std_sim)
        adaptive_threshold = max(0.2, adaptive_threshold)  # floor

        boundaries = []
        for i, sim in enumerate(similarities):
            # Check if this is a local minimum and below threshold
            is_local_min = True
            if i > 0 and similarities[i - 1] <= sim:
                is_local_min = False
            if i < len(similarities) - 1 and similarities[i + 1] <= sim:
                is_local_min = False

            if sim < adaptive_threshold or (is_local_min and sim < mean_sim - 0.3 * std_sim):
                # Map window index back to sentence index
                # The boundary is at sentence index i + window_size
                sent_idx = i + self.window_size
                if sent_idx < len(sentences):
                    boundaries.append(sent_idx)

        return sorted(set(boundaries))

    def _build_chunks(
        self,
        original_text: str,
        sentences: List[str],
        boundaries: List[int],
        similarities: List[float],
    ) -> List[SemanticChunk]:
        """Build SemanticChunks from boundary positions."""
        chunks = []

        # Add start and end
        all_boundaries = [0] + boundaries + [len(sentences)]

        for i in range(len(all_boundaries) - 1):
            start = all_boundaries[i]
            end = all_boundaries[i + 1]

            chunk_sentences = sentences[start:end]
            chunk_text = " ".join(chunk_sentences).strip()

            if len(chunk_text) < self.min_chunk_chars and chunks:
                # Merge tiny chunk with previous
                chunks[-1] = SemanticChunk(
                    id=chunks[-1].id,
                    text=chunks[-1].text + " " + chunk_text,
                    start_pos=chunks[-1].start_pos,
                    end_pos=chunks[-1].end_pos + len(chunk_text),
                    header=chunks[-1].header,
                    boundary_scores=chunks[-1].boundary_scores,
                    coherence_score=chunks[-1].coherence_score,
                )
                continue

            # Split oversized chunks
            if len(chunk_text) > self.max_chunk_chars:
                sub_chunks = self._split_oversized(chunk_text, len(chunks))
                chunks.extend(sub_chunks)
                continue

            # Extract header from first line
            header = self._extract_header(chunk_text)

            # Calculate coherence = average similarity within chunk
            chunk_sims = []
            for j in range(max(0, start - 1), min(len(similarities), end)):
                chunk_sims.append(similarities[j])
            coherence = float(np.mean(chunk_sims)) if chunk_sims else 0.5

            # Approximate character positions
            start_pos = sum(len(s) + 1 for s in sentences[:start])
            end_pos = start_pos + len(chunk_text)

            # Boundary scores at this chunk's edges
            boundary_scores_list = []
            if start > 0 and start - 1 < len(similarities):
                boundary_scores_list.append(similarities[start - 1])
            if end - 1 < len(similarities):
                boundary_scores_list.append(similarities[end - 1])

            chunks.append(SemanticChunk(
                id=f"section_{len(chunks)}",
                text=chunk_text,
                start_pos=start_pos,
                end_pos=end_pos,
                header=header,
                boundary_scores=boundary_scores_list,
                coherence_score=round(coherence, 3),
            ))

        return chunks

    def _split_oversized(self, text: str, base_idx: int) -> List[SemanticChunk]:
        """Split an oversized chunk into smaller pieces."""
        parts = []
        paragraphs = text.split("\n\n")
        current = ""
        for para in paragraphs:
            if len(current) + len(para) > self.max_chunk_chars and current:
                parts.append(current.strip())
                current = para
            else:
                current += "\n\n" + para if current else para
        if current.strip():
            parts.append(current.strip())

        return [
            SemanticChunk(
                id=f"section_{base_idx + i}",
                text=part,
                start_pos=0,
                end_pos=len(part),
                header=self._extract_header(part),
                boundary_scores=[],
                coherence_score=0.5,
            )
            for i, part in enumerate(parts)
        ]

    def _extract_header(self, text: str) -> str:
        """Extract a header from the first line of text."""
        first_line = text.split("\n")[0].strip()
        # Check for numbered section header
        match = re.match(
            r'(?:Section|Article|Clause)?\s*\d{1,2}\.?\s*(.+)',
            first_line, re.IGNORECASE
        )
        if match:
            header = match.group(1).strip()
            # Trim to reasonable length
            return header[:80] if len(header) > 80 else header
        return first_line[:80] if len(first_line) > 80 else first_line

    def _try_regex_chunking(self, text: str) -> List[SemanticChunk]:
        """Try regex-based chunking for well-structured contracts."""
        pattern = r'(?=(?:^|\n)\s*(?:(?:Section|Article|Clause)\s+)?\d{1,2}\.\s+[A-Z])'
        sections = re.split(pattern, text, flags=re.IGNORECASE)

        if len(sections) < 4:
            return []

        chunks = []
        for i, section in enumerate(sections):
            section = section.strip()
            if len(section) < self.min_chunk_chars:
                continue
            header = self._extract_header(section)
            chunks.append(SemanticChunk(
                id=f"section_{i}",
                text=section[:self.max_chunk_chars],
                start_pos=0,
                end_pos=len(section),
                header=header,
                boundary_scores=[],
                coherence_score=0.7,  # assume decent coherence for structured text
            ))

        return chunks

    def _paragraph_fallback(self, text: str) -> List[SemanticChunk]:
        """Fallback: split on double newlines."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        return [
            SemanticChunk(
                id=f"clause_{i}",
                text=p[:self.max_chunk_chars],
                start_pos=0,
                end_pos=len(p),
                header=self._extract_header(p),
                boundary_scores=[],
                coherence_score=0.5,
            )
            for i, p in enumerate(paragraphs)
        ]


__all__ = ["SemanticChunker", "SemanticChunk"]
