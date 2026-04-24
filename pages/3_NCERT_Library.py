"""
Resource Library.

Two tabs:
  1. NCERTs — Class 6–12, UPSC-relevant subjects. Chapter-wise fetch from ncert.nic.in.
  2. Official Resources — Constitution, Budget, Economic Survey, 2nd ARC, NITI reports,
     PRS bill summaries, PIB, UPSC PYQs, etc. All from .gov.in / .nic.in.
  3. Bundles — one-click curated sets.

Only legit public sources. Respectful rate-limiting (20s timeout, 2 retries).
Auto-ingestion into RAG so downloads become searchable immediately.
"""
import streamlit as st
from core.state import init_state
from core.ui import inject_css, hero, resource_card
from core.catalog import (
    NCERTS, ncert_chapter_urls,
    OFFICIAL_RESOURCES, group_official_by_category,
)
from core.downloader import fetch_pdf, fetch_many
from core.rag_engine import get_engine

st.set_page_config(page_title="Library · Sansad", page_icon="📥", layout="wide")
init_state()
inject_css()


# ══════════════════════════════════════════════════════════════════════════════
# Helpers (defined first so button callbacks can use them safely)
# ══════════════════════════════════════════════════════════════════════════════
def _fetch_ncert(book, engine):
    urls = ncert_chapter_urls(book)
    url_list = [
        {"url": u["url"], "label": f"Ch {u['chapter']}", "filename": u["filename"]}
        for u in urls
    ]
    progress = st.progress(0.0, text=f"Fetching {book['title']}…")
    results = fetch_many(
        url_list,
        on_progress=lambda i, total, lbl: progress.progress(
            min(i / max(total, 1), 1.0), text=f"{lbl} — {i}/{total}"
        ),
    )
    progress.empty()

    ok, fail, ingested = 0, 0, 0
    for r in results:
        if r["bytes"]:
            count = engine.ingest_pdf_bytes(
                r["bytes"],
                name=f"NCERT-C{book['class']}-{book['subject']}-{r['filename']}",
                doc_type="ncert",
                subject=book["subject"],
            )
            ingested += count
            ok += 1
        else:
            fail += 1
    if ok:
        st.success(
            f"✓ Fetched {ok} chapter(s) · {ingested} chunks indexed · {book['title']}"
        )
    if fail:
        st.warning(
            f"⚠ {fail} chapter(s) couldn't be fetched directly. NCERT occasionally "
            f"changes filename patterns. Visit [ncert.nic.in](https://ncert.nic.in) "
            f"and upload the PDFs from the Home page as a fallback."
        )


def _fetch_and_index(url, title, subject, engine):
    progress = st.progress(0.3, text=f"Fetching {title}…")
    data = fetch_pdf(url)
    progress.progress(0.7, text="Indexing…")
    if data:
        count = engine.ingest_pdf_bytes(
            data, name=title, doc_type="official", subject=subject,
        )
        progress.empty()
        if count:
            st.success(f"✓ Added {title} · {count} chunks indexed")
        else:
            st.info(
                f"Fetched {title}, but the content looks like a listing page rather "
                f"than a PDF. Visit the source link and upload the actual PDF from Home."
            )
    else:
        progress.empty()
        st.warning(
            f"Couldn't auto-fetch **{title}** — some gov portals list PDFs rather "
            f"than serving them directly at a stable URL. Open the source link "
            f"and upload the PDF manually from the Home page."
        )


def _fetch_bundle(bundle, engine):
    st.markdown("#### 📦 Fetching bundle…")
    for code in bundle["ncerts"]:
        book = next((n for n in NCERTS if n["code"] == code), None)
        if book:
            with st.status(f"📚 {book['title']}", expanded=False):
                _fetch_ncert(book, engine)
    for title in bundle["official"]:
        r = next((o for o in OFFICIAL_RESOURCES if o["title"] == title), None)
        if r:
            with st.status(f"🏛️ {title}", expanded=False):
                _fetch_and_index(r["url"], r["title"], r["subject"], engine)
    st.success(f"✓ Bundle '{bundle['title']}' complete")
    st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
# Page
# ══════════════════════════════════════════════════════════════════════════════
hero(
    title="The Library",
    tagline="Only the legit stuff.",
    subtitle="NCERTs from ncert.nic.in, Constitution from legislative.gov.in, "
             "Economic Survey from indiabudget.gov.in, 2nd ARC from darpg.gov.in. "
             "One click fetches them and makes them searchable from Study Chat.",
    eyebrow="Official · Public · Free",
)

engine = get_engine()

tab_ncert, tab_official, tab_bulk = st.tabs(
    ["📚 NCERTs", "🏛️ Official Resources", "⚡ One-Click Bundles"]
)

