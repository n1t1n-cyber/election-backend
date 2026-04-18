from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List


# ─── Auth Schemas ───────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    is_admin: bool


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_verified: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Election Schemas ────────────────────────────────────────
class ElectionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ElectionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Candidate Schemas ───────────────────────────────────────
class CandidateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    party: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    party: Optional[str]
    election_id: int

    class Config:
        from_attributes = True


class CandidateWithVotes(BaseModel):
    id: int
    name: str
    description: Optional[str]
    party: Optional[str]
    vote_count: int

    class Config:
        from_attributes = True


# ─── Vote Schemas ────────────────────────────────────────────
class VoteCreate(BaseModel):
    candidate_id: int


class VoteResponse(BaseModel):
    id: int
    voter_id: int
    candidate_id: int
    election_id: int
    voted_at: datetime

    class Config:
        from_attributes = True


# ─── Results Schema ──────────────────────────────────────────
class ElectionResults(BaseModel):
    election_id: int
    election_title: str
    total_votes: int
    candidates: List[CandidateWithVotes]
    is_active: bool


class MessageResponse(BaseModel):
    message: str
