"""
PYQ Quiz — generate UPSC-style questions from the user's own PYQ corpus.

Logic:
  - Pull chunks tagged 'pyq' for pattern, 'subject'/'ncert'/'official' for content
  - Ask the LLM to craft a fresh question in the style of the PYQs retrieved
  - Prelims → MCQ (4 options, one correct, explanation)
  - Mains → descriptive (250 words) with marking scheme
  - Interview → open-ended probing question + expected angles
"""
import json
import re
import streamlit as st
from core.state import init_state, current_mode_config, UPSC_MODES
from core.ui import inject_css, hero
from core.rag_engine import get_engine
from core.llm import call_llm
from core.voice import play_audio

st.set_page_config(page_title="PYQ Quiz · Sansad", page_icon="📝", layout="wide")
init_state()
inject_css()

hero(
    title="PYQ Quiz",
    tagline="Fresh questions. Your PYQs' DNA.",
    subtitle="The generator studies your uploaded Previous Year Papers, picks up UPSC's phrasing "
             "and difficulty fingerprint, and crafts new questions from your subject material.",
    eyebrow="Pattern-matched question generator",
)

engine = get_engine()
mode = st.session_state.get("upsc_mode", "prelims")
config = current_mode_config()

# ── Topic/subject picker ─────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    subject = st.selectbox(
        "Subject",
        ["Polity", "History", "Geography", "Economy", "Environment",
         "Science & Tech", "International Relations", "Ethics", "Culture", "Current Affairs"],
    )
with col2:
    topic = st.text_input(
        "Specific topic (optional)",
        placeholder="e.g. Fundamental Rights, Indus Valley, Monsoon, GST…",
    )
with col3:
    num_q = st.number_input("Questions", 1, 10, 3)

stats = engine.stats()
pyq_count = stats["by_type"].get("pyq", 0)
content_count = stats["by_type"].get("subject", 0) + stats["by_type"].get("ncert", 0) + stats["by_type"].get("official", 0)

cc1, cc2, cc3 = st.columns(3)
cc1.metric("PYQ chunks", pyq_count)
cc2.metric("Content chunks", content_count)
cc3.metric("Active mode", UPSC_MODES[mode]["label"])

if pyq_count == 0:
    st.warning("No PYQs uploaded yet. For best results, add PYQ PDFs on the Home page "
               "(tagged as 'Previous Year Papers'). You can still generate questions "
               "from subject material alone.")

# ── Generate button ──────────────────────────────────────────────────────────
if st.button("🎯 Generate Questions", type="primary", use_container_width=True):
    if content_count == 0:
        st.error("No subject material indexed. Upload some PDFs first.")
        st.stop()

    with st.spinner("Studying your PYQ style and crafting questions…"):
        # Retrieve PYQ style exemplars
        pyq_query = f"{topic or subject} previous year question"
        pyq_samples = [c for c in engine.search(pyq_query, k=4, doc_type="pyq")]

        # Retrieve content
        content_query = topic or subject
        content_chunks = engine.search(content_query, k=6, subject=subject)

        pyq_text = "\n\n".join([f"PYQ SAMPLE: {c.text[:500]}" for c in pyq_samples]) or "(No PYQ samples available — use standard UPSC style.)"
        content_text = "\n\n".join([f"[{c.source}, p.{c.page}] {c.text}" for c in content_chunks])

        # Build prompt based on mode
        if mode == "prelims":
            fmt_instr = f"""Generate {num_q} UPSC Prelims-style MCQ(s). For each, return strict JSON:
{{
  "questions": [
    {{
      "question": "The question stem (can be 'Consider the following statements…' type)",
      "options": ["(a) Option A", "(b) Option B", "(c) Option C", "(d) Option D"],
      "correct": 0,
      "explanation": "Why the correct option is right and why others fail. Cite source.",
      "source_note": "Brief attribution to source material"
    }}
  ]
}}"""
        elif mode == "mains":
            fmt_instr = f"""Generate {num_q} UPSC Mains-style descriptive question(s). Return strict JSON:
{{
  "questions": [
    {{
      "question": "The question (clear directive verb: 'Discuss', 'Critically examine', 'Analyse')",
      "marks": 15,
      "word_limit": 250,
      "model_answer_outline": "Intro → 3-4 body points with examples → Way forward",
      "marking_scheme": "What gets full marks vs average",
      "source_note": "Brief attribution"
    }}
  ]
}}"""
        else:  # interview
            fmt_instr = f"""Generate {num_q} UPSC Interview-style probing question(s). Return strict JSON:
{{
  "questions": [
    {{
      "question": "A thought-provoking question that tests opinion + reasoning",
      "why_asked": "What the board is checking",
      "expected_angles": ["Angle 1", "Angle 2", "Angle 3"],
      "likely_followup": "The probe they'd fire next",
      "source_note": "Attribution"
    }}
  ]
}}"""

        system = f"""You are a UPSC question-setter who has studied decades of papers.
Mode: {config['label']}. Subject: {subject}. Topic: {topic or 'broad'}.

PYQ STYLE EXEMPLARS:
{pyq_text}

SOURCE CONTENT TO BASE QUESTIONS ON:
{content_text}

Create questions that feel authentically UPSC — right difficulty, right phrasing, right trick-factor.
Output ONLY valid JSON matching the schema below. No prose outside JSON."""

        user = fmt_instr

        raw = call_llm([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ], temperature=0.5, max_tokens=2500, stream=False)

        # Robust JSON extract (LLMs sometimes wrap in ```json)
        try:
            json_str = raw
            m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if m:
                json_str = m.group(1)
            else:
                # Find first { to last }
                start = raw.find("{")
                end = raw.rfind("}")
                if start != -1 and end != -1:
                    json_str = raw[start:end + 1]
            parsed = json.loads(json_str)
            st.session_state.current_quiz = {
                "mode": mode, "subject": subject, "topic": topic,
                "questions": parsed.get("questions", []),
                "answers": {},
                "revealed": {},
            }
        except Exception as e:
            st.error(f"Couldn't parse questions. Raw output:\n\n{raw[:2000]}")
            st.stop()

    st.rerun()