# ────────────────── TAB 1 ──────────────────
with tab_ncert:
    st.markdown(
        "NCERT textbooks are the bedrock of UPSC preparation — especially Class 6–12 "
        "Polity, History, Geography, and Economics. Pick what you need below."
    )

    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        filter_class = st.multiselect(
            "Class",
            options=sorted({n["class"] for n in NCERTS}),
            default=[],
            placeholder="All",
        )
    with col_f2:
        filter_subj = st.multiselect(
            "Subject",
            options=sorted({n["subject"] for n in NCERTS}),
            default=[],
            placeholder="All",
        )

    filtered = [
        n for n in NCERTS
        if (not filter_class or n["class"] in filter_class)
        and (not filter_subj or n["subject"] in filter_subj)
    ]
    st.caption(f"**{len(filtered)} book(s)** match")

    grouped: dict = {}
    for n in filtered:
        grouped.setdefault(n["subject"], []).append(n)

    for subj, books in grouped.items():
        with st.expander(f"**{subj}** — {len(books)} book(s)",
                         expanded=len(grouped) <= 3):
            for book in books:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(
                        f"**Class {book['class']} · {book['title']}**  \n"
                        f"<span class='sansad-cite'>{book['chapters']} chapters</span> "
                        f"<span class='sansad-cite'>code {book['code']}</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    key = f"fetch_{book['code']}"
                    if st.button("⬇ Fetch all chapters",
                                 key=key, use_container_width=True):
                        _fetch_ncert(book, engine)

# ────────────────── TAB 2 ──────────────────
with tab_official:
    st.markdown(
        "Canonical government sources. **must-read** = essential. "
        "**reference** = look up as needed."
    )
    by_cat = group_official_by_category()

    for category, items in by_cat.items():
        st.markdown(f"### {category}")
        for idx, r in enumerate(items):
            key = f"ofc_{category}_{idx}".replace(" ", "_").replace("&", "and")
            if resource_card(r["title"], r["why"], r["url"], r["tier"], key=key):
                _fetch_and_index(r["url"], r["title"], r["subject"], engine)

# ────────────────── TAB 3 ──────────────────
with tab_bulk:
    st.markdown(
        "Curated bundles — hand-picked combos for common prep stages. "
        "One click fetches the whole set."
    )

    bundles = [
        {
            "title": "🏁 Foundation Starter Pack",
            "desc": "Class 9–10 NCERTs in Polity, History, Geography, Economy. Start here if you're new.",
            "ncerts": ["iess4", "iess1", "iess3", "iess2", "jess4", "jess1", "jess3", "jess2"],
            "official": [],
        },
        {
            "title": "🏛️ Polity Core",
            "desc": "Class 9–12 Polity NCERTs + the Constitution of India (full text).",
            "ncerts": ["iess4", "jess4", "keps2", "leps2"],
            "official": ["The Constitution of India (Full Text, Updated)"],
        },
        {
            "title": "🌾 Economy Essentials",
            "desc": "Class 9–12 Economy NCERTs + latest Economic Survey + Budget.",
            "ncerts": ["iess2", "jess2", "keec1", "leec1", "leec2"],
            "official": ["Economic Survey (Latest)", "Union Budget (Latest)"],
        },
        {
            "title": "🌍 Geography Complete",
            "desc": "Class 11 Physical + India geo, Class 12 Human + India-People-Economy.",
            "ncerts": ["kegy2", "kegy1", "legy1", "legy2"],
            "official": [],
        },
        {
            "title": "⚖️ Ethics & Governance (Mains GS-IV)",
            "desc": "2nd ARC Reports index + Class 11 Political Theory.",
            "ncerts": ["keps1"],
            "official": ["Second ARC — All 15 Reports (Index)"],
        },
        {
            "title": "🗺️ History All-In",
            "desc": "Ancient, Medieval, Modern — Class 6–12 History NCERTs.",
            "ncerts": ["fess1", "gess1", "hess2", "iess3", "jess3",
                       "kehs1", "lehs1", "lehs2", "lehs3"],
            "official": [],
        },
    ]

    for b in bundles:
        with st.container(border=True):
            st.markdown(f"### {b['title']}")
            st.caption(b["desc"])
            n_count = len(b["ncerts"])
            o_count = len(b["official"])
            st.markdown(
                f"<span class='sansad-cite'>{n_count} NCERT book(s)</span> "
                f"<span class='sansad-cite'>{o_count} official doc(s)</span>",
                unsafe_allow_html=True,
            )
            if st.button("Fetch entire bundle",
                         key=f"bundle_{b['title']}",
                         type="primary", use_container_width=True):
                _fetch_bundle(b, engine)
