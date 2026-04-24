"""
Progress & Weak-Area Tracker.

Tracks:
  - Prelims MCQ accuracy by subject
  - Mains evaluation scores
  - Topics seen / topics missed
  - Time-on-task (session-based)

Uses persistent storage via Streamlit's session_state.
Export to JSON so the aspirant can keep a long-term record.
"""
import json
import streamlit as st
from datetime import datetime
from core.state import init_state
from core.ui import inject_css, hero
from core.rag_engine import get_engine

st.set_page_config(page_title="Progress · Sansad", page_icon="📊", layout="wide")
init_state()
inject_css()

hero(
    title="Progress",
    tagline="Where you stand. Where to push next.",
    subtitle="Track quiz accuracy by subject, surface the topics you keep missing, "
             "and export your record.",
    eyebrow="Spaced review · Weak-area mapping",
)

engine = get_engine()
stats = engine.stats()

# ── Corpus health ────────────────────────────────────────────────────────────
st.markdown("### 📚 Corpus Health")
cols = st.columns(4)
cols[0].metric("Documents", stats["docs"])
cols[1].metric("Total chunks", stats["chunks"])
cols[2].metric("NCERT chunks", stats["by_type"].get("ncert", 0))
cols[3].metric("PYQ chunks", stats["by_type"].get("pyq", 0))

if stats["sources"]:
    with st.expander(f"📎 All {len(stats['sources'])} indexed sources"):
        for s in stats["sources"]:
            st.caption(f"• {s}")

# ── Quiz history ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 📝 Quiz History")

quiz = st.session_state.get("current_quiz")
history = st.session_state.get("quiz_log", [])

if quiz and quiz.get("revealed"):
    # Save current quiz to log if all answered
    total = len(quiz["questions"])
    revealed = sum(1 for v in quiz["revealed"].values() if v)
    if revealed == total and not any(
        h.get("ts_id") == id(quiz) for h in history
    ):
        correct = 0
        if quiz["mode"] == "prelims":
            for i, q in enumerate(quiz["questions"]):
                if quiz["answers"].get(i) == q.get("correct"):
                    correct += 1
        history.append({
            "ts_id": id(quiz),
            "when": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": quiz["mode"],
            "subject": quiz["subject"],
            "topic": quiz.get("topic") or "—",
            "total": total,
            "correct": correct,
        })
        st.session_state.quiz_log = history

if not history:
    st.info("No attempts yet. Head to **PYQ Quiz** and take a round — your scores will land here.")
else:
    # Subject-wise aggregate
    subj_agg: dict = {}
    for h in history:
        s = h["subject"]
        a = subj_agg.setdefault(s, {"attempted": 0, "correct": 0})
        a["attempted"] += h["total"]
        a["correct"] += h["correct"]

    st.markdown("#### Accuracy by Subject")
    for subj, a in sorted(subj_agg.items(), key=lambda x: -x[1]["attempted"]):
        pct = (a["correct"] / a["attempted"] * 100) if a["attempted"] else 0
        bar_color = "#4a6b2a" if pct >= 70 else ("#b8860b" if pct >= 50 else "#8a2622")
        st.markdown(
            f"""<div style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;font-family:'Fraunces',serif;">
                <span><b>{subj}</b></span>
                <span>{a['correct']} / {a['attempted']} · {pct:.0f}%</span>
            </div>
            <div style="background:#e8ddc5;height:8px;border-radius:4px;overflow:hidden;">
                <div style="background:{bar_color};height:100%;width:{pct}%;"></div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # History table
    st.markdown("#### Session Log")
    for h in reversed(history[-20:]):
        pct = (h["correct"] / h["total"] * 100) if h["total"] else 0
        st.markdown(
            f"<div style='padding:10px 14px;margin-bottom:6px;background:#fffdf9;"
            f"border-left:3px solid {'#4a6b2a' if pct >= 70 else '#8a2622'};"
            f"border-radius:4px;'>"
            f"<b>{h['when']}</b> · {h['mode'].title()} · {h['subject']} "
            f"<i>{h['topic']}</i> · <b>{h['correct']}/{h['total']}</b></div>",
            unsafe_allow_html=True,
        )

    # Export
    c1, c2 = st.columns([1, 1])
    with c1:
        st.download_button(
            "⬇️ Export history (JSON)",
            data=json.dumps(history, indent=2),
            file_name="sansad_progress.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.quiz_log = []
            st.rerun()

# ── Corpus clear ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### ⚠️ Reset Corpus")
st.caption("Nuclear option — drops all indexed PDFs. You'll have to re-ingest.")
if st.button("Clear everything", type="secondary"):
    engine.clear()
    st.success("Corpus cleared.")
    st.rerun()
