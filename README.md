# 🗳️ Online Voting System — FastAPI + SQLite

A full-featured voting system backend with email verification, JWT auth, and role-based access.

---

## 📁 Project Structure

```
voting-system/
├── main.py              # FastAPI app entry point
├── database.py          # SQLAlchemy models & DB setup
├── config.py            # Settings (SMTP, JWT, etc.)
├── auth.py              # JWT auth helpers & dependencies
├── schemas.py           # Pydantic request/response models
├── email_utils.py       # Email sending functions
├── requirements.txt
├── .env.example         # Copy to .env and configure
└── routers/
    ├── auth_router.py       # Register, login, verify email
    ├── elections_router.py  # Create/manage elections & candidates
    ├── votes_router.py      # Cast votes & view results
    └── admin_router.py      # Admin user management
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure email (Gmail recommended)
```bash
cp .env.example .env
```
Edit `.env` with your Gmail credentials.

> **Gmail App Password Setup:**
> 1. Enable 2-Step Verification on your Google Account
> 2. Go to: Google Account → Security → App Passwords
> 3. Generate a password for "Mail"
> 4. Paste the 16-character password into `SMTP_PASSWORD`

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Open API docs
Visit: **http://localhost:8000/docs**

---

## 🔐 Auth Flow

```
Register (/auth/register)
    ↓
Email sent with verification link
    ↓
Click link (/auth/verify-email?token=...)
    ↓
Login (/auth/login) → get JWT token
    ↓
Use token in Authorization: Bearer <token>
```

---

## 👑 Setup First Admin

1. Register a user normally
2. Verify their email
3. Call: `POST /admin/seed-admin?email=your@email.com`
4. **Remove this endpoint** from `admin_router.py` in production!

---

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| GET | `/auth/verify-email?token=...` | Verify email |
| POST | `/auth/login` | Login → get token |
| POST | `/auth/resend-verification` | Resend verification email |
| GET | `/auth/me` | Get current user info |

### Elections (Admin to create, all verified users to view)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/elections/` | Create election (Admin) |
| GET | `/elections/` | List all elections |
| GET | `/elections/active` | List active elections |
| GET | `/elections/{id}` | Get election details |
| PUT | `/elections/{id}/deactivate` | Deactivate (Admin) |
| DELETE | `/elections/{id}` | Delete election (Admin) |
| POST | `/elections/{id}/candidates` | Add candidate (Admin) |
| GET | `/elections/{id}/candidates` | List candidates |

### Voting
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/votes/{election_id}` | Cast a vote |
| GET | `/votes/{election_id}/results` | View results |
| GET | `/votes/{election_id}/my-vote` | Check if you voted |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List all users |
| PUT | `/admin/users/{id}/make-admin` | Grant admin |
| PUT | `/admin/users/{id}/toggle-active` | Enable/disable user |
| POST | `/admin/seed-admin` | Make first admin |

---

## 🛡️ Security Features
- Passwords hashed with **bcrypt**
- JWT tokens expire in **24 hours**
- Email must be **verified** before login works
- **One vote per user** per election enforced at DB level
- Election time windows enforced (**start/end time** validation)
