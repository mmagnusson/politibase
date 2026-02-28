"""API routes for elections."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from politibase.db.database import get_db
from politibase.models.schema import Candidacy, Candidate, Election, Office

router = APIRouter()


@router.get("/")
def list_elections(
    jurisdiction_id: int | None = None,
    upcoming: bool = False,
    db: Session = Depends(get_db),
):
    """List elections. Set upcoming=true to see only future elections."""
    q = db.query(Election).join(Office)

    if jurisdiction_id:
        q = q.filter(Office.jurisdiction_id == jurisdiction_id)
    if upcoming:
        q = q.filter(Election.election_date >= date.today())

    elections = q.order_by(Election.election_date.desc()).all()
    return [
        {
            "id": e.id,
            "office_title": e.office.title,
            "office_level": e.office.office_level,
            "jurisdiction_id": e.office.jurisdiction_id,
            "election_date": e.election_date.isoformat(),
            "election_type": e.election_type,
            "filing_deadline": e.filing_deadline.isoformat() if e.filing_deadline else None,
            "registration_deadline": (
                e.registration_deadline.isoformat() if e.registration_deadline else None
            ),
            "description": e.description,
        }
        for e in elections
    ]


@router.get("/{election_id}")
def get_election(election_id: int, db: Session = Depends(get_db)):
    """Get election details with all candidates."""
    e = db.query(Election).get(election_id)
    if not e:
        return {"error": "Election not found"}, 404

    candidacies = (
        db.query(Candidacy)
        .filter(Candidacy.election_id == e.id)
        .join(Candidate)
        .order_by(Candidate.last_name)
        .all()
    )

    return {
        "id": e.id,
        "office_title": e.office.title,
        "office_level": e.office.office_level,
        "jurisdiction_id": e.office.jurisdiction_id,
        "election_date": e.election_date.isoformat(),
        "election_type": e.election_type,
        "filing_deadline": e.filing_deadline.isoformat() if e.filing_deadline else None,
        "description": e.description,
        "candidates": [
            {
                "id": cy.candidate.id,
                "full_name": cy.candidate.full_name,
                "status": cy.status,
                "is_incumbent": cy.is_incumbent,
                "votes_received": cy.votes_received,
                "vote_percentage": cy.vote_percentage,
                "party_affiliation": cy.candidate.party_affiliation,
                "occupation": cy.candidate.occupation,
            }
            for cy in candidacies
        ],
    }
