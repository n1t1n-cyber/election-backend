from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, User
from schemas import UserResponse, MessageResponse
from auth import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get all registered users (Admin only)."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/make-admin", response_model=MessageResponse)
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Grant admin privileges to a user (Admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True
    db.commit()
    return {"message": f"User '{user.name}' is now an admin."}


@router.put("/users/{user_id}/toggle-active", response_model=MessageResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Enable or disable a user account (Admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")

    user.is_active = not user.is_active
    db.commit()
    status = "enabled" if user.is_active else "disabled"
    return {"message": f"User '{user.name}' has been {status}."}


@router.post("/seed-admin", response_model=MessageResponse)
def seed_first_admin(email: str, db: Session = Depends(get_db)):
    """
    Make a registered user an admin by email.
    Use this ONCE to set up your first admin.
    Disable or remove this endpoint in production!
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Register first.")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="User must verify email first.")

    user.is_admin = True
    db.commit()
    return {"message": f"✅ '{user.name}' is now an admin!"}
