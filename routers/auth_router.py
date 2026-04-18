from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, User
from schemas import UserRegister, UserLogin, TokenResponse, UserResponse, MessageResponse
from auth import hash_password, verify_password, generate_token, create_access_token, get_current_user
from email_utils import send_verification_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user. Sends a verification email."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    verification_token = generate_token()
    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        verification_token=verification_token,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    #Send verification email in background
    background_tasks.add_task(
       send_verification_email,
       user_data.email,
       user_data.name,
       verification_token
    )

    return {"message": f"Registration successful! Please check {user_data.email} to verify your account."}


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Verify email using the token sent to user's email."""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    if user.is_verified:
        return {"message": "Email already verified. You can log in."}

    user.is_verified = True
    user.verification_token = None
    db.commit()

    background_tasks.add_task(send_welcome_email, user.email, user.name)

    return {"message": "✅ Email verified successfully! You can now log in."}


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password. Returns JWT token."""
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please check your inbox."
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        is_admin=user.is_admin
    )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend verification email if user hasn't verified yet."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if user.is_verified:
        return {"message": "Email already verified. Please log in."}

    new_token = generate_token()
    user.verification_token = new_token
    db.commit()

    background_tasks.add_task(send_verification_email, user.email, user.name, new_token)

    return {"message": "Verification email resent. Please check your inbox."}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info."""
    return current_user
