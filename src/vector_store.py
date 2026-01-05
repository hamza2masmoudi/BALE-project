import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np

# Use a local embedding model for the prototype to avoid API dependency issues immediately
# In production, swap with Cohere or OpenAI
class LocalEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        # sentence-transformers returns numpy array, convert to list
        embeddings = self.model.encode(input).tolist()
        return embeddings

class VectorEngine:
    def __init__(self, persist_path="./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.embedding_fn = LocalEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="legal_docs",
            embedding_function=self.embedding_fn
        )
        self.bm25 = None
        self.doc_store = {} # Map ID to text for BM25 retrieval
        self.doc_ids = []

    def add_documents(self, chunks: List[Any]):
        """
        Adds LegalNode objects to the store.
        """
        ids = [c.id for c in chunks]
        documents = [c.text_content for c in chunks]
        
        # Convert Pydantic/Enums to simple dict for Chroma
        metadatas = []
        for c in chunks:
            meta = {
                "system": c.system.value,
                "authority_level": c.authority_level.value,
                "binding_status": c.binding_status.value,
                "citation": c.citation or ""
            }
            metadatas.append(meta)

        # Add to Chroma
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        # Update in-memory BM25 (re-indexing for simplicity in prototype)
        # In a real app, you'd want to handle this more efficiently
        self._update_bm25(ids, documents)

    def _update_bm25(self, ids, documents):
        self.doc_ids = ids
        self.doc_store = {ids[i]: documents[i] for i in range(len(ids))}
        tokenized_corpus = [doc.split(" ") for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def hybrid_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Performs Hybrid Search (Dense + Sparse) with RRF.
        """
        # 1. Dense Search (Chroma)
        dense_results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        dense_hits = []
        if dense_results['ids']:
            ids = dense_results['ids'][0]
            docs = dense_results['documents'][0] if 'documents' in dense_results else []
            metas = dense_results['metadatas'][0] if 'metadatas' in dense_results else []
            
            for i, doc_id in enumerate(ids):
                dense_hits.append({
                    "id": doc_id,
                    "content": docs[i] if docs else "",
                    "metadata": metas[i] if metas else {}
                })

        # 2. Sparse Search (BM25)
        sparse_hits = []
        if self.bm25:
            tokenized_query = query.split(" ")
            # Get top k from BM25
            # BM25Okapi get_top_n returns the documents, not IDs directly easily without mapping
            # So we use get_scores
            scores = self.bm25.get_scores(tokenized_query)
            top_n_indices = np.argsort(scores)[::-1][:k]
            
            for idx in top_n_indices:
                doc_id = self.doc_ids[idx]
                sparse_hits.append({
                    "id": doc_id,
                    "content": self.doc_store[doc_id],
                    "metadata": {} # We might need to store metadata in doc_store if needed here
                })

        # 3. Reciprocal Rank Fusion
        fused_results = self._rrf(dense_hits, sparse_hits, k=k)
        return fused_results

    def _rrf(self, dense_hits, sparse_hits, k=5, k_rrf=60):
        """
        Combines results.
        """
        rank_scores = {}
        
        # Helper to process list
        def process_list(hit_list):
            for rank, hit in enumerate(hit_list):
                doc_id = hit['id']
                if doc_id not in rank_scores:
                    rank_scores[doc_id] = {"score": 0, "hit": hit}
                
                # RRF formula: 1 / (k + rank)
                base_score = 1 / (k_rrf + rank + 1)
                
                # Authority Boosting (Partner Requirement)
                # We retrieve metadata from the hit to apply weight
                meta = hit.get("metadata", {})
                if meta:
                    auth_level = meta.get("authority_level", 30) # Default Contractual
                    binding = meta.get("binding_status", "DEFAULT")
                    
                    # Logarithmic boost: Constitution (100) vs Contract (30)
                    # Simple factor: 1.0 + (Level / 200)
                    boost = 1.0 + (auth_level / 200.0)
                    
                    if binding == "MANDATORY":
                        boost *= 1.2
                    
                    base_score *= boost
                
                rank_scores[doc_id]["score"] += base_score

        process_list(dense_hits)
        process_list(sparse_hits)

        # Sort by score
        sorted_ids = sorted(rank_scores, key=lambda x: rank_scores[x]["score"], reverse=True)
        
        final_results = []
        for doc_id in sorted_ids[:k]:
            final_results.append(rank_scores[doc_id]["hit"])
            
        return final_results

if __name__ == "__main__":
    # Test Stub
    db = VectorEngine()
    from src.ingestion import LegalChunk
    
    chunks = [
        LegalChunk("Article 1100: Contract law basics", {"tag": "FR"}, "fr_1"),
        LegalChunk("Section 5: Offer and Acceptance", {"tag": "EN"}, "en_1")
    ]
    
    db.add_documents(chunks)
    res = db.hybrid_search("contract law")
    print(f"Results: {res}")
