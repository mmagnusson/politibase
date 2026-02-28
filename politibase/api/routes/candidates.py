"""API routes for candidates."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from politibase.db.database import get_db
from politibase.models.schema import (
    Candidate,
    Candidacy,
    Election,
    Endorsement,
    Office,
    Position,
)

router = APIRouter()


def _candidate_summary(c: Candidate) -> dict:
    return {
        "id": c.id,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "full_name": c.full_name,
        "party_affiliation": c.party_affiliation,
        "occupation": c.occupation,
        "residence_city": c.residence_city,
        "residence_state": c.residence_state,
        "photo_url": c.photo_url,
        "website": c.website,
    }


def _candidate_detail(c: Candidate, db: Session) -> dict:
    d = _candidate_summary(c)
    d["bio"] = c.bio
    d["education"] = c.education
    d["email"] = c.email
    d["phone"] = c.phone
    d["facebook_url"] = c.facebook_url
    d["twitter_handle"] = c.twitter_handle
    d["linkedin_url"] = c.linkedin_url

    # Candidacies (what they ran for / are running for)
    candidacies = (
        db.query(Candidacy)
        .filter(Candidacy.candidate_id == c.id)
        .join(Election)
        .join(Office)
        .order_by(Election.election_date.desc())
        .all()
    )
    d["candidacies"] = [
        {
            "id": cy.id,
            "election_date": cy.election.election_date.isoformat(),
            "election_type": cy.election.election_type,
            "office_title": cy.election.office.title,
            "office_level": cy.election.office.office_level,
            "jurisdiction_id": cy.election.office.jurisdiction_id,
            "status": cy.status,
            "is_incumbent": cy.is_incumbent,
            "votes_received": cy.votes_received,
            "vote_percentage": cy.vote_percentage,
        }
        for cy in candidacies
    ]

    # Positions
    positions = db.query(Position).filter(Position.candidate_id == c.id).all()
    d["positions"] = [
        {
            "topic": p.topic,
            "stance": p.stance,
            "source_url": p.source_url,
            "date_stated": p.date_stated.isoformat() if p.date_stated else None,
        }
        for p in positions
    ]

    # Endorsements
    endorsements = db.query(Endorsement).filter(Endorsement.candidate_id == c.id).all()
    d["endorsements"] = [
        {
            "endorser_name": e.endorser_name,
            "endorser_type": e.endorser_type,
            "source_url": e.source_url,
        }
        for e in endorsements
    ]

    return d


@router.get("/")
def list_candidates(
    jurisdiction_id: int | None = None,
    office_level: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """List candidates, with optional filters.

    Query params:
      - jurisdiction_id: filter to a specific jurisdiction
      - office_level: city | county | school_board | state
      - search: text search on name
    """
    q = db.query(Candidate)

    if search:
        pattern = f"%{search}%"
        q = q.filter(
            (Candidate.first_name.ilike(pattern))
            | (Candidate.last_name.ilike(pattern))
        )

    if jurisdiction_id or office_level:
        q = q.join(Candidacy).join(Election).join(Office)
        if jurisdiction_id:
            q = q.filter(Office.jurisdiction_id == jurisdiction_id)
        if office_level:
            q = q.filter(Office.office_level == office_level)

    candidates = q.order_by(Candidate.last_name, Candidate.first_name).all()
    return [_candidate_summary(c) for c in candidates]


@router.get("/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get full candidate profile with candidacies, positions, and endorsements."""
    c = db.query(Candidate).get(candidate_id)
    if not c:
        return {"error": "Candidate not found"}, 404
    return _candidate_detail(c, db)


@router.get("/compare")
def compare_candidates(
    ids: list[int] = Query(..., description="Candidate IDs to compare"),
    db: Session = Depends(get_db),
):
    """Side-by-side comparison of two or more candidates."""
    candidates = db.query(Candidate).filter(Candidate.id.in_(ids)).all()
    return {
        "candidates": [_candidate_detail(c, db) for c in candidates],
    }
