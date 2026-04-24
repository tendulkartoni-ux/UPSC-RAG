"""
Sansad — UPSC RAG Study Companion
Main entry point. Handles mode selection (Prelims/Mains/Interview), API key setup,
and routes the user to study chat, PYQ quizzes, NCERT library, or progress tracker.
"""
import streamlit as st
from core.state import init_state, set_mode, UPSC_MODES
from core.ui import inject_css, hero, mode_card, stat_pill
from core.rag_engine import get_engine

st.set_page_config(
    page_title="Sansad · UPSC RAG",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()
inject_css()

# ── Sidebar: API key + provider + global status ──────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    provider = st.selectbox(
        "LLM Provider",
        ["Groq (free tier)", "Anthropic Claude", "OpenAI"],
        index=["Groq (free tier)", "Anthropic Claude", "OpenAI"].index(
            st.session_state.get("llm_provider", "Groq (free tier)")
        ),
        help="Groq offers a free tier — get a key at console.groq.com",
    )
    st.session_state.llm_provider = provider

    key_label = {
        "Groq (free tier)": "Groq API Key",
        "Anthropic Claude": "Anthropic API Key",
        "OpenAI": "OpenAI API Key",
    }[provider]

    api_key = st.text_input(
        key_label,
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="Paste key here",
    )
    st.session_state.api_key = api_key

    model_opts = {
        "Groq (free tier)": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "Anthropic Claude": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
        "OpenAI": ["gpt-4o-mini", "gpt-4o"],
    }[provider]
    st.session_state.llm_model = st.selectbox("Model", model_opts)

    st.divider()

    # Corpus stats
    engine = get_engine()
    stats = engine.stats()
    st.markdown("### 📚 Your Corpus")
    c1, c2 = st.columns(2)
    c1.metric("Documents", stats["docs"])
    c2.metric("Chunks", stats["chunks"])
    if stats["sources"]:
        with st.expander("Loaded sources", expanded=False):
            for src in stats["sources"]:
                st.caption(f"• {src}")

    st.divider()
    st.markdown("### 🎙️ Voice")
    st.session_state.voice_enabled = st.toggle(
        "Enable voice I/O", value=st.session_state.get("voice_enabled", True)
    )
    st.session_state.tts_autoplay = st.toggle(
        "Auto-play answers", value=st.session_state.get("tts_autoplay", False)
    )

    st.divider()
    st.caption(
        "Built for UPSC aspirants. NCERTs via ncert.nic.in · "
        "PIB, Laxmikanth-style constitutional coverage via your PDFs."
    )

# ── Main Hero ────────────────────────────────────────────────────────────────
hero(
    title="Sansad",
    tagline="Your Grounded UPSC Study Companion",
    subtitle="RAG over your PDFs · NCERT library · PYQ-style quizzing · Voice chat",
)

# ── Mode Selection ───────────────────────────────────────────────────────────
st.markdown("### Choose your stage")
st.caption("The assistant's depth, citations style, and quiz format adapt to your choice.")

cols = st.columns(3)
modes = [
    ("prelims", "🎯", "Prelims", "Factual MCQ recall, static GS, current affairs, map-based", "objective · factual · breadth"),
    ("mains", "✍️", "Mains", "Analytical essays, structured answers, case-studies, GS I–IV", "analytical · 250-word answers · depth"),
    ("interview", "🎙️", "Interview", "Opinion calibration, DAF probing, current affairs depth", "conversational · persona · ethics"),
]
for col, (key, icon, title, desc, meta) in zip(cols, modes):
    with col:
        is_active = st.session_state.get("upsc_mode") == key
        if mode_card(icon, title, desc, meta, active=is_active, key=f"mode_{key}"):
            set_mode(key)
            st.rerun()

current = st.session_state.get("upsc_mode", "prelims")
st.info(f"**Active mode:** {UPSC_MODES[current]['label']} — {UPSC_MODES[current]['hint']}")

# ── Quick Actions ────────────────────────────────────────────────────────────
st.markdown("### Where would you like to go?")
qa = st.columns(4)
with qa[0]:
    st.page_link("pages/1_Study_Chat.py", label="**Study Chat**", icon="📚")
    st.caption("Ask anything. Grounded in your PDFs + NCERTs.")
with qa[1]:
    st.page_link("pages/2_PYQ_Quiz.py", label="**PYQ Quiz**", icon="📝")
    st.caption("Auto-generated questions from your PYQs.")
with qa[2]:
    st.page_link("pages/3_NCERT_Library.py", label="**NCERT Library**", icon="📥")
    st.caption("Fetch official NCERTs by class/subject.")
with qa[3]:
    st.page_link("pages/4_Progress.py", label="**Progress**", icon="📊")
    st.caption("Track weak areas and quiz history.")

st.divider()

# ── Upload Zone ──────────────────────────────────────────────────────────────
st.markdown("### 📎 Add your PDFs")
st.caption(
    "Upload subject notes (Polity, History, Geo, Economy, Env, S&T, IR) and PYQ papers. "
    "Everything is processed locally in the app — no files leave this session."
)
up = st.file_uploader(
    "Drop PDFs here",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader_home",
)

col1, col2 = st.columns([1, 1])
with col1:
    doc_type = st.radio(
        "Tag these as:",
        ["📘 Subject Material", "📝 Previous Year Papers (PYQ)", "📰 Current Affairs"],
        horizontal=True,
    )
with col2:
    subject = st.selectbox(
        "Subject (optional)",
        ["General", "Polity", "History", "Geography", "Economy", "Environment",
         "Science & Tech", "International Relations", "Ethics", "Essay", "CSAT"],
    )

if up and st.button("Ingest into RAG index", type="primary", use_container_width=True):
    tag = {"📘 Subject Material": "subject", "📝 Previous Year Papers (PYQ)": "pyq",
           "📰 Current Affairs": "current"}[doc_type]
    progress = st.progress(0.0, text="Starting ingestion…")
    for i, f in enumerate(up):
        progress.progress((i) / len(up), text=f"Processing {f.name}…")
        engine.ingest_pdf_bytes(f.read(), name=f.name, doc_type=tag, subject=subject)
    progress.progress(1.0, text="Indexed ✓")
    st.success(f"Added {len(up)} PDF(s) · corpus now has {engine.stats()['chunks']} chunks.")
    st.rerun()

# ── Footer credits ───────────────────────────────────────────────────────────
st.markdown(
    """<div class='sansad-foot'>
    <span>Sansad · Built for the long grind</span>
    <span>Pvt info never leaves the browser session · BYO API key</span>
    </div>""",
    unsafe_allow_html=True,
)
