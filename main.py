from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth_router, elections_router, votes_router, admin_router

app = FastAPI(
    title="🗳️ Online Voting System",
    description="""
## Online Voting System API

A secure backend for managing elections, candidates, and votes with email verification.

### Features
- 📧 **Email Verification** — users must verify their email before voting
- 🔐 **JWT Authentication** — secure token-based login
- 🗳️ **One Vote Per User** — each verified user can vote once per election
- 📊 **Live Results** — real-time vote counts per candidate
- 👑 **Admin Controls** — manage elections, candidates, and users
- 🛡️ **SQLite Database** — lightweight, no setup needed

### Flow
1. Register → receive verification email
2. Verify email → account activated
3. Login → get JWT token
4. Browse elections → cast vote → view results
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


import os

# CORS — allow all origins for development (restrict in production)
origins = [
    "http://localhost:8080",
    "http://localhost:5173", # Default Vite port
    os.getenv("FRONTEND_URL", ""),
]

# Filter out empty strings
origins = [o for o in origins if o]

# CORS — allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], # Add your Vite port here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")
    print("📚 API Docs: http://localhost:8000/docs")

# Include routers
app.include_router(auth_router.router)
app.include_router(elections_router.router)
app.include_router(votes_router.router)
app.include_router(admin_router.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": "🗳️ Online Voting System",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
