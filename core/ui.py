"""
UI helpers.

Aesthetic: editorial/parliamentary. Warm ivory base, deep maroon + olive accents,
Fraunces (display serif) + Spectral (body serif). Think: a well-made civics journal,
not another SaaS dashboard.
"""
import streamlit as st


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,800&family=Spectral:wght@400;500;700&display=swap');

/* ── Global ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Spectral', Georgia, serif;
    color: #2a1f14;
}
.stApp {
    background:
        radial-gradient(at 10% 0%, #f5efe4 0%, transparent 50%),
        radial-gradient(at 90% 100%, #ede3d0 0%, transparent 50%),
        #faf7f2;
}

/* Headings */
h1, h2, h3, h4 {
    font-family: 'Fraunces', 'Playfair Display', serif !important;
    font-weight: 600 !important;
    color: #3d2817 !important;
    letter-spacing: -0.01em;
}
h1 { font-weight: 800 !important; letter-spacing: -0.025em; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3d2817 0%, #2a1f14 100%);
}
section[data-testid="stSidebar"] * {
    color: #f5efe4 !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    color: #faf7f2 !important;
    border-color: rgba(245,239,228,0.2) !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #e8c88a !important;
    font-family: 'Fraunces', serif !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #c9b68f !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    border-radius: 4px !important;
    border: 1px solid #6b4e2a !important;
    background: #faf7f2 !important;
    color: #3d2817 !important;
    transition: all .2s ease;
}
.stButton > button:hover {
    background: #3d2817 !important;
    color: #faf7f2 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(61, 40, 23, 0.2);
}
.stButton > button[kind="primary"] {
    background: #6b4e2a !important;
    color: #faf7f2 !important;
    border-color: #3d2817 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3d2817 !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
    border-radius: 4px !important;
    border-color: #c9b68f !important;
    background: #fffdf9 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 2px solid #d9c9a8;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    color: #8b6f47;
    padding: 10px 18px;
    border-radius: 4px 4px 0 0;
}
.stTabs [aria-selected="true"] {
    background: #fffdf9 !important;
    color: #3d2817 !important;
    border-bottom: 3px solid #8a2622 !important;
}

/* Info/alerts */
.stAlert {
    border-radius: 4px !important;
    border-left-width: 4px !important;
    font-family: 'Spectral', serif;
}

