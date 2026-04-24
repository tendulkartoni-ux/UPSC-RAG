"""
RAG Engine — the core retrieval system.

Uses:
  - pypdf for PDF text extraction
  - sentence-transformers (all-MiniLM-L6-v2, 80MB, CPU-friendly) for embeddings
  - NumPy cosine similarity (no FAISS needed — keeps deploy light)
  - Overlapping chunking tuned for UPSC textbook content

Persistence: session-scoped. Streamlit Cloud's ephemeral FS means we don't
fight disk quotas. Re-ingestion on restart is fast (MiniLM on CPU).
"""
from __future__ import annotations
import hashlib
import io
import re
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np
import streamlit as st


# ── Lazy singleton (model loads once per session) ────────────────────────────
@st.cache_resource(show_spinner="Loading embedding model (first time ~30s)…")
def _load_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@dataclass
class Chunk:
    text: str
    source: str           # filename or NCERT id
    doc_type: str         # 'subject' | 'pyq' | 'current' | 'ncert' | 'official'
    subject: str          # 'Polity', 'History', …
    page: int
    chunk_id: str
    score: float = 0.0


class RAGEngine:
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.sources_seen: set = set()

    # ── Ingestion ────────────────────────────────────────────────────────────
    def ingest_pdf_bytes(self, data: bytes, name: str, doc_type: str = "subject",
                         subject: str = "General") -> int:
        """Extract → chunk → embed → append. Returns chunk count."""
        if name in self.sources_seen:
            return 0  # dedup

        from pypdf import PdfReader
        try:
            reader = PdfReader(io.BytesIO(data))
        except Exception as e:
            st.error(f"Could not read {name}: {e}")
            return 0

        new_chunks: List[Chunk] = []
        for p_idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            text = _clean(text)
            if len(text) < 100:
                continue
            for chunk_text in _chunk_text(text, target=800, overlap=120):
                cid = hashlib.md5(f"{name}:{p_idx}:{chunk_text[:60]}".encode()).hexdigest()[:12]
                new_chunks.append(Chunk(
                    text=chunk_text, source=name, doc_type=doc_type,
                    subject=subject, page=p_idx + 1, chunk_id=cid,
                ))

        if not new_chunks:
            return 0

        embedder = _load_embedder()
        vecs = embedder.encode(
            [c.text for c in new_chunks],
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        ).astype("float32")

        self.chunks.extend(new_chunks)
        if self.embeddings is None:
            self.embeddings = vecs
        else:
            self.embeddings = np.vstack([self.embeddings, vecs])
        self.sources_seen.add(name)
        return len(new_chunks)

    # ── Retrieval ────────────────────────────────────────────────────────────
    def search(self, query: str, k: int = 6,
               doc_type: Optional[str] = None,
               subject: Optional[str] = None) -> List[Chunk]:
        if not self.chunks or self.embeddings is None:
            return []

        embedder = _load_embedder()
        q_vec = embedder.encode([query], normalize_embeddings=True).astype("float32")[0]
        sims = self.embeddings @ q_vec

        mask = np.ones(len(self.chunks), dtype=bool)
        if doc_type:
            mask &= np.array([c.doc_type == doc_type for c in self.chunks])
        if subject and subject != "General":
            mask &= np.array([
                c.subject == subject or c.subject == "General"
                for c in self.chunks
            ])

        scores = np.where(mask, sims, -np.inf)
        top_idx = np.argsort(scores)[::-1][:k]
        results = []
        for i in top_idx:
            if scores[i] == -np.inf:
                continue
            c = self.chunks[int(i)]
            c.score = float(scores[i])
            results.append(c)
        return results

    def stats(self) -> Dict:
        by_type: Dict[str, int] = {}
        for c in self.chunks:
            by_type[c.doc_type] = by_type.get(c.doc_type, 0) + 1
        return {
            "chunks": len(self.chunks),
            "docs": len(self.sources_seen),
            "sources": sorted(self.sources_seen),
            "by_type": by_type,
        }

    def clear(self):
        self.chunks.clear()
        self.embeddings = None
        self.sources_seen.clear()


# ── Helpers ──────────────────────────────────────────────────────────────────
def _clean(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _chunk_text(text: str, target: int = 800, overlap: int = 120) -> List[str]:
    """Chunk by sentences, accumulate until ~target chars, keep overlap tail."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current, current_len = [], [], 0
    for s in sentences:
        if current_len + len(s) > target and current:
            chunks.append(" ".join(current))
            # overlap: take last few sentences summing to ~overlap chars
            tail, tail_len = [], 0
            for prev in reversed(current):
                if tail_len + len(prev) > overlap:
                    break
                tail.insert(0, prev)
                tail_len += len(prev)
            current = tail + [s]
            current_len = sum(len(x) for x in current)
        else:
            current.append(s)
            current_len += len(s)
    if current:
        chunks.append(" ".join(current))
    return [c for c in chunks if len(c) > 80]


# ── Session-scoped singleton ─────────────────────────────────────────────────
def get_engine() -> RAGEngine:
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
    return st.session_state.rag_engine
