"""
Official UPSC Resource Catalog.

Every URL here is from a .gov.in / .nic.in / publicly-listed official source.
PDF filename pattern on ncert.nic.in: textbook/pdf/{code}{chapterN}.pdf
  e.g. iess301.pdf = Class 9 History Ch 1 ("India and the Contemporary World")

For non-NCERT resources we point to full-book PDFs from source ministries.
"""
from typing import List, Dict


# ── NCERT catalog (UPSC-relevant subset) ─────────────────────────────────────
# The "code" is the NCERT textbook code. Chapters = number of chapters.
# For UPSC, Class 6-12 NCERTs are the foundational bedrock.
NCERTS: List[Dict] = [
    # ─── Class 6 ──────────────────────────────────────────────────────
    {"class": 6, "subject": "History",    "title": "Our Pasts – I",                "code": "fess1", "chapters": 11, "tags": ["history", "ancient"]},
    {"class": 6, "subject": "Geography",  "title": "The Earth Our Habitat",        "code": "fess2", "chapters": 8,  "tags": ["geography", "physical"]},
    {"class": 6, "subject": "Polity",     "title": "Social and Political Life – I","code": "fess3", "chapters": 9,  "tags": ["polity", "civics"]},
    {"class": 6, "subject": "Science",    "title": "Science",                      "code": "fesc1", "chapters": 16, "tags": ["science"]},

    # ─── Class 7 ──────────────────────────────────────────────────────
    {"class": 7, "subject": "History",    "title": "Our Pasts – II (Medieval)",    "code": "gess1", "chapters": 10, "tags": ["history", "medieval"]},
    {"class": 7, "subject": "Geography",  "title": "Our Environment",              "code": "gess2", "chapters": 9,  "tags": ["geography"]},
    {"class": 7, "subject": "Polity",     "title": "Social and Political Life – II","code": "gess3", "chapters": 9,  "tags": ["polity"]},
    {"class": 7, "subject": "Science",    "title": "Science",                      "code": "gesc1", "chapters": 18, "tags": ["science"]},

    # ─── Class 8 ──────────────────────────────────────────────────────
    {"class": 8, "subject": "History",    "title": "Our Pasts – III (Modern)",     "code": "hess2", "chapters": 10, "tags": ["history", "modern"]},
    {"class": 8, "subject": "Geography",  "title": "Resources and Development",    "code": "hess4", "chapters": 6,  "tags": ["geography", "economy"]},
    {"class": 8, "subject": "Polity",     "title": "Social and Political Life – III","code": "hess3", "chapters": 10, "tags": ["polity"]},
    {"class": 8, "subject": "Science",    "title": "Science",                      "code": "hesc1", "chapters": 18, "tags": ["science"]},

    # ─── Class 9 ──────────────────────────────────────────────────────
    {"class": 9, "subject": "History",    "title": "India and the Contemporary World – I", "code": "iess3", "chapters": 5,  "tags": ["history", "world"]},
    {"class": 9, "subject": "Geography",  "title": "Contemporary India – I",       "code": "iess1", "chapters": 6,  "tags": ["geography", "india"]},
    {"class": 9, "subject": "Polity",     "title": "Democratic Politics – I",      "code": "iess4", "chapters": 5,  "tags": ["polity"]},
    {"class": 9, "subject": "Economy",    "title": "Economics",                    "code": "iess2", "chapters": 4,  "tags": ["economy"]},
    {"class": 9, "subject": "Science",    "title": "Science",                      "code": "iesc1", "chapters": 15, "tags": ["science"]},

    # ─── Class 10 ─────────────────────────────────────────────────────
    {"class": 10, "subject": "History",   "title": "India and the Contemporary World – II", "code": "jess3", "chapters": 5,  "tags": ["history", "world"]},
    {"class": 10, "subject": "Geography", "title": "Contemporary India – II",      "code": "jess1", "chapters": 7,  "tags": ["geography", "india"]},
    {"class": 10, "subject": "Polity",    "title": "Democratic Politics – II",     "code": "jess4", "chapters": 8,  "tags": ["polity"]},
    {"class": 10, "subject": "Economy",   "title": "Understanding Economic Development", "code": "jess2", "chapters": 5,  "tags": ["economy"]},
    {"class": 10, "subject": "Science",   "title": "Science",                      "code": "jesc1", "chapters": 16, "tags": ["science"]},

    # ─── Class 11 ─────────────────────────────────────────────────────
    {"class": 11, "subject": "History",   "title": "Themes in World History",      "code": "kehs1", "chapters": 11, "tags": ["history", "world"]},
    {"class": 11, "subject": "Geography", "title": "Fundamentals of Physical Geography", "code": "kegy2", "chapters": 16, "tags": ["geography", "physical"]},
    {"class": 11, "subject": "Geography", "title": "India – Physical Environment", "code": "kegy1", "chapters": 7,  "tags": ["geography", "india"]},
    {"class": 11, "subject": "Polity",    "title": "Indian Constitution at Work",  "code": "keps2", "chapters": 10, "tags": ["polity", "constitution"]},
    {"class": 11, "subject": "Polity",    "title": "Political Theory",             "code": "keps1", "chapters": 10, "tags": ["polity", "theory"]},
    {"class": 11, "subject": "Economy",   "title": "Indian Economic Development",  "code": "keec1", "chapters": 10, "tags": ["economy", "india"]},
    {"class": 11, "subject": "Sociology", "title": "Introducing Sociology",        "code": "kesy1", "chapters": 5,  "tags": ["sociology"]},
    {"class": 11, "subject": "Sociology", "title": "Understanding Society",        "code": "kesy2", "chapters": 5,  "tags": ["sociology"]},
    {"class": 11, "subject": "Fine Art",  "title": "An Introduction to Indian Art","code": "kefa1", "chapters": 8,  "tags": ["culture", "art"]},

    # ─── Class 12 ─────────────────────────────────────────────────────
    {"class": 12, "subject": "History",   "title": "Themes in Indian History – I", "code": "lehs1", "chapters": 4,  "tags": ["history", "ancient"]},
    {"class": 12, "subject": "History",   "title": "Themes in Indian History – II","code": "lehs2", "chapters": 5,  "tags": ["history", "medieval"]},
    {"class": 12, "subject": "History",   "title": "Themes in Indian History – III","code": "lehs3", "chapters": 6,  "tags": ["history", "modern"]},
    {"class": 12, "subject": "Geography", "title": "Fundamentals of Human Geography","code": "legy1", "chapters": 10, "tags": ["geography", "human"]},
    {"class": 12, "subject": "Geography", "title": "India – People and Economy",   "code": "legy2", "chapters": 12, "tags": ["geography", "india"]},
    {"class": 12, "subject": "Polity",    "title": "Contemporary World Politics",  "code": "leps1", "chapters": 9,  "tags": ["polity", "ir"]},
    {"class": 12, "subject": "Polity",    "title": "Politics in India Since Independence","code": "leps2", "chapters": 9,  "tags": ["polity", "history"]},
    {"class": 12, "subject": "Economy",   "title": "Introductory Microeconomics",  "code": "leec2", "chapters": 6,  "tags": ["economy", "micro"]},
    {"class": 12, "subject": "Economy",   "title": "Introductory Macroeconomics",  "code": "leec1", "chapters": 6,  "tags": ["economy", "macro"]},
    {"class": 12, "subject": "Sociology", "title": "Indian Society",               "code": "lesy1", "chapters": 7,  "tags": ["sociology"]},
    {"class": 12, "subject": "Sociology", "title": "Social Change and Development in India", "code": "lesy2", "chapters": 8,  "tags": ["sociology"]},
]


