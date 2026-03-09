"""Ballot lookup — "What's on my ballot?" endpoint.

Combines local database data with Google Civic API for comprehensive results.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from politibase.db.database import get_db
from politibase.models.schema import Candidate, Candidacy, Election, Jurisdiction, Office, OfficeTerm
from politibase.scrapers.google_civic import lookup_representatives, lookup_elections

router = APIRouter()

# Known address → jurisdiction mappings for the FM metro
# In production, this would use geocoding + district shapefiles
_CITY_KEYWORDS = {
    "moorhead": "City of Moorhead",
    "fargo": "City of Fargo",
}
_COUNTY_KEYWORDS = {
    "moorhead": "Clay County",
    "dilworth": "Clay County",
    "glyndon": "Clay County",
    "hawley": "Clay County",
    "fargo": "Cass County",
    "west fargo": "Cass County",
    "horace": "Cass County",
}
_SCHOOL_KEYWORDS = {
    "moorhead": "Moorhead Area Public Schools (ISD 152)",
    "fargo": "Fargo Public Schools",
}


def _resolve_jurisdictions(address: str, db: Session) -> list[dict]:
    """Given an address string, find matching jurisdictions in our database.

    This is a simplified keyword-based matcher. A production system would use
    geocoding (lat/lng) + PostGIS district boundary queries.
    """
    addr_lower = address.lower()
    matches = []

    for keyword, jname in _CITY_KEYWORDS.items():
        if keyword in addr_lower:
            j = db.query(Jurisdiction).filter(Jurisdiction.name == jname).first()
            if j:
                matches.append(j)

    for keyword, jname in _COUNTY_KEYWORDS.items():
        if keyword in addr_lower:
            j = db.query(Jurisdiction).filter(Jurisdiction.name == jname).first()
            if j and j not in matches:
                matches.append(j)

    for keyword, jname in _SCHOOL_KEYWORDS.items():
        if keyword in addr_lower:
            j = db.query(Jurisdiction).filter(Jurisdiction.name == jname).first()
            if j and j not in matches:
                matches.append(j)

    return matches


@router.get("/lookup")
def ballot_lookup(
    address: str = Query(..., description="Street address, e.g. '123 Main St, Moorhead, MN 56560'"),
    db: Session = Depends(get_db),
):
    """Look up what's on the ballot for a given address.

    Combines local Politibase data with the Google Civic Information API.
    """
    # 1. Resolve address to local jurisdictions
    jurisdictions = _resolve_jurisdictions(address, db)

    local_results = []
    for j in jurisdictions:
        offices = db.query(Office).filter(Office.jurisdiction_id == j.id).all()
        jurisdiction_data = {
            "jurisdiction": {
                "id": j.id,
                "name": j.name,
                "type": j.jurisdiction_type,
            },
            "offices": [],
        }

        for office in offices:
            office_data = {
                "id": office.id,
                "title": office.title,
                "level": office.office_level,
                "district": office.district,
                "current_holders": [],
                "upcoming_elections": [],
            }

            # Current holders from OfficeTerm
            terms = (
                db.query(OfficeTerm)
                .filter(OfficeTerm.office_id == office.id, OfficeTerm.status == "serving")
                .join(Candidate)
                .all()
            )
            for term in terms:
                office_data["current_holders"].append(
                    {
                        "id": term.candidate.id,
                        "name": term.candidate.full_name,
                        "occupation": term.candidate.occupation,
                        "is_term_limited": term.is_term_limited,
                        "term_end": term.term_end.isoformat() if term.term_end else None,
                    }
                )

            # Upcoming elections
            elections = (
                db.query(Election)
                .filter(Election.office_id == office.id, Election.filing_deadline.isnot(None))
                .order_by(Election.election_date.desc())
                .all()
            )
            for election in elections:
                office_data["upcoming_elections"].append(
                    {
                        "election_id": election.id,
                        "date": election.election_date.isoformat(),
                        "type": election.election_type,
                        "filing_deadline": election.filing_deadline.isoformat(),
                        "description": election.description,
                    }
                )

            jurisdiction_data["offices"].append(office_data)

        local_results.append(jurisdiction_data)

    # 2. Supplement with Google Civic API data
    civic_data = lookup_representatives(address)

    return {
        "address": address,
        "local_data": local_results,
        "civic_api": civic_data,
    }
