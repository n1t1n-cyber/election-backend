from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db, Election, Candidate, User
from schemas import ElectionCreate, ElectionResponse, CandidateCreate, CandidateResponse, MessageResponse
from auth import get_current_user, get_admin_user

router = APIRouter(prefix="/elections", tags=["Elections"])


@router.post("/", response_model=ElectionResponse, status_code=201)
def create_election(
    data: ElectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Create a new election (Admin only)."""
    election = Election(
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        created_by=admin.id
    )
    db.add(election)
    db.commit()
    db.refresh(election)
    return election


@router.get("/", response_model=List[ElectionResponse])
def get_all_elections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all elections."""
    return db.query(Election).order_by(Election.created_at.desc()).all()


@router.get("/active", response_model=List[ElectionResponse])
def get_active_elections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get currently active elections."""
    now = datetime.utcnow()
    return db.query(Election).filter(
        Election.is_active == True,
        Election.start_time <= now,
        Election.end_time >= now
    ).all()


@router.get("/{election_id}", response_model=ElectionResponse)
def get_election(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific election by ID."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    return election


@router.put("/{election_id}/deactivate", response_model=MessageResponse)
def deactivate_election(
    election_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Deactivate an election (Admin only)."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    election.is_active = False
    db.commit()
    return {"message": f"Election '{election.title}' has been deactivated."}


@router.delete("/{election_id}", response_model=MessageResponse)
def delete_election(
    election_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Delete an election and all its data (Admin only)."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    db.delete(election)
    db.commit()
    return {"message": f"Election '{election.title}' deleted successfully."}


# ─── Candidates ──────────────────────────────────────────────

@router.post("/{election_id}/candidates", response_model=CandidateResponse, status_code=201)
def add_candidate(
    election_id: int,
    data: CandidateCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Add a candidate to an election (Admin only)."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    candidate = Candidate(
        name=data.name,
        description=data.description,
        party=data.party,
        election_id=election_id
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{election_id}/candidates", response_model=List[CandidateResponse])
def get_candidates(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all candidates for an election."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    return db.query(Candidate).filter(Candidate.election_id == election_id).all()


@router.delete("/{election_id}/candidates/{candidate_id}", response_model=MessageResponse)
def delete_candidate(
    election_id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Remove a candidate from an election (Admin only)."""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.election_id == election_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    return {"message": f"Candidate '{candidate.name}' removed successfully."}
