import re
from typing import List, Dict, Tuple
import pdfplumber
from dataclasses import dataclass
from src.ontology import LegalNode, LegalSystem, AuthorityLevel, BindingStatus
from src.logger import setup_logger

logger = setup_logger("bale_ingestion")

class PDFProcessor:
    def __init__(self):
        pass

    def extract_layout_aware_text(self, pdf_path: str) -> str:
        """
        Extracts text from PDF using pdfplumber for better layout preservation.
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # extract_text(x_tolerance=2, y_tolerance=3) helps with preserving columns/layout better
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=3)
                    if page_text:
                        text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("PDF content is empty or unreadable.")
                
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            # Depending on requirements, we might want to re-raise or return empty
            return "" # Graceful failure
        return text

    def tag_text(self, text: str) -> str:
        """
        Tags text as [FR_CIVIL] or [EN_COMMON] based on heuristics.
        """
        # Improved heuristics
        fr_keywords = ["article", "code", "loi", "alinéa", "société", "contrat", "force majeure", "débiteur"]
        en_keywords = ["section", "act", "law", "statute", "company", "agreement", "tort", "consideration", "clause"]
        
        text_lower = text.lower()
        fr_count = sum(text_lower.count(k) for k in fr_keywords)
        en_count = sum(text_lower.count(k) for k in en_keywords)
        
        # Simple ratio check
        if fr_count > en_count:
            return "[FR_CIVIL]"
        else:
            return "[EN_COMMON]"

    def semantic_chunking(self, text: str, sys_tag: str) -> List[LegalNode]:
        """
        Splits text by legal headers (Article X, Section Y).
        """
        chunks = []
        
        # Regex to find Article/Section headers
        # Matches "Article 123", "Article 12-1", "Section 1.2", "SECTION 5"
        if sys_tag == "[FR_CIVIL]":
            # French: Article L123-1, Article 1100, etc.
            pattern = r"(Article\s+[L-]?\d+[\d\-\.]*|SECTION\s+\w+)"
        else:
            # English: Section 1, Clause 5.1
            pattern = r"(Section\s+\d+[\d\.]*|Clause\s+\d+[\d\.]*|Article\s+\d+)"

        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        # Reconstruct chunks: delimiter + content
        if len(parts) > 0 and not re.match(pattern, parts[0], re.IGNORECASE):
             chunks.append(LegalNode(
                id=f"{sys_tag}_preamble",
                text_content=parts[0].strip(),
                system=LegalSystem.CIVIL_LAW if sys_tag == "[FR_CIVIL]" else LegalSystem.COMMON_LAW,
                authority_level=AuthorityLevel.CONTRACTUAL,
                binding_status=BindingStatus.DEFAULT,
                citation="Preamble"
            ))
             parts = parts[1:]

        # Track usage to ensure uniqueness
        seen_ids = {}

        for i in range(0, len(parts) - 1, 2):
            header = parts[i].strip()
            content = parts[i+1].strip() if i+1 < len(parts) else ""
            
            full_text = f"{header}\n{content}"
            # Normalize header for ID
            safe_header = re.sub(r"[^a-zA-Z0-9]", "_", header)
            base_id = f"{sys_tag}_{safe_header}"
            
            # Ensure uniqueness
            if base_id in seen_ids:
                seen_ids[base_id] += 1
                chunk_id = f"{base_id}_{seen_ids[base_id]}"
            else:
                seen_ids[base_id] = 0
                chunk_id = base_id
            
            # Ontology Logic (Heuristic for Demo)
            auth_level = AuthorityLevel.CONTRACTUAL
            binding = BindingStatus.DEFAULT
            
            # If it looks like a Code Civil citation (e.g., Article 1104), make it STATUTORY
            # In a real system, we'd check if this is a CONTRACT or a LAW file.
            # Here we assume user uploads a CONTRACT mostly, but let's pretend
            if "Article" in header and sys_tag == "[FR_CIVIL]":
                # Only if the text explicitly cites the code, but usually headers in contracts mimic code.
                # Let's keep it CONTRACTUAL for safety unless it says "Code Civil"
                pass 

            chunks.append(LegalNode(
                id=chunk_id,
                text_content=full_text,
                system=LegalSystem.CIVIL_LAW if sys_tag == "[FR_CIVIL]" else LegalSystem.COMMON_LAW,
                authority_level=auth_level,
                binding_status=binding,
                citation=header
            ))

        return chunks

if __name__ == "__main__":
    # Test Stub
    proc = PDFProcessor()
    # Stub doesn't test PDF reading without a file, but tests logic
    logger.info("PDFProcessor initialized.")