# ── Render current quiz ──────────────────────────────────────────────────────
quiz = st.session_state.get("current_quiz")
if quiz:
    st.divider()
    st.markdown(f"### 📝 Questions · {quiz['subject']} · {UPSC_MODES[quiz['mode']]['label']}")

    for i, q in enumerate(quiz["questions"]):
        with st.container(border=True):
            st.markdown(f"**Q{i+1}.** {q['question']}")

            if quiz["mode"] == "prelims":
                # MCQ
                options = q.get("options", [])
                correct_idx = q.get("correct", 0)
                selected = st.radio(
                    "Pick an answer",
                    list(range(len(options))),
                    format_func=lambda j: options[j],
                    key=f"q{i}_radio",
                    index=None,
                )
                c1, c2 = st.columns([1, 1])
                if c1.button("Check", key=f"check_{i}"):
                    quiz["answers"][i] = selected
                    quiz["revealed"][i] = True
                    st.rerun()
                if c2.button("🔊 Read aloud", key=f"tts_{i}"):
                    play_audio(q["question"] + " " + " ".join(options), autoplay=True)

                if quiz["revealed"].get(i):
                    ans = quiz["answers"][i]
                    if ans == correct_idx:
                        st.success(f"✓ Correct! **{options[correct_idx]}**")
                    else:
                        ans_label = options[ans] if ans is not None else "(no answer)"
                        st.error(f"✗ You chose {ans_label}. Correct: **{options[correct_idx]}**")
                    st.info(f"**Explanation:** {q.get('explanation', '—')}")
                    if q.get("source_note"):
                        st.caption(f"📎 {q['source_note']}")

            elif quiz["mode"] == "mains":
                st.caption(f"**{q.get('marks', 15)} marks · ~{q.get('word_limit', 250)} words**")
                answer = st.text_area(
                    "Your answer",
                    height=220,
                    key=f"q{i}_text",
                    placeholder="Write your answer here. Structure: Intro → Body → Way forward.",
                )
                c1, c2, c3 = st.columns([1, 1, 1])
                if c1.button("Evaluate", key=f"eval_{i}"):
                    if answer.strip():
                        with st.spinner("Evaluating…"):
                            eval_prompt = f"""You are a UPSC Mains evaluator. Grade this answer strictly.

QUESTION: {q['question']}
MARKING SCHEME: {q.get('marking_scheme', 'standard')}
MODEL OUTLINE: {q.get('model_answer_outline', '')}

STUDENT ANSWER:
{answer}

Give:
1. Score out of {q.get('marks', 15)}
2. What worked (2-3 points)
3. What was missed (2-3 points)
4. Concrete rewrite of intro + conclusion
Be blunt but constructive."""
                            feedback = call_llm([
                                {"role": "system", "content": "You are a senior UPSC evaluator. Be precise and fair."},
                                {"role": "user", "content": eval_prompt},
                            ], temperature=0.2, max_tokens=1200, stream=False)
                            st.markdown("#### 📋 Evaluation")
                            st.markdown(feedback)
                    else:
                        st.warning("Write an answer first.")
                if c2.button("Show model outline", key=f"model_{i}"):
                    st.info(f"**Outline:** {q.get('model_answer_outline', '—')}")
                if c3.button("🔊 Read aloud", key=f"tts_{i}"):
                    play_audio(q["question"], autoplay=True)

            else:  # interview
                st.caption(f"*{q.get('why_asked', '')}*")
                answer = st.text_area("Your response", height=120, key=f"q{i}_text",
                                      placeholder="Answer conversationally…")
                c1, c2, c3 = st.columns([1, 1, 1])
                if c1.button("Reveal angles", key=f"reveal_{i}"):
                    st.markdown("**Expected angles:**")
                    for a in q.get("expected_angles", []):
                        st.markdown(f"- {a}")
                    if q.get("likely_followup"):
                        st.info(f"**Probable follow-up:** {q['likely_followup']}")
                if c2.button("Evaluate", key=f"eval_{i}"):
                    if answer.strip():
                        with st.spinner("Evaluating…"):
                            feedback = call_llm([
                                {"role": "system", "content": "You are a UPSC interview board member. Give concise feedback on clarity, balance, depth."},
                                {"role": "user", "content": f"Q: {q['question']}\n\nCandidate: {answer}\n\nCritique (3 bullets)."},
                            ], temperature=0.3, max_tokens=500, stream=False)
                            st.markdown(feedback)
                    else:
                        st.warning("Respond first.")
                if c3.button("🔊 Read aloud", key=f"tts_{i}"):
                    play_audio(q["question"], autoplay=True)

    st.divider()
    if st.button("🗑️ Clear and start over", use_container_width=True):
        st.session_state.current_quiz = None
        st.rerun()
