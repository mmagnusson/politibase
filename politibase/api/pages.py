"""Server-rendered page routes (HTML views).

These serve the Jinja2-rendered frontend pages, separate from the JSON API routes.
"""

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from politibase.db.database import get_db
from politibase.models.schema import (
    Candidate,
    Candidacy,
    Election,
    Endorsement,
    Jurisdiction,
    Office,
    OfficeTerm,
    Position,
)

router = APIRouter()
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
templates = Jinja2Templates(directory=str(_frontend_dir / "templates"))


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    jurisdictions = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.jurisdiction_type != "state")
        .order_by(Jurisdiction.name)
        .all()
    )
    jur_data = []
    for j in jurisdictions:
        office_count = db.query(Office).filter(Office.jurisdiction_id == j.id).count()
        jur_data.append(
            {
                "id": j.id,
                "name": j.name,
                "jurisdiction_type": j.jurisdiction_type,
                "state": j.state,
                "office_count": office_count,
            }
        )

    upcoming = (
        db.query(Election)
        .join(Office)
        .filter(Election.election_date >= date.today())
        .order_by(Election.election_date)
        .all()
    )
    upcoming_data = [
        {
            "election_date": e.election_date.isoformat(),
            "office_title": e.office.title,
            "election_type": e.election_type,
            "filing_deadline": e.filing_deadline.isoformat() if e.filing_deadline else None,
            "description": e.description,
        }
        for e in upcoming
    ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jurisdictions": jur_data,
            "upcoming_elections": upcoming_data,
        },
    )


@router.get("/candidates", response_class=HTMLResponse)
def candidates_page(request: Request, db: Session = Depends(get_db)):
    jurisdictions = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.jurisdiction_type != "state")
        .order_by(Jurisdiction.name)
        .all()
    )
    jur_data = [
        {"id": j.id, "name": j.name, "jurisdiction_type": j.jurisdiction_type}
        for j in jurisdictions
    ]
    return templates.TemplateResponse(
        "candidates.html", {"request": request, "jurisdictions": jur_data}
    )


@router.get("/candidate/{candidate_id}", response_class=HTMLResponse)
def candidate_detail_page(candidate_id: int, request: Request, db: Session = Depends(get_db)):
    c = db.query(Candidate).get(candidate_id)
    if not c:
        return HTMLResponse("<h1>Candidate not found</h1>", status_code=404)

    # Build full candidate data
    candidacies = (
        db.query(Candidacy)
        .filter(Candidacy.candidate_id == c.id)
        .join(Election)
        .join(Office)
        .order_by(Election.election_date.desc())
        .all()
    )
    positions = db.query(Position).filter(Position.candidate_id == c.id).all()
    endorsements = db.query(Endorsement).filter(Endorsement.candidate_id == c.id).all()

    candidate_data = {
        "id": c.id,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "full_name": c.full_name,
        "bio": c.bio,
        "education": c.education,
        "occupation": c.occupation,
        "party_affiliation": c.party_affiliation,
        "residence_city": c.residence_city,
        "residence_state": c.residence_state,
        "website": c.website,
        "email": c.email,
        "phone": c.phone,
        "photo_url": c.photo_url,
        "facebook_url": c.facebook_url,
        "twitter_handle": c.twitter_handle,
        "linkedin_url": c.linkedin_url,
        "candidacies": [
            {
                "election_date": cy.election.election_date.isoformat(),
                "election_type": cy.election.election_type,
                "office_title": cy.election.office.title,
                "status": cy.status,
                "is_incumbent": cy.is_incumbent,
                "votes_received": cy.votes_received,
                "vote_percentage": cy.vote_percentage,
            }
            for cy in candidacies
        ],
        "positions": [
            {
                "topic": p.topic,
                "stance": p.stance,
                "source_url": p.source_url,
                "date_stated": p.date_stated.isoformat() if p.date_stated else None,
            }
            for p in positions
        ],
        "endorsements": [
            {
                "endorser_name": e.endorser_name,
                "endorser_type": e.endorser_type,
                "source_url": e.source_url,
            }
            for e in endorsements
        ],
    }

    return templates.TemplateResponse(
        "candidate_detail.html", {"request": request, "candidate": candidate_data}
    )