def ncert_chapter_urls(item: Dict) -> List[Dict]:
    """Build chapter-wise PDF URL list for an NCERT book.

    NCERT's actual pattern: {code}{chapter}.pdf — single digit for ch 1–9,
    two digits from ch 10 onward. Example: iess31.pdf, iess32.pdf, iess310.pdf.
    """
    urls = []
    for ch in range(1, item["chapters"] + 1):
        fname = f"{item['code']}{ch}.pdf"
        urls.append({
            "chapter": ch,
            "url": f"https://ncert.nic.in/textbook/pdf/{fname}",
            "filename": fname,
        })
    return urls


# ── Other official resources (PIB/Gov/Parliament) ───────────────────────────
OFFICIAL_RESOURCES: List[Dict] = [
    # CONSTITUTION
    {
        "category": "Constitution & Polity",
        "title": "The Constitution of India (Full Text, Updated)",
        "subject": "Polity",
        "url": "https://legislative.gov.in/sites/default/files/COI.pdf",
        "why": "Canonical source. Every Article, Schedule, Amendment. Open any time for doubts.",
        "tier": "essential",
    },
    {
        "category": "Constitution & Polity",
        "title": "Basic Structure Doctrine — Kesavananda Bharati judgment (SC)",
        "subject": "Polity",
        "url": "https://main.sci.gov.in/judgments",
        "why": "Landmark judgment. Search 'Kesavananda Bharati' on the SC portal.",
        "tier": "reference",
    },
    {
        "category": "Constitution & Polity",
        "title": "Rules of Procedure and Conduct of Business — Lok Sabha",
        "subject": "Polity",
        "url": "https://sansad.in/getFile/rsnew/Procedure_Manual/rules_procedure_eng.pdf",
        "why": "Parliamentary procedure — recurring Prelims & Mains topic.",
        "tier": "reference",
    },

    # ECONOMY
    {
        "category": "Economy",
        "title": "Economic Survey (Latest)",
        "subject": "Economy",
        "url": "https://www.indiabudget.gov.in/economicsurvey/",
        "why": "Mandatory read for Mains GS-III. Download Volume I + Statistical Appendix.",
        "tier": "essential",
    },
    {
        "category": "Economy",
        "title": "Union Budget (Latest)",
        "subject": "Economy",
        "url": "https://www.indiabudget.gov.in/",
        "why": "Budget speech + FM's key announcements. Prelims factual + Mains analytical.",
        "tier": "essential",
    },
    {
        "category": "Economy",
        "title": "RBI Annual Report",
        "subject": "Economy",
        "url": "https://www.rbi.org.in/Scripts/AnnualReportMainDisplay.aspx",
        "why": "Authoritative on monetary policy, banking, financial stability.",
        "tier": "reference",
    },
    {
        "category": "Economy",
        "title": "NITI Aayog — Strategy for New India @ 75",
        "subject": "Economy",
        "url": "https://www.niti.gov.in/sites/default/files/2023-02/Strategy_for_New_India.pdf",
        "why": "47-chapter policy roadmap. Excellent Mains fodder across sectors.",
        "tier": "essential",
    },

    # GOVERNANCE / ETHICS
    {
        "category": "Governance & Ethics",
        "title": "Second ARC — All 15 Reports (Index)",
        "subject": "Ethics",
        "url": "https://darpg.gov.in/arc-reports",
        "why": "Gold for GS-II (Governance) & GS-IV (Ethics). Read 4th (Ethics) & 10th (Personnel Admin) minimum.",
        "tier": "essential",
    },
    {
        "category": "Governance & Ethics",
        "title": "Citizens' Charter Guidelines — DARPG",
        "subject": "Governance",
        "url": "https://darpg.gov.in/sites/default/files/CitizenCharter.pdf",
        "why": "Service delivery reform — GS-II staple.",
        "tier": "reference",
    },

    # INTERNATIONAL RELATIONS
    {
        "category": "International Relations",
        "title": "MEA — India's Foreign Policy (Annual Report)",
        "subject": "International Relations",
        "url": "https://www.mea.gov.in/annual-reports.htm",
        "why": "Definitive summary of India's bilateral & multilateral engagements.",
        "tier": "essential",
    },

    # ENVIRONMENT
    {
        "category": "Environment",
        "title": "State of Forest Report — FSI",
        "subject": "Environment",
        "url": "https://fsi.nic.in/forest-report",
        "why": "Biennial. Factual trove for Prelims; conservation angle for Mains.",
        "tier": "essential",
    },
    {
        "category": "Environment",
        "title": "India State of Environment Report — MoEFCC",
        "subject": "Environment",
        "url": "https://moef.gov.in/annual-report/",
        "why": "Climate, pollution, biodiversity — core Environment syllabus.",
        "tier": "reference",
    },

    # SCHEMES / SOCIAL JUSTICE
    {
        "category": "Schemes & Social Justice",
        "title": "Flagship Schemes Compendium — India.gov.in",
        "subject": "Governance",
        "url": "https://www.india.gov.in/spotlight/schemes",
        "why": "One-stop directory of every central scheme. Know 3-line summary of each.",
        "tier": "essential",
    },
    {
        "category": "Schemes & Social Justice",
        "title": "PM Portal — Ongoing Initiatives",
        "subject": "Governance",
        "url": "https://www.pmindia.gov.in/en/major_initiatives/",
        "why": "Flagship initiatives with official framing.",
        "tier": "reference",
    },

    # CURRENT AFFAIRS FEEDS
    {
        "category": "Current Affairs",
        "title": "PIB — Press Information Bureau (Daily)",
        "subject": "Current Affairs",
        "url": "https://pib.gov.in/AllRelease.aspx",
        "why": "Primary source for daily government news. Filter by ministry.",
        "tier": "essential",
    },
    {
        "category": "Current Affairs",
        "title": "PRS India — Bill Summaries",
        "subject": "Polity",
        "url": "https://prsindia.org/billtrack",
        "why": "Neutral, concise bill analyses — Mains-ready framing.",
        "tier": "essential",
    },
    {
        "category": "Current Affairs",
        "title": "Rajya Sabha TV / Sansad TV — The Big Picture",
        "subject": "General",
        "url": "https://sansadtv.nic.in/",
        "why": "Panel discussions on current issues. Interview prep gold.",
        "tier": "reference",
    },

    # UPSC OFFICIAL
    {
        "category": "UPSC Official",
        "title": "UPSC — Previous Year Question Papers",
        "subject": "PYQ",
        "url": "https://www.upsc.gov.in/examinations/previous-question-papers",
        "why": "Never skip. Download last 10 years of Prelims + Mains papers.",
        "tier": "essential",
    },
    {
        "category": "UPSC Official",
        "title": "UPSC — Detailed Syllabus (CSE)",
        "subject": "General",
        "url": "https://www.upsc.gov.in/sites/default/files/Notif-CSP-24-engl-130324.pdf",
        "why": "The bible. Tick off topics as you cover them.",
        "tier": "essential",
    },

    # CULTURE
    {
        "category": "Art & Culture",
        "title": "CCRT — Cultural Heritage of India (Indira Gandhi National Centre)",
        "subject": "Culture",
        "url": "https://ccrtindia.gov.in/readingroom.php",
        "why": "Free e-books on classical dance, music, architecture, festivals.",
        "tier": "reference",
    },
]


def group_official_by_category() -> Dict[str, List[Dict]]:
    out: Dict[str, List[Dict]] = {}
    for r in OFFICIAL_RESOURCES:
        out.setdefault(r["category"], []).append(r)
    return out


def ncerts_by_subject() -> Dict[str, List[Dict]]:
    out: Dict[str, List[Dict]] = {}
    for n in NCERTS:
        out.setdefault(n["subject"], []).append(n)
    return out
