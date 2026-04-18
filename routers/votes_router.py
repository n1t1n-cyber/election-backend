from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, Vote, Election, Candidate, User
from schemas import VoteCreate, VoteResponse, ElectionResults, CandidateWithVotes
from auth import get_current_user

router = APIRouter(prefix="/votes", tags=["Voting"])


@router.post("/{election_id}", response_model=VoteResponse, status_code=201)
def cast_vote(
    election_id: int,
    vote_data: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cast a vote in an election. Each user can only vote once per election."""
    # Check election exists and is active
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    now = datetime.utcnow()
    if not election.is_active:
        raise HTTPException(status_code=400, detail="This election is not active")
    if now < election.start_time:
        raise HTTPException(status_code=400, detail=f"Election starts at {election.start_time}")
    if now > election.end_time:
        raise HTTPException(status_code=400, detail="Election has ended")

    # Check candidate belongs to this election
    candidate = db.query(Candidate).filter(
        Candidate.id == vote_data.candidate_id,
        Candidate.election_id == election_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found in this election")

    # Check if user already voted in this election
    existing_vote = db.query(Vote).filter(
        Vote.voter_id == current_user.id,
        Vote.election_id == election_id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted in this election")

    # Cast the vote
    vote = Vote(
        voter_id=current_user.id,
        candidate_id=vote_data.candidate_id,
        election_id=election_id
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


@router.get("/{election_id}/results", response_model=ElectionResults)
def get_results(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live results for an election."""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    candidates = db.query(Candidate).filter(Candidate.election_id == election_id).all()
    total_votes = db.query(Vote).filter(Vote.election_id == election_id).count()

    candidate_results = []
    for candidate in candidates:
        vote_count = db.query(Vote).filter(Vote.candidate_id == candidate.id).count()
        candidate_results.append(CandidateWithVotes(
            id=candidate.id,
            name=candidate.name,
            description=candidate.description,
            party=candidate.party,
            vote_count=vote_count
        ))

    # Sort by votes descending
    candidate_results.sort(key=lambda x: x.vote_count, reverse=True)

    return ElectionResults(
        election_id=election.id,
        election_title=election.title,
        total_votes=total_votes,
        candidates=candidate_results,
        is_active=election.is_active
    )


@router.get("/{election_id}/my-vote", response_model=dict)
def check_my_vote(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user has voted in an election."""
    vote = db.query(Vote).filter(
        Vote.voter_id == current_user.id,
        Vote.election_id == election_id
    ).first()

    if not vote:
        return {"has_voted": False, "candidate_id": None, "voted_at": None}

    candidate = db.query(Candidate).filter(Candidate.id == vote.candidate_id).first()
    return {
        "has_voted": True,
        "candidate_id": vote.candidate_id,
        "candidate_name": candidate.name if candidate else None,
        "voted_at": vote.voted_at
    }
