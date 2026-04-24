"""Session state & UPSC mode configuration."""
import streamlit as st

UPSC_MODES = {
    "prelims": {
        "label": "Prelims",
        "hint": "Factual, objective, MCQ-ready. Emphasis on dates, names, constitutional articles, map facts.",
        "answer_style": (
            "Answer in a precise, exam-factual tone. Use bullet points for facts. "
            "Highlight numbers, dates, articles (e.g., 'Art. 21'), and committee names in **bold**. "
            "End with a one-line 'Likely Prelims angle:' note on what UPSC typically asks from this topic."
        ),
        "quiz_style": "mcq",
    },
    "mains": {
        "label": "Mains",
        "hint": "Analytical, structured, 150–250 word answers with intro-body-conclusion.",
        "answer_style": (
            "Structure answers as: (1) Intro — define the issue in 1–2 lines. "
            "(2) Body — use sub-headings, list multiple dimensions (historical, constitutional, socio-economic, "
            "global). Cite committees, judgments, Art. numbers where relevant. "
            "(3) Way forward — forward-looking, balanced conclusion. "
            "Target ~250 words. Avoid one-sided views."
        ),
        "quiz_style": "descriptive",
    },
    "interview": {
        "label": "Interview",
        "hint": "Conversational, opinionated but balanced, ethical reasoning, DAF-style probing.",
        "answer_style": (
            "Respond conversationally, as if in a UPSC interview. Give a balanced opinion with "
            "reasoning. Acknowledge multiple viewpoints. If the question touches ethics, apply "
            "frameworks (utilitarian vs deontological, public-service values). Keep it concise — "
            "3–5 sentences usually. Offer a thoughtful follow-up question the interviewer might ask."
        ),
        "quiz_style": "interview",
    },
}


def init_state():
    defaults = {
        "upsc_mode": "prelims",
        "llm_provider": "Groq (free tier)",
        "llm_model": "llama-3.3-70b-versatile",
        "api_key": "",
        "voice_enabled": True,
        "tts_autoplay": False,
        "chat_history": [],
        "quiz_history": [],
        "current_quiz": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def set_mode(mode: str):
    if mode in UPSC_MODES:
        st.session_state.upsc_mode = mode


def current_mode_config():
    return UPSC_MODES[st.session_state.get("upsc_mode", "prelims")]