/* Custom components */
.sansad-hero {
    padding: 48px 32px 32px;
    margin: -20px -20px 32px -20px;
    background:
        linear-gradient(180deg, rgba(61,40,23,0.02) 0%, transparent 100%),
        radial-gradient(ellipse at top right, rgba(138,38,34,0.06), transparent 50%),
        #fffdf9;
    border-bottom: 1px solid #e8ddc5;
    position: relative;
    overflow: hidden;
}
.sansad-hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -40px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(232,200,138,0.35) 0%, transparent 70%);
    pointer-events: none;
}
.sansad-hero-eyebrow {
    font-family: 'Fraunces', serif;
    font-style: italic;
    color: #8a2622;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-size: 12px;
    margin-bottom: 8px;
}
.sansad-hero-title {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 64px;
    line-height: 1;
    color: #3d2817;
    margin: 0 0 8px 0;
    letter-spacing: -0.035em;
}
.sansad-hero-tag {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 24px;
    color: #6b4e2a;
    margin-bottom: 14px;
}
.sansad-hero-sub {
    font-family: 'Spectral', serif;
    color: #5a4a3a;
    font-size: 16px;
    max-width: 640px;
}
.sansad-hero-divider {
    width: 80px; height: 2px;
    background: linear-gradient(90deg, #8a2622, #e8c88a);
    margin: 16px 0 0 0;
}

/* Mode cards */
.sansad-mode {
    padding: 22px 20px;
    border: 1px solid #d9c9a8;
    border-radius: 6px;
    background: #fffdf9;
    transition: all .2s ease;
    cursor: pointer;
    height: 100%;
    position: relative;
}
.sansad-mode:hover {
    border-color: #8b6f47;
    box-shadow: 0 4px 16px rgba(61, 40, 23, 0.08);
    transform: translateY(-2px);
}
.sansad-mode.active {
    border: 2px solid #8a2622;
    background: linear-gradient(180deg, #fffdf9, #faf0e8);
}
.sansad-mode.active::before {
    content: "★ active";
    position: absolute;
    top: -10px; left: 16px;
    background: #8a2622;
    color: #fffdf9;
    padding: 2px 10px;
    border-radius: 3px;
    font-family: 'Fraunces', serif;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.sansad-mode-icon { font-size: 34px; margin-bottom: 8px; }
.sansad-mode-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 22px;
    color: #3d2817;
    margin-bottom: 6px;
}
.sansad-mode-desc {
    color: #5a4a3a;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 12px;
}
.sansad-mode-meta {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 12px;
    color: #8b6f47;
    letter-spacing: 0.05em;
}

/* Citation chips */
.sansad-cite {
    display: inline-block;
    font-family: 'Fraunces', serif;
    font-size: 11px;
    background: #f5efe4;
    color: #6b4e2a;
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
    border-radius: 3px;
    border: 1px solid #d9c9a8;
}

/* Footer */
.sansad-foot {
    display: flex; justify-content: space-between;
    margin-top: 48px; padding-top: 20px;
    border-top: 1px solid #e8ddc5;
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 12px;
    color: #8b6f47;
}

/* Resource cards */
.sansad-resource {
    padding: 16px 18px;
    margin-bottom: 10px;
    border: 1px solid #e8ddc5;
    background: #fffdf9;
    border-radius: 4px;
    border-left: 3px solid #8b6f47;
}
.sansad-resource.essential { border-left-color: #8a2622; }
.sansad-resource h4 {
    margin: 0 0 4px 0 !important;
    font-size: 16px !important;
}
.sansad-resource p { margin: 0; color: #5a4a3a; font-size: 14px; }
.sansad-tier {
    font-family: 'Fraunces', serif; font-style: italic;
    font-size: 11px; color: #8a2622;
    letter-spacing: 0.08em; text-transform: uppercase;
}

/* Chat bubbles — override Streamlit default */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stChatMessageContent"] {
    background: #fffdf9;
    border: 1px solid #e8ddc5;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'Spectral', serif;
    font-size: 15.5px;
    line-height: 1.65;
}

/* MCQ option buttons */
.sansad-mcq-opt {
    display: block;
    width: 100%;
    text-align: left;
    padding: 12px 16px;
    margin-bottom: 8px;
    background: #fffdf9;
    border: 1px solid #d9c9a8;
    border-radius: 4px;
    font-family: 'Spectral', serif;
    font-size: 15px;
    cursor: pointer;
    transition: all .15s;
}
.sansad-mcq-opt:hover { border-color: #8b6f47; background: #f9f3e6; }
.sansad-mcq-opt.correct { border-color: #4a6b2a; background: #edf3e0; }
.sansad-mcq-opt.wrong { border-color: #8a2622; background: #f5e0de; }

/* Make mode-select buttons compact — they sit below the visual cards */
.stButton > button[kind="secondary"]:has(+ *),
button[data-testid*="mode_"] {
    font-size: 12px !important;
    padding: 4px 8px !important;
    margin-top: 4px !important;
    opacity: 0.75;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, tagline: str, subtitle: str, eyebrow: str = "UPSC · RAG · Voice"):
    st.markdown(f"""
    <div class="sansad-hero">
      <div class="sansad-hero-eyebrow">{eyebrow}</div>
      <div class="sansad-hero-title">{title}</div>
      <div class="sansad-hero-tag">{tagline}</div>
      <div class="sansad-hero-sub">{subtitle}</div>
      <div class="sansad-hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)


def mode_card(icon: str, title: str, desc: str, meta: str, active: bool, key: str) -> bool:
    """Clickable mode card. Returns True if clicked."""
    active_cls = "active" if active else ""
    # Render the card as HTML for the look, and place an invisible Streamlit button beneath it
    # for the click handling.
    st.markdown(f"""
    <div class="sansad-mode {active_cls}">
      <div class="sansad-mode-icon">{icon}</div>
      <div class="sansad-mode-title">{title}</div>
      <div class="sansad-mode-desc">{desc}</div>
      <div class="sansad-mode-meta">{meta}</div>
    </div>
    """, unsafe_allow_html=True)
    return st.button(
        "✓ Active" if active else "Select this mode",
        key=key,
        use_container_width=True,
        type="primary" if active else "secondary",
    )


def stat_pill(label: str, value: str):
    return f"""<span class="sansad-cite"><b>{value}</b> {label}</span>"""


def resource_card(title: str, why: str, url: str, tier: str, key: str) -> bool:
    """Renders a resource card with a single fetch button. Returns True if button clicked."""
    tier_cls = "essential" if tier == "essential" else ""
    tier_label = "must-read" if tier == "essential" else "reference"
    st.markdown(f"""
    <div class="sansad-resource {tier_cls}">
      <div class="sansad-tier">{tier_label}</div>
      <h4>{title}</h4>
      <p>{why}</p>
      <p style="margin-top:6px;"><a href="{url}" target="_blank"
         style="color:#8b6f47;font-size:12px;">↗ open source page</a></p>
    </div>
    """, unsafe_allow_html=True)
    return st.button("⬇ Fetch & index this", key=key, use_container_width=True)