@router.get("/elections", response_class=HTMLResponse)
def elections_page(request: Request, db: Session = Depends(get_db)):
    all_elections = (
        db.query(Election).join(Office).order_by(Election.election_date.desc()).all()
    )
    today = date.today()

    def election_dict(e):
        return {
            "id": e.id,
            "election_date": e.election_date.isoformat(),
            "office_title": e.office.title,
            "election_type": e.election_type,
            "filing_deadline": e.filing_deadline.isoformat() if e.filing_deadline else None,
            "description": e.description,
        }

    upcoming = [election_dict(e) for e in all_elections if e.election_date >= today]
    past = [election_dict(e) for e in all_elections if e.election_date < today]

    return templates.TemplateResponse(
        "elections.html", {"request": request, "upcoming": upcoming, "past": past}
    )


@router.get("/elections/{election_id}", response_class=HTMLResponse)
def election_detail_page(election_id: int, request: Request, db: Session = Depends(get_db)):
    e = db.query(Election).get(election_id)
    if not e:
        return HTMLResponse("<h1>Election not found</h1>", status_code=404)

    candidacies = (
        db.query(Candidacy)
        .filter(Candidacy.election_id == e.id)
        .join(Candidate)
        .order_by(Candidate.last_name)
        .all()
    )

    election_data = {
        "id": e.id,
        "election_date": e.election_date.isoformat(),
        "office_title": e.office.title,
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
                "occupation": cy.candidate.occupation,
            }
            for cy in candidacies
        ],
    }

    return templates.TemplateResponse(
        "election_detail.html", {"request": request, "election": election_data}
    )


@router.get("/jurisdictions", response_class=HTMLResponse)
def jurisdictions_page(request: Request, db: Session = Depends(get_db)):
    jurisdictions = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.jurisdiction_type != "state")
        .order_by(Jurisdiction.name)
        .all()
    )
    jur_data = [
        {"id": j.id, "name": j.name, "type": j.jurisdiction_type, "state": j.state}
        for j in jurisdictions
    ]
    return templates.TemplateResponse(
        "jurisdictions.html", {"request": request, "jurisdictions": jur_data}
    )


@router.get("/jurisdictions/{jurisdiction_id}", response_class=HTMLResponse)
def jurisdiction_detail_page(
    jurisdiction_id: int, request: Request, db: Session = Depends(get_db)
):
    j = db.query(Jurisdiction).get(jurisdiction_id)
    if not j:
        return HTMLResponse("<h1>Jurisdiction not found</h1>", status_code=404)

    offices = db.query(Office).filter(Office.jurisdiction_id == j.id).order_by(Office.title).all()
    office_data = []
    for o in offices:
        terms = (
            db.query(OfficeTerm)
            .filter(OfficeTerm.office_id == o.id, OfficeTerm.status == "serving")
            .join(Candidate)
            .all()
        )
        current_holders = [
            {
                "id": t.candidate.id,
                "name": t.candidate.full_name,
                "is_term_limited": t.is_term_limited,
                "term_end": t.term_end.isoformat() if t.term_end else None,
            }
            for t in terms
        ]

        office_data.append(
            {
                "title": o.title,
                "district": o.district,
                "term_length_years": o.term_length_years,
                "is_partisan": o.is_partisan,
                "current_holders": current_holders,
            }
        )

    jur_data = {
        "id": j.id,
        "name": j.name,
        "type": j.jurisdiction_type,
        "state": j.state,
        "offices": office_data,
    }

    return templates.TemplateResponse(
        "jurisdiction_detail.html", {"request": request, "jurisdiction": jur_data}
    )


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
