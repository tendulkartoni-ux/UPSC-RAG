# 🕊️ Sansad — UPSC RAG Study Companion

A real, grounded RAG (Retrieval-Augmented Generation) study app for UPSC Civil Services preparation. Built for aspirants, not for a demo reel.

**Live features:**
- 📚 **Real RAG** over your uploaded PDFs (subjects + PYQs) — FAISS-free, uses `sentence-transformers` + NumPy, so it deploys clean on free tiers.
- 🎯 **Mode-aware answers** — the same question gets a different treatment for Prelims (factual) vs Mains (analytical, 250-word) vs Interview (conversational).
- 📝 **PYQ-style quiz generator** — studies your uploaded PYQs to pick up UPSC's phrasing, then crafts new questions from your subject material.
- 📥 **One-click resource library** — fetches NCERTs (Class 6–12, all UPSC-relevant subjects) from `ncert.nic.in`, plus the Constitution, Economic Survey, Budget, 2nd ARC, NITI reports, PIB, and more. All from official `.gov.in` / `.nic.in` sources.
- 🎙️ **Voice in, voice out** — speak questions via the browser's Web Speech API (no server STT needed), get answers read aloud via gTTS.
- 📊 **Progress tracker** — subject-wise accuracy, weak-area mapping, exportable history.

## Deploy in 5 minutes

### Option A — Streamlit Cloud (recommended, free)
1. Push this folder to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, set entry point to `app.py`.
3. Deploy. First boot takes ~2 min (downloads the 80MB embedding model).
4. Open the app. Paste your Groq API key in the sidebar (get one free at [console.groq.com](https://console.groq.com)).

### Option B — Hugging Face Spaces (also free)
1. Create a new Space → SDK: **Streamlit**.
2. Upload this folder's contents (or link the repo).
3. Done. Same Groq key goes in the sidebar.

### Option C — Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## API key — why & how

The embedding model (for RAG retrieval) runs **locally in the app**, free. But generating answers needs an LLM.

| Provider | Cost | Speed | Get a key |
|---|---|---|---|
| **Groq** (default) | Free tier is generous | Fastest | [console.groq.com](https://console.groq.com) |
| Anthropic Claude | Paid, best quality | Fast | [console.anthropic.com](https://console.anthropic.com) |
| OpenAI | Paid | Fast | [platform.openai.com](https://platform.openai.com) |

Pick in the sidebar, paste the key, go.

## What to upload

The app shines when you feed it:
1. **Your PYQ PDFs** — tag them as "Previous Year Papers" so the quiz generator learns UPSC's style.
2. **Subject PDFs** — Laxmikanth notes, Bipan Chandra, G.C. Leong, Sriram IAS, your class handouts — whatever you're already studying.
3. **Current affairs compilations** — tag as "Current Affairs".

Everything is processed **in-session, in-memory**. No files leave your browser. No server-side storage.

## The library (one-click fetch)

From the **Library** page you can grab:

**NCERTs** — Class 6–12, all UPSC-relevant subjects: History, Geography, Polity, Economy, Sociology, Fine Art. Fetched chapter-wise from `ncert.nic.in`.

**Official gov resources:**
- The Constitution of India (full text, `legislative.gov.in`)
- Economic Survey & Union Budget (latest, `indiabudget.gov.in`)
- NITI Aayog's Strategy for New India (`niti.gov.in`)
- 2nd ARC — all 15 reports (`darpg.gov.in`)
- MEA Annual Report
- State of Forest Report (FSI)
- PRS India bill summaries
- PIB press releases
- UPSC's own archive — PYQs + syllabus

**Curated bundles** — one click fetches themed sets (e.g. "Polity Core", "Economy Essentials", "Foundation Starter Pack").

## Voice I/O

- **Input:** Browser Web Speech API. Works in Chrome / Edge / Safari. Firefox doesn't support it yet.
- **Output:** gTTS generates MP3 bytes in-session, plays inline. Falls back to browser speech synthesis if gTTS fails.
- Language is set to `en-IN` for Indian English — pronunciation of place names, committee names, schemes is noticeably better.

## Architecture (one paragraph)

`app.py` is the entry. Four pages under `pages/` handle Study Chat, PYQ Quiz, Library, and Progress. `core/rag_engine.py` does chunking + embedding + cosine retrieval — no vector DB, just NumPy (scales to ~100K chunks fine). `core/llm.py` is a provider-agnostic router. `core/voice.py` wires the Web Speech API component + gTTS. `core/catalog.py` hard-codes the NCERT + official-resource catalog. `core/downloader.py` fetches PDFs with retries. `core/ui.py` injects the warm ivory/maroon editorial aesthetic.

## Troubleshooting

| Issue | Fix |
|---|---|
| NCERT chapter download fails | NCERT sometimes restructures paths. The app surfaces failures clearly — just visit `ncert.nic.in` directly and upload from Home. |
| Voice input doesn't work | Must be HTTPS (Streamlit Cloud / HF Spaces are HTTPS by default). Must be Chrome/Edge/Safari. |
| "No API key set" | Paste one in the sidebar under ⚙️ Configuration. |
| Embedding model takes forever | First load only (~30s on cold start). Cached after that for the session. |

## Why this architecture

- **No FAISS** — avoids the deploy headaches on free tiers (FAISS wheels can be finicky on ARM / HF Spaces). NumPy cosine sim scales fine for a UPSC corpus.
- **No vector DB** — session-scoped in-memory. Re-ingest on restart, which is fast.
- **No server-side STT** — browser Web Speech API means zero infrastructure. Works on free tier.
- **Multi-provider LLM** — you're not locked in. Groq for free speed, Anthropic for quality, OpenAI if you prefer.

Good luck with the prep. `राष्ट्र सेवा` 🇮🇳
