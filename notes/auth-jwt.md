# JWT Authentication

## Concepts

- **JWT** — a signed token that proves who you are. Backend signs it with a secret key — nobody can fake it without the key.
- **JWT structure:** `header.payload.signature` — payload contains user id and expiry
- **Access token** — short-lived (60 min). User must re-login when it expires.
- **Bearer token** — sent in every request: `Authorization: Bearer <token>`
- **Password hashing** — one-way. You can never get the original password back. Use bcrypt.
- **`verify_password`** — re-hashes the input and compares internally. Never decrypt.

## Packages

```bash
pip install "python-jose[cryptography]" "passlib[bcrypt]" "bcrypt==4.0.1"
```

## auth.py — Core Functions

```python
from passlib.context import CryptContext
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)          # use on register

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)   # use on login

def create_access_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": ...}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> int | None:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return int(payload["sub"])
```

## Auth Routes

```python
# Register
@app.post("/auth/register", status_code=201)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

# Login
@app.post("/auth/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
```

## Protecting Routes

```python
bearer_scheme = HTTPBearer()

def get_current_user(credentials = Depends(bearer_scheme), db = Depends(get_db)):
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(401, "Invalid or expired token")
    return db.query(User).filter(User.id == user_id).first()

# Add to any protected route:
async def list_documents(current_user: User = Depends(get_current_user), ...):
```

## Login Flow (step by step)

1. User sends email + password to `POST /auth/login`
2. Find user by email — 401 if not found
3. `verify_password(plain, hashed)` — 401 if wrong
4. `create_access_token(user.id)` — returns signed JWT
5. Frontend stores token, sends it in `Authorization: Bearer <token>` header on every request
6. `get_current_user` decodes token → gets user id → returns user

## Why bcrypt — Know This Cold

bcrypt is the library we use to hash passwords. It is a **one-way function** — you can never reverse it to get the original password back.

**On register:** hash the password, store the hash. Never store the plain text.

**On login:** hash the input again and compare using `verify_password`. We never decrypt — we just hash and compare.

**Why bcrypt specifically, not just any hash function?**

Two reasons:

1. **Automatic salting** — bcrypt adds a random value (salt) to each password before hashing. This means two users with the password `"123456"` will have completely different hashes in your database. Without salt, attackers use **rainbow tables** — precomputed lists of hash → password — and can crack thousands of passwords instantly. Salt defeats that.

2. **Intentionally slow** — bcrypt is designed to be computationally expensive. Brute-forcing millions of guesses becomes impractical.

**Interview answer:** "We use bcrypt because it salts automatically, which defeats rainbow table attacks, and it's slow by design, which makes brute force expensive."
