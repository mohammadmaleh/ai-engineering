# JWT Authentication

## Concepts

- **JWT** — a signed token that proves who you are. Backend signs it with a secret key — nobody can fake it without the key.
- **JWT structure:** `header.payload.signature`
  - **Header** — the algorithm used to sign the token (e.g. `HS256`)
  - **Payload** — user id (`sub`) and expiry (`exp`). Not encrypted — anyone can decode it. Never put passwords or sensitive data here.
  - **Signature** — proves the token wasn't tampered with. Created by signing header + payload with the secret key. The secret key never leaves the server.
- **Access token** — short-lived (60 min). User must re-login when it expires.
- **Bearer token** — sent in every request: `Authorization: Bearer <token>`
- **Password hashing** — one-way. You can never get the original password back. Use bcrypt.
- **`verify_password`** — re-hashes the input and compares to the stored hash. Never decrypt.

## Packages

```bash
pip install "python-jose[cryptography]" "passlib[bcrypt]" "bcrypt==4.0.1"
```

## File Structure

| File | What it does |
|---|---|
| `app/auth.py` | Pure utility functions — hash, verify, create token, decode token, get_current_user |
| `app/crud.py` | Database queries only — get_user_by_email, get_user_by_id, create_user |
| `app/routes/auth.py` | Endpoints — register and login. Wires auth + crud together |

## auth.py — Complete Example

```python
import os
from datetime import datetime, timedelta, timezone
from typing import cast

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set.")
SECRET_KEY = cast(str, SECRET_KEY)  # fixes type checker — python-jose has bad stubs
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # use on register


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)  # use on login — never decrypt


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore[arg-type]


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore[arg-type]
        return int(payload["sub"])
    except (JWTError, KeyError):  # JWTError = bad token, KeyError = missing "sub"
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

## crud.py — Auth Queries

```python
from sqlalchemy.orm import Session
from app.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)  # reloads user from db so you get the generated id back
    return user
```

## routes/auth.py — Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.crud import create_user, get_user_by_email
from app.database import get_db
from app.schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])
# prefix means every route here starts with /auth automatically


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db=db, email=body.email):
        raise HTTPException(400, "Email already registered")
    hashed_password = hash_password(body.password)
    return create_user(db=db, email=body.email, hashed_password=hashed_password)


@router.post("/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db=db, email=body.email)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(plain=body.password, hashed=user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
```

## Protecting a Route

```python
# In main.py or any route file:
from app.auth import get_current_user
from app.models import User
from fastapi import Depends

@app.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}
```

`Depends(get_current_user)` — FastAPI automatically calls `get_current_user` before the route runs. If it raises 401, the route never executes.

## Login Flow (step by step)

1. Frontend sends `POST /auth/login` with email + password
2. Backend finds user by email — 401 if not found
3. `verify_password(plain, user.hashed_password)` — 401 if wrong
4. `create_access_token(user.id)` — builds and signs a JWT
5. Frontend stores the token, sends it on every request: `Authorization: Bearer <token>`
6. On protected routes: `get_current_user` decodes token → gets user id → fetches user from db → passes it into the route

## SQLAlchemy 2.0 — Mapped Columns (use this, not legacy)

```python
# OLD (legacy) — type checker can't infer the Python type
id = Column(Integer, primary_key=True)

# NEW (correct) — type checker knows user.id is an int
from sqlalchemy.orm import Mapped, mapped_column

id: Mapped[int] = mapped_column(Integer, primary_key=True)
email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
```

Use `Mapped[type]` + `mapped_column()` for all new models. Fixes type errors when passing model fields to functions.

## Why bcrypt — Know This Cold

bcrypt is a **one-way hash function** — you can never reverse it.

**On register:** hash the password, store the hash. Never store plain text.
**On login:** call `verify_password(plain, stored_hash)` — it hashes the input and compares. Never decrypt.

**Why bcrypt specifically?**
1. **Automatic salting** — adds a random value before hashing so two users with the same password get different hashes. Defeats rainbow table attacks.
2. **Intentionally slow** — computationally expensive by design. Makes brute force impractical.

**Interview answer:** "bcrypt salts automatically, defeating rainbow tables, and it's slow by design, making brute force expensive."

## try/except in Python

Python uses `except`, not `catch`:

```python
try:
    result = risky_operation()
except (ValueError, KeyError):  # catch multiple exceptions with a tuple
    return None
```
