"""API routes for jurisdictions (cities, counties, school districts)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from politibase.db.database import get_db
from politibase.models.schema import Jurisdiction, Office

router = APIRouter()


@router.get("/")
def list_jurisdictions(
    jurisdiction_type: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    """List all jurisdictions, optionally filtered by type and state."""
    q = db.query(Jurisdiction)
    if jurisdiction_type:
        q = q.filter(Jurisdiction.jurisdiction_type == jurisdiction_type)
    if state:
        q = q.filter(Jurisdiction.state == state.upper())
    rows = q.order_by(Jurisdiction.name).all()
    return [
        {
            "id": j.id,
            "name": j.name,
            "type": j.jurisdiction_type,
            "state": j.state,
            "parent_id": j.parent_id,
        }
        for j in rows
    ]


@router.get("/{jurisdiction_id}")
def get_jurisdiction(jurisdiction_id: int, db: Session = Depends(get_db)):
    """Get a single jurisdiction with its offices."""
    j = db.query(Jurisdiction).get(jurisdiction_id)
    if not j:
        return {"error": "Not found"}, 404
    offices = db.query(Office).filter(Office.jurisdiction_id == j.id).order_by(Office.title).all()
    return {
        "id": j.id,
        "name": j.name,
        "type": j.jurisdiction_type,
        "state": j.state,
        "parent_id": j.parent_id,
        "offices": [
            {
                "id": o.id,
                "title": o.title,
                "level": o.office_level,
                "district": o.district,
                "seats": o.seats,
                "term_length_years": o.term_length_years,
                "is_partisan": o.is_partisan,
            }
            for o in offices
        ],
    }
