import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import os

# --- Load Models and Data ONCE ---
FAISS_INDEX_FILE = "knowledge.index"
METADATA_FILE = "chunk_metadata.json"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
RERANKER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

print(f"Loading RAG components...")

# 1. Load Embedding Model (for Vector Search)
try:
    EMBED_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"✅ Embedding Model loaded: {EMBEDDING_MODEL_NAME}")
except Exception as e:
    print(f"❌ Error loading embedding model: {e}")
    EMBED_MODEL = None

# 2. Load Re-Ranker Model (The "Judge")
try:
    RERANKER = CrossEncoder(RERANKER_MODEL_NAME)
    print(f"✅ Re-Ranker Model loaded: {RERANKER_MODEL_NAME}")
except Exception as e:
    print(f"❌ Error loading re-ranker: {e}")
    RERANKER = None

# 3. Load FAISS Index
try:
    INDEX = faiss.read_index(FAISS_INDEX_FILE)
    print(f"✅ FAISS Index loaded.")
except Exception as e:
    print(f"❌ Error loading FAISS index: {e}")
    INDEX = None

# 4. Load Metadata & Build BM25 Index (for Keyword Search)
try:
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        CHUNK_METADATA = json.load(f)
    
    # Prepare text for BM25
    print("Building BM25 Keyword Index...")
    corpus_tokens = [m['content'].lower().split() for m in CHUNK_METADATA]
    BM25_INDEX = BM25Okapi(corpus_tokens)
    print(f"✅ BM25 Index built with {len(corpus_tokens)} chunks.")
    
except Exception as e:
    print(f"❌ Error loading metadata/BM25: {e}")
    CHUNK_METADATA = []
    BM25_INDEX = None

print("--- Hybrid RAG Tool Initialized ---")

# --- The Python Function ---

def query_knowledge_base(query: str, k: int = 3) -> str:
    """
    Performs Hybrid Search (Vector + Keyword) with Re-Ranking.
    """
    if not INDEX or not EMBED_MODEL or not BM25_INDEX or not RERANKER:
        return "Error: RAG system not initialized properly."

    print(f"\n🔎 Hybrid RAG Query: {query[:50]}...")
    
    try:
        candidates = set() # Use a set to avoid duplicates
        
        # --- A. Vector Search (Semantic) ---
        query_embedding = EMBED_MODEL.encode([query])[0]
        query_vector = np.array([query_embedding]).astype("float32")
        
        # Get more candidates than we need (e.g., 10) to let the re-ranker filter them
        distances, indices = INDEX.search(query_vector, k=10)
        for idx in indices[0]:
            if idx >= 0 and idx < len(CHUNK_METADATA):
                candidates.add(idx)

        # --- B. Keyword Search (BM25) ---
        tokenized_query = query.lower().split()
        # Get top 10 keyword matches
        bm25_scores = BM25_INDEX.get_scores(tokenized_query)
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:10]
        for idx in top_bm25_indices:
            if idx >= 0 and idx < len(CHUNK_METADATA):
                candidates.add(idx)

        if not candidates:
            return "No relevant information found."

        # --- C. Re-Ranking (The Smart Part) ---
        candidate_indices = list(candidates)
        
        # Prepare pairs for Cross-Encoder: [[query, doc_text], [query, doc_text], ...]
        cross_inp = [[query, CHUNK_METADATA[idx]['content']] for idx in candidate_indices]
        
        # Score the pairs
        cross_scores = RERANKER.predict(cross_inp)
        
        # Sort by score (highest relevance first)
        # We zip indices with scores, sort by score descending
        scored_results = sorted(zip(candidate_indices, cross_scores), key=lambda x: x[1], reverse=True)
        
        # Select Top K (final answer)
        top_results = scored_results[:k]
        
        # --- D. Format Output ---
        final_output = []
        print(f"   Found {len(candidates)} candidates. Re-ranked top {k}.")
        
        for idx, score in top_results:
            metadata = CHUNK_METADATA[idx]
            final_output.append(
                f"[Source: {metadata['source']} | Score: {score:.4f}]\n"
                f"{metadata['content']}\n"
                f"-----------------"
            )
            
        return "\n".join(final_output)
        
    except Exception as e:
        print(f"Error during Hybrid RAG: {e}")
        import traceback
        traceback.print_exc()
        return f"Error searching knowledge base: {e}"