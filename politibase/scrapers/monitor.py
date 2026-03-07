"""Page change monitor for government websites.

Periodically fetches key pages and compares content hashes to detect when
information has changed. This is a lightweight alternative to full scraping —
it tells you *when* to look, not *what* changed.

Usage:
    from politibase.scrapers.monitor import check_all_sources
    changes = check_all_sources()
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "snapshots"

# Pages to monitor for changes.
# Each entry: (name, url, css_selector_or_None)
# If css_selector is provided, only that portion of the page is hashed
# (this avoids false positives from dynamic headers/footers/ads).
MONITORED_PAGES = [
    (
        "moorhead_council_members",
        "https://www.moorheadmn.gov/government/mayor-city-council",
        None,
    ),
    (
        "moorhead_elections",
        "https://www.moorheadmn.gov/government/elections",
        None,
    ),
    (
        "fargo_commission_members",
        "https://fargond.gov/city-government/departments/city-commission/members",
        None,
    ),
    (
        "clay_county_elected_officials",
        "https://claycountymn.gov/276/Elected-Officials",
        None,
    ),
    (
        "cass_county_elected_officials",
        "https://www.casscountynd.gov/our-county/finance-office/elections/elected-officials-in-cass-county",
        None,
    ),
    (
        "moorhead_school_board",
        "https://www.isd152.org/page/school-board-elections",
        None,
    ),
    (
        "fargo_school_board",
        "https://www.fargo.k12.nd.us/boardmembers",
        None,
    ),
    (
        "fargo_school_election",
        "https://www.fargo.k12.nd.us/boardelection",
        None,
    ),
    (
        "fargo_park_board",
        "https://www.fargoparks.com/park-board",
        None,
    ),
    (
        "wf_park_board",
        "https://wfparks.org/wf-parks-board/",
        None,
    ),
    (
        "clay_county_election_results",
        "https://claycountymn.gov/351/Election-Results",
        None,
    ),
    (
        "cass_county_elections",
        "https://www.casscountynd.gov/government/elections",
        None,
    ),
]


def _fetch_content(url: str, selector: str | None = None) -> str:
    """Fetch a page and extract the text content for hashing."""
    headers = {
        "User-Agent": "Politibase/0.1 (civic data monitor; https://github.com/mmagnusson/politibase)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return ""

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove script, style, nav, footer to reduce noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    if selector:
        target = soup.select_one(selector)
        if target:
            return target.get_text(separator="\n", strip=True)

    # Use the main content area if we can find it
    main = soup.find("main") or soup.find("article") or soup.find(id="content")
    if main:
        return main.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)


def _content_hash(text: str) -> str:
    """Hash normalized text content."""
    # Normalize whitespace to reduce false positives
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode()).hexdigest()[:20]


def check_page(name: str, url: str, selector: str | None = None) -> dict:
    """Check a single page for changes.

    Returns a dict with:
        name, url, changed (bool), hash, previous_hash, checked_at
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_file = SNAPSHOT_DIR / f"monitor_{name}.json"

    content = _fetch_content(url, selector)
    if not content:
        return {"name": name, "url": url, "error": "failed to fetch", "changed": False}

    current_hash = _content_hash(content)
    checked_at = datetime.utcnow().isoformat()

    previous = None
    if snapshot_file.exists():
        try:
            previous = json.loads(snapshot_file.read_text())
        except json.JSONDecodeError:
            pass

    changed = previous is not None and previous.get("hash") != current_hash

    result = {
        "name": name,
        "url": url,
        "hash": current_hash,
        "previous_hash": previous.get("hash") if previous else None,
        "checked_at": checked_at,
        "previous_checked_at": previous.get("checked_at") if previous else None,
        "changed": changed,
    }

    # Save new snapshot
    snapshot_file.write_text(json.dumps(result, indent=2))

    return result


def check_all_sources(delay: float = 2.0) -> list[dict]:
    """Check all monitored pages for changes.

    Args:
        delay: Seconds between requests (be polite to government servers)

    Returns:
        List of result dicts, one per page.
    """
    results = []
    for name, url, selector in MONITORED_PAGES:
        logger.info("Checking %s (%s)", name, url)
        result = check_page(name, url, selector)
        results.append(result)

        if result.get("changed"):
            logger.warning("CHANGE DETECTED: %s (%s)", name, url)
        elif result.get("error"):
            logger.warning("ERROR: %s - %s", name, result["error"])
        else:
            logger.info("No change: %s (hash: %s)", name, result.get("hash", "?"))

        time.sleep(delay)

    return results
