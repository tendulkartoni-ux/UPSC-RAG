"""
Study Chat — the RAG-grounded Q&A page.

Flow:
  1. Retrieve top-k chunks from the user's corpus (subject, PYQ, NCERT, official)
  2. Assemble a mode-specific prompt (Prelims / Mains / Interview)
  3. Stream the LLM response
  4. Optionally read it aloud (gTTS)
  5. Voice input via browser Web Speech API
"""
import streamlit as st
from core.state import init_state, current_mode_config, UPSC_MODES
from core.ui import inject_css, hero
from core.rag_engine import get_engine
from core.llm import call_llm
from core.voice import play_audio, voice_input_component

st.set_page_config(page_title="Study Chat · Sansad", page_icon="📚", layout="wide")
init_state()
inject_css()

hero(
    title="Study Chat",
    tagline="Ask. Be answered with citations.",
    subtitle="Every answer is grounded in your uploaded PDFs, NCERTs and official sources. "
             "Mode-aware — the same question gets a different treatment for Prelims vs Mains vs Interview.",
    eyebrow="Retrieval-Augmented Q&A",
)

engine = get_engine()

# ── Top bar: mode + subject filter + voice ───────────────────────────────────
colA, colB, colC = st.columns([2, 2, 1])
with colA:
    mode = st.session_state.get("upsc_mode", "prelims")
    new_mode = st.selectbox(
        "Mode",
        ["prelims", "mains", "interview"],
        index=["prelims", "mains", "interview"].index(mode),
        format_func=lambda m: UPSC_MODES[m]["label"],
    )
    st.session_state.upsc_mode = new_mode

with colB:
    subject_filter = st.selectbox(
        "Limit to subject",
        ["Any", "Polity", "History", "Geography", "Economy", "Environment",
         "Science & Tech", "International Relations", "Ethics", "Current Affairs", "Culture"],
    )

with colC:
    use_voice = st.toggle("🎙️ Voice mode", value=st.session_state.get("voice_enabled", True))

if engine.stats()["chunks"] == 0:
    st.warning("No PDFs ingested yet. Upload some on the **Home** page, "
               "or fetch NCERTs from **NCERT Library**.")

# ── Voice input (optional) ───────────────────────────────────────────────────
voice_text = None
if use_voice:
    with st.expander("🎤 Speak your question", expanded=False):
        voice_text = voice_input_component(key="chat_voice")
        if voice_text:
            st.info(f"Heard: *{voice_text}*")

# ── Chat history render ──────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "🙋"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            with st.expander(f"📎 {len(msg['citations'])} source(s)", expanded=False):
                for i, c in enumerate(msg["citations"], 1):
                    st.markdown(
                        f"**[{i}]** `{c['source']}` · page {c['page']} · "
                        f"*{c['subject']}* · relevance {c['score']:.2f}"
                    )
                    st.caption(c["preview"])
        if msg["role"] == "assistant" and use_voice:
            play_audio(msg["content"], autoplay=st.session_state.get("tts_autoplay", False))

# ── Input box ────────────────────────────────────────────────────────────────
user_q = st.chat_input("Ask anything — e.g. 'What is basic structure doctrine?'")
if voice_text and not user_q:
    user_q = voice_text

if user_q:
    # Show user turn
    st.session_state.chat_history.append({"role": "user", "content": user_q})
    with st.chat_message("user", avatar="🙋"):
        st.markdown(user_q)

    # Retrieve
    subj = None if subject_filter == "Any" else subject_filter
    chunks = engine.search(user_q, k=6, subject=subj)

    # Build prompt
    config = current_mode_config()
    if chunks:
        context = "\n\n".join([
            f"[Source {i+1}: {c.source}, p.{c.page}, subject={c.subject}]\n{c.text}"
            for i, c in enumerate(chunks)
        ])
    else:
        context = "(No indexed material. Answer from general knowledge but flag this clearly.)"

    system_prompt = f"""You are Sansad, an expert UPSC Civil Services preparation tutor.
The aspirant is in **{config['label']} mode**.

ANSWER STYLE:
{config['answer_style']}

RULES:
1. Base your answer on the provided SOURCES when available. Cite like [1], [2].
2. If sources don't cover the question, say so and answer from general knowledge with a note.
3. Never hallucinate constitutional articles, case names, dates, or statistics.
4. Use Indian context and examples. Be precise about Articles, Schedules, committees, judgments.
5. For Prelims: highlight factual nuggets. For Mains: structure with sub-points. For Interview: be conversational.

SOURCES:
{context}"""

    messages = [{"role": "system", "content": system_prompt}]
    # Last few turns for context
    for m in st.session_state.chat_history[-6:-1]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_q})

    # Stream the response
    with st.chat_message("assistant", avatar="🎓"):
        placeholder = st.empty()
        full_text = ""
        stream = call_llm(messages, temperature=0.3, max_tokens=1500, stream=True)
        if isinstance(stream, str):
            # Error — not a generator
            full_text = stream
            placeholder.markdown(full_text)
        else:
            for delta in stream:
                full_text += delta
                placeholder.markdown(full_text + " ▌")
            placeholder.markdown(full_text)

        # Citations panel
        citations = [{
            "source": c.source, "page": c.page, "subject": c.subject,
            "score": c.score, "preview": c.text[:220] + "…",
        } for c in chunks]
        if citations:
            with st.expander(f"📎 {len(citations)} source(s)", expanded=False):
                for i, c in enumerate(citations, 1):
                    st.markdown(
                        f"**[{i}]** `{c['source']}` · page {c['page']} · "
                        f"*{c['subject']}* · relevance {c['score']:.2f}"
                    )
                    st.caption(c["preview"])

        # Voice output
        if use_voice:
            play_audio(full_text, autoplay=st.session_state.get("tts_autoplay", False))

    st.session_state.chat_history.append({
        "role": "assistant", "content": full_text, "citations": citations,
    })

# ── Sidebar tools ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧹 Chat controls")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    st.caption(f"{len(st.session_state.chat_history)} messages in memory")
