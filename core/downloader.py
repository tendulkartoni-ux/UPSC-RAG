"""
PDF Downloader.

Fetches remote PDFs with retries & timeout handling. Used by:
  - NCERT Library page (chapter-wise fetch → ingest)
  - Official resources page (full book / report → ingest)

Design choices:
  - requests with 15s timeout, 2 retries
  - In-memory bytes (no disk write needed — we pipe straight into pypdf)
  - Graceful error reporting — if a URL 404s (NCERT does occasionally
    restructure), we surface a clear message rather than silent failure.
"""
from __future__ import annotations
import time
from typing import Callable, Optional
import requests

UA = "Mozilla/5.0 (compatible; SansadUPSC/1.0; +https://example.com)"
TIMEOUT = 20


def fetch_pdf(url: str, max_retries: int = 2) -> Optional[bytes]:
    """Download a PDF. Returns bytes on success, None on failure."""
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA},
                             allow_redirects=True)
            if r.status_code == 200:
                # Sanity check — PDFs start with %PDF
                if r.content[:4] == b"%PDF":
                    return r.content
                # Sometimes the server sends HTML (404 page, redirect page)
                return None
            if r.status_code == 404:
                return None
            # Transient — retry
        except requests.RequestException:
            pass
        if attempt < max_retries:
            time.sleep(0.8 * (attempt + 1))
    return None


def fetch_many(
    urls: list[dict],
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> list[dict]:
    """
    urls: list of {'url': str, 'label': str, ...}
    Returns list of {'url', 'label', 'bytes' (or None), 'error' (or None), ...}
    """
    results = []
    total = len(urls)
    for i, item in enumerate(urls):
        if on_progress:
            on_progress(i, total, item.get("label", item["url"]))
        data = fetch_pdf(item["url"])
        entry = dict(item)
        if data:
            entry["bytes"] = data
            entry["error"] = None
        else:
            entry["bytes"] = None
            entry["error"] = "Could not fetch (404 or network issue)"
        results.append(entry)
    if on_progress:
        on_progress(total, total, "Done")
    return results
