"""Google Civic Information API integration.

Provides address-based ballot lookup — "what's on my ballot?" — using the
Google Civic Information API.

Requires a GOOGLE_CIVIC_API_KEY environment variable. Get a free key at:
https://console.cloud.google.com/ (enable "Google Civic Information API")
"""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)

CIVIC_API_BASE = "https://www.googleapis.com/civicinfo/v2"


def get_api_key() -> str | None:
    return os.environ.get("GOOGLE_CIVIC_API_KEY")


def lookup_representatives(address: str) -> dict[str, Any]:
    """Look up elected representatives for a given address.

    Returns officials at all levels of government: federal, state, county, city,
    school board (where data is available).

    Args:
        address: A street address, e.g. "123 Main St, Moorhead, MN 56560"

    Returns:
        Dict with 'offices' and 'officials' lists, or an error dict.
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "error": "GOOGLE_CIVIC_API_KEY not set. Get a free key at https://console.cloud.google.com/"
        }

    url = f"{CIVIC_API_BASE}/representatives"
    params = {"key": api_key, "address": address}

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Google Civic API error: %s", e)
        return {"error": str(e)}

    # Flatten the response into a more usable format
    offices = data.get("offices", [])
    officials = data.get("officials", [])
    result = []

    for office in offices:
        for idx in office.get("officialIndices", []):
            if idx < len(officials):
                official = officials[idx]
                result.append(
                    {
                        "office": office.get("name"),
                        "level": office.get("levels", []),
                        "division": office.get("divisionId", ""),
                        "name": official.get("name"),
                        "party": official.get("party", ""),
                        "phones": official.get("phones", []),
                        "urls": official.get("urls", []),
                        "emails": official.get("emails", []),
                        "photo_url": official.get("photoUrl", ""),
                        "channels": official.get("channels", []),
                    }
                )

    return {"representatives": result, "address": data.get("normalizedInput", {})}


def lookup_elections(address: str) -> dict[str, Any]:
    """Look up upcoming elections and what's on the ballot for an address.

    Args:
        address: A street address, e.g. "123 Main St, Fargo, ND 58103"

    Returns:
        Dict with election info and contests, or an error dict.
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "error": "GOOGLE_CIVIC_API_KEY not set. Get a free key at https://console.cloud.google.com/"
        }

    # First, get available elections
    elections_url = f"{CIVIC_API_BASE}/elections"
    try:
        resp = requests.get(elections_url, params={"key": api_key}, timeout=15)
        resp.raise_for_status()
        elections = resp.json().get("elections", [])
    except requests.RequestException as e:
        logger.error("Google Civic API elections error: %s", e)
        return {"error": str(e)}

    # Then look up voter info for each election
    results = []
    for election in elections:
        election_id = election.get("id")
        if election_id == "2000":  # Test election
            continue

        voter_url = f"{CIVIC_API_BASE}/voterinfo"
        params = {"key": api_key, "address": address, "electionId": election_id}
        try:
            resp = requests.get(voter_url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                results.append(
                    {
                        "election": election,
                        "contests": data.get("contests", []),
                        "polling_locations": data.get("pollingLocations", []),
                        "early_vote_sites": data.get("earlyVoteSites", []),
                    }
                )
        except requests.RequestException:
            continue

    return {"elections": results, "available_elections": elections}
