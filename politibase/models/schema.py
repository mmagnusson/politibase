"""SQLAlchemy models for Politibase.

This schema captures the full lifecycle of local elections: jurisdictions contain
offices, offices have elections, candidates file candidacies for those elections,
and we track their positions, endorsements, finances, and (for incumbents) their
voting/meeting records.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Jurisdiction — a city, county, school district, or state
# ---------------------------------------------------------------------------

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)  # "City of Moorhead"
    jurisdiction_type = Column(
        String(64), nullable=False
    )  # city | county | school_district | state | township
    state = Column(String(2), nullable=False)  # "MN", "ND"
    parent_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=True)

    # Relationships
    parent = relationship("Jurisdiction", remote_side=[id], backref="children")
    offices = relationship("Office", back_populates="jurisdiction")

    def __repr__(self):
        return f"<Jurisdiction {self.name} ({self.jurisdiction_type}, {self.state})>"


# ---------------------------------------------------------------------------
# Office — a seat that can be held (e.g. "Ward 1 Council Member")
# ---------------------------------------------------------------------------

class Office(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    title = Column(String(256), nullable=False)  # "Mayor", "Council Member Ward 1"
    office_level = Column(
        String(64), nullable=False
    )  # city | county | school_board | state | township
    district = Column(String(64), nullable=True)  # "Ward 1", "District 3", null for at-large
    seats = Column(Integer, nullable=False, default=1)  # how many seats for this office
    term_length_years = Column(Integer, nullable=True)
    is_partisan = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)

    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="offices")
    elections = relationship("Election", back_populates="office")

    __table_args__ = (
        UniqueConstraint("jurisdiction_id", "title", name="uq_office_title_per_jurisdiction"),
    )

    def __repr__(self):
        return f"<Office {self.title} in {self.jurisdiction_id}>"


# ---------------------------------------------------------------------------
# Election — a specific election event for an office
# ---------------------------------------------------------------------------

class Election(Base):
    __tablename__ = "elections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=False)
    election_date = Column(Date, nullable=False)
    election_type = Column(
        String(32), nullable=False
    )  # general | primary | special | runoff
    filing_deadline = Column(Date, nullable=True)
    registration_deadline = Column(Date, nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    office = relationship("Office", back_populates="elections")
    candidacies = relationship("Candidacy", back_populates="election")

    def __repr__(self):
        return f"<Election {self.election_type} on {self.election_date} for office {self.office_id}>"


# ---------------------------------------------------------------------------
# Candidate — a person who runs for office
# ---------------------------------------------------------------------------

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    middle_name = Column(String(128), nullable=True)
    suffix = Column(String(16), nullable=True)  # Jr., III, etc.
    date_of_birth = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    photo_url = Column(String(512), nullable=True)
    website = Column(String(512), nullable=True)
    email = Column(String(256), nullable=True)
    phone = Column(String(32), nullable=True)
    party_affiliation = Column(String(64), nullable=True)
    occupation = Column(String(256), nullable=True)
    education = Column(Text, nullable=True)
    residence_city = Column(String(128), nullable=True)
    residence_state = Column(String(2), nullable=True)

    # Social media
    facebook_url = Column(String(512), nullable=True)
    twitter_handle = Column(String(128), nullable=True)
    linkedin_url = Column(String(512), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidacies = relationship("Candidacy", back_populates="candidate")
    positions = relationship("Position", back_populates="candidate")
    endorsements = relationship("Endorsement", back_populates="candidate")
    finance_records = relationship("FinanceRecord", back_populates="candidate")

    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)

    def __repr__(self):
        return f"<Candidate {self.first_name} {self.last_name}>"


# ---------------------------------------------------------------------------
# Candidacy — links a Candidate to an Election (they filed / ran / won)
# ---------------------------------------------------------------------------

class Candidacy(Base):
    __tablename__ = "candidacies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False)
    filing_date = Column(Date, nullable=True)
    status = Column(
        String(32), nullable=False, default="filed"
    )  # filed | withdrawn | active | winner | loser
    is_incumbent = Column(Boolean, nullable=False, default=False)
    votes_received = Column(Integer, nullable=True)
    vote_percentage = Column(Float, nullable=True)
    campaign_url = Column(String(512), nullable=True)
    campaign_slogan = Column(String(512), nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="candidacies")
    election = relationship("Election", back_populates="candidacies")

    __table_args__ = (
        UniqueConstraint("candidate_id", "election_id", name="uq_candidate_per_election"),
    )

    def __repr__(self):
        return f"<Candidacy candidate={self.candidate_id} election={self.election_id} status={self.status}>"


# ---------------------------------------------------------------------------
# Position — a candidate's stated stance on an issue
# ---------------------------------------------------------------------------

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    topic = Column(String(256), nullable=False)  # "School Funding", "Property Tax"
    stance = Column(Text, nullable=False)  # free-text description
    source_url = Column(String(512), nullable=True)
    source_name = Column(String(256), nullable=True)
    date_stated = Column(Date, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="positions")

    def __repr__(self):
        return f"<Position {self.candidate_id} on {self.topic}>"


# ---------------------------------------------------------------------------
# Endorsement — an organization or person endorsing a candidate
# ---------------------------------------------------------------------------

class Endorsement(Base):
    __tablename__ = "endorsements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    endorser_name = Column(String(256), nullable=False)
    endorser_type = Column(
        String(64), nullable=True
    )  # organization | newspaper | individual | union | party
    source_url = Column(String(512), nullable=True)
    date_endorsed = Column(Date, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="endorsements")

    def __repr__(self):
        return f"<Endorsement {self.endorser_name} -> candidate {self.candidate_id}>"


# ---------------------------------------------------------------------------
# FinanceRecord — campaign contributions / expenditures
# ---------------------------------------------------------------------------

class FinanceRecord(Base):
    __tablename__ = "finance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    record_type = Column(
        String(32), nullable=False
    )  # contribution | expenditure | total_raised | total_spent
    amount = Column(Float, nullable=False)
    donor_name = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    date_recorded = Column(Date, nullable=True)
    reporting_period = Column(String(64), nullable=True)
    source_url = Column(String(512), nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="finance_records")

    def __repr__(self):
        return f"<FinanceRecord {self.record_type} ${self.amount} for candidate {self.candidate_id}>"


# ---------------------------------------------------------------------------
# MeetingRecord — for incumbents: attendance and votes at public meetings
# ---------------------------------------------------------------------------

class MeetingRecord(Base):
    __tablename__ = "meeting_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_type = Column(String(128), nullable=True)  # "Regular Meeting", "Special Session"
    was_present = Column(Boolean, nullable=True)
    agenda_item = Column(Text, nullable=True)
    vote_cast = Column(String(32), nullable=True)  # yes | no | abstain | absent
    minutes_url = Column(String(512), nullable=True)

    # Relationships
    candidate = relationship("Candidate")
    jurisdiction = relationship("Jurisdiction")

    def __repr__(self):
        return f"<MeetingRecord {self.meeting_date} candidate={self.candidate_id}>"


# ---------------------------------------------------------------------------
# OfficeTerm — who currently holds (or recently held) an office
# ---------------------------------------------------------------------------

class OfficeTerm(Base):
    __tablename__ = "office_terms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    term_start = Column(Date, nullable=True)
    term_end = Column(Date, nullable=True)
    is_term_limited = Column(Boolean, nullable=False, default=False)
    appointment_type = Column(
        String(32), nullable=False, default="elected"
    )  # elected | appointed
    status = Column(
        String(32), nullable=False, default="serving"
    )  # serving | resigned | recalled | term_expired

    # Relationships
    office = relationship("Office", backref="terms")
    candidate = relationship("Candidate", backref="office_terms")

    def __repr__(self):
        return f"<OfficeTerm office={self.office_id} candidate={self.candidate_id} status={self.status}>"


# ---------------------------------------------------------------------------
# DataSource — provenance tracking for all imported data
# ---------------------------------------------------------------------------

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(256), nullable=False)  # "City of Moorhead Website"
    source_url = Column(String(512), nullable=True)
    source_type = Column(
        String(64), nullable=False
    )  # official | news | campaign | community | api
    last_scraped_at = Column(DateTime, nullable=True)
    record_table = Column(String(128), nullable=True)  # which table this source feeds
    record_id = Column(Integer, nullable=True)  # which row
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<DataSource {self.source_name}>"
