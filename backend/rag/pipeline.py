"""
rag/pipeline.py
Retrieval-Augmented Generation (RAG) Pipeline

Workflow:
  Documents → Chunk → Embed → Store in FAISS → Retrieve on query → Inject into LLM
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


# ─── Configuration ────────────────────────────────────────────────────────────
EMBED_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
KNOWLEDGE_DIR = Path("knowledge_base")
INDEX_PATH    = Path("vectorstore/faiss.index")
META_PATH     = Path("vectorstore/metadata.pkl")
CHUNK_SIZE    = 400       # characters per chunk
CHUNK_OVERLAP = 80        # overlap between chunks


class DocumentChunker:
    """Splits documents into overlapping text chunks."""

    @staticmethod
    def chunk_text(text: str, source: str) -> List[Dict]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end].strip()
            if chunk:
                chunks.append({"text": chunk, "source": source, "start": start})
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    @staticmethod
    def load_pdf(path: Path) -> str:
        reader = PdfReader(str(path))
        return "\n".join(p.extract_text() or "" for p in reader.pages)

    @staticmethod
    def load_txt(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def ingest_directory(self, directory: Path) -> List[Dict]:
        all_chunks = []
        for file in directory.iterdir():
            if file.suffix.lower() == ".pdf":
                text = self.load_pdf(file)
            elif file.suffix.lower() in (".txt", ".md"):
                text = self.load_txt(file)
            else:
                continue
            chunks = self.chunk_text(text, source=file.name)
            all_chunks.extend(chunks)
            print(f"  ✓ {file.name}: {len(chunks)} chunks")
        return all_chunks


class EmbeddingEngine:
    """Generates vector embeddings using a sentence-transformer model."""

    def __init__(self, model_name: str = EMBED_MODEL):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dim   = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


class VectorStore:
    """FAISS-backed vector store with metadata."""

    def __init__(self, dim: int):
        self.index    = faiss.IndexFlatIP(dim)   # inner-product (cosine on normalized vecs)
        self.metadata: List[Dict] = []

    def add(self, embeddings: np.ndarray, metadata: List[Dict]):
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(metadata)

    def search(self, query_vec: np.ndarray, top_k: int = 4) -> List[Dict]:
        scores, indices = self.index.search(query_vec.astype(np.float32), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)
        return results

    def save(self):
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"Saved index: {self.index.ntotal} vectors → {INDEX_PATH}")

    @classmethod
    def load(cls, dim: int) -> "VectorStore":
        vs = cls(dim)
        vs.index    = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "rb") as f:
            vs.metadata = pickle.load(f)
        print(f"Loaded index: {vs.index.ntotal} vectors")
        return vs


class RAGPipeline:
    """
    High-level interface used by agents.
    Auto-builds the index if it doesn't exist; otherwise loads from disk.
    """

    def __init__(self):
        self.embedder = EmbeddingEngine()
        if INDEX_PATH.exists() and META_PATH.exists():
            self.store = VectorStore.load(self.embedder.dim)
        else:
            print("Index not found – building from knowledge_base/")
            self.store = self._build_index()

    def _build_index(self) -> VectorStore:
        chunker = DocumentChunker()
        chunks  = chunker.ingest_directory(KNOWLEDGE_DIR)

        if not chunks:
            raise RuntimeError("No documents found in knowledge_base/")

        texts = [c["text"] for c in chunks]
        vecs  = self.embedder.embed(texts)

        store = VectorStore(self.embedder.dim)
        store.add(vecs, chunks)
        store.save()
        return store

    async def retrieve(self, query: str, top_k: int = 4) -> List[Dict]:
        """Return the top-k most relevant chunks for the query."""
        vec    = self.embedder.embed([query])
        result = self.store.search(vec, top_k=top_k)
        return [{"text": r["text"], "source": r["source"], "score": r["score"]} for r in result]

    def rebuild(self):
        """Force a full re-ingestion (call after updating knowledge_base/)."""
        self.store = self._build_index()


# ─── CLI helper ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    pipeline = RAGPipeline()
    query    = "What is the refund policy?"
    results  = asyncio.run(pipeline.retrieve(query))
    print(f"\nQuery: {query}\n")
    for r in results:
        print(f"[{r['score']:.3f}] {r['source']}")
        print(r["text"][:200])
        print()
