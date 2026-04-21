# PostgreSQL + SQLAlchemy

## SQL Fundamentals

```sql
SELECT * FROM documents;                          -- get all rows
SELECT id, title FROM documents;                  -- specific columns
SELECT * FROM documents WHERE user_id = 5;        -- filter
INSERT INTO documents (title, user_id) VALUES ('Lab Report', 5);
UPDATE documents SET content = 'new' WHERE id = 1;
DELETE FROM documents WHERE id = 1;
```

### JOIN

Merges two tables on a shared column.

```sql
-- INNER JOIN — only rows with a match in both tables
SELECT documents.title, users.email
FROM documents
JOIN users ON documents.user_id = users.id;

-- LEFT JOIN — all rows from left table, NULL if no match on right
SELECT documents.title, users.email
FROM documents
LEFT JOIN users ON documents.user_id = users.id;
```

### N+1 Problem

Loading a list then querying inside a loop = N+1 database hits.

```python
# BAD — 1 + N queries
docs = db.query(Document).all()
for doc in docs:
    user = db.query(User).filter(User.id == doc.user_id).first()

# GOOD — 1 query with JOIN
```

- Fix: always use JOIN instead of querying inside a loop
- Interview question: "What is N+1 and how do you fix it?"

---

## The 3-File Pattern

Every FastAPI + database project uses this structure:

```
database.py   ← connection setup (engine, session, Base)
models.py     ← database tables as Python classes (SQLAlchemy)
schemas.py    ← API input/output shapes (Pydantic)
main.py       ← routes that use all of the above
```

- **models.py** talks to the database
- **schemas.py** talks to the outside world (API)
- They look similar but serve different purposes — never mix them

## database.py — Connection Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(DATABASE_URL)        # the connection to PostgreSQL
SessionLocal = sessionmaker(bind=engine)    # factory that creates sessions
Base = declarative_base()                   # parent class for all models

def get_db():
    db = SessionLocal()   # open session
    try:
        yield db          # give it to the route handler
    finally:
        db.close()        # close when request is done
```

- **engine** — the phone line to PostgreSQL. Created once, reused forever.
- **session** — one conversation over that line. One per request.
- **Base** — shared parent class. `class Document(Base)` = this is a table.
- **`yield`** — pauses the function, gives `db` to the route, closes it after.

## models.py — Database Tables

> ⭐ MEMORIZE: how to define a model, a foreign key, and a relationship

```python
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
```

- `String` — short text (name, title, email — under ~255 chars)
- `Text` — long text with no length limit (document content, descriptions)
- `index=True` — makes lookups by that column fast (always index primary key + columns you filter by)
- `nullable=False` — same as `NOT NULL` in SQL

## schemas.py — API Shapes (Pydantic)

```python
from pydantic import BaseModel

class CreateDocument(BaseModel):    # request body shape
    title: str
    content: str

class DocumentResponse(BaseModel):  # response shape
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True      # lets Pydantic read SQLAlchemy objects
```

- `CreateDocument` — what the API accepts (IN)
- `DocumentResponse` — what the API returns (OUT)
- `from_attributes = True` — required when returning SQLAlchemy objects as Pydantic

## main.py — Routes with Database

```python
# inject db session into every route that needs it
async def list_documents(db: Session = Depends(get_db)):
```

- `Depends(get_db)` — FastAPI calls `get_db()` and injects the session automatically
- Every route that touches the database needs `db: Session = Depends(get_db)`

## SQLAlchemy CRUD Operations

```python
# READ all
db.query(Document).all()

# READ with filter
db.query(Document).filter(Document.id == id).first()

# SEARCH (case-insensitive)
db.query(Document).filter(Document.title.ilike(f"%{search}%")).all()

# CREATE
doc = Document(title="hello", content="world")
db.add(doc)
db.commit()
db.refresh(doc)   # reload from DB to get the generated id
return doc

# DELETE
db.delete(doc)
db.commit()
```

- `.all()` — executes query, returns list
- `.first()` — executes query, returns one or None
- `ilike` — case-insensitive search (`like` is case-sensitive)
- `db.refresh(doc)` — after commit, reload the object to get auto-generated fields (like id)

## Create Tables on Startup

```python
# in main.py — runs once when app starts
Base.metadata.create_all(bind=engine)
```

- Creates all tables defined in models.py if they don't exist yet
- Safe to run every startup — skips tables that already exist

## Alembic — Migrations

Like git for your database schema. Change models.py → generate migration → apply it.

```bash
# ⭐ MEMORIZE THESE 4
alembic init alembic                                        # run once to set up
alembic revision --autogenerate -m "add status column"     # generate migration from models
alembic upgrade head                                        # apply migration to DB
alembic downgrade -1                                        # rollback one step
```

Setup required in two files:

- `alembic.ini` — set `sqlalchemy.url` to your database URL
- `alembic/env.py` — import `Base` and `models`, set `target_metadata = Base.metadata`

Every migration file has:

- `upgrade()` — what to do when applying
- `downgrade()` — how to undo it

- Rule: every schema change = new migration. Never edit an already-applied migration.

## Connection String Format

```
postgresql://user:password@localhost:5432/database_name
```

Always store in `.env`, never hardcode.

## How to Plan a Database

Ask these questions in order:

**1. What are the nouns in the app?**
Each noun is usually a table. In MedDocs: User, Document, ChatSession, ChatMessage.

**2. Who owns what? (→ foreign keys)**

- A document belongs to a user → `user_id` on `documents`
- A chat session belongs to a user and a document → `user_id` + `document_id` on `chat_sessions`
- A message belongs to a session → `session_id` on `chat_messages`

**3. What do I need to display on each screen? (→ columns)**
Look at every screen in the app. The document list page shows: filename, status, flagged keywords, date.
That tells you exactly what columns `documents` needs.

**4. Which fields must never be empty? (→ nullable=False)**
`email`, `hashed_password`, `filename` — the app breaks without them. Mark them `nullable=False`.

**5. Which fields are lists? (→ JSON)**
`flagged_keywords` is a list of strings → `Column(JSON, default=list)`

**6. Which tables need shortcuts to related data? (→ relationships)**
Relationships are Python-only shortcuts — they don't add columns to the DB.
They sit on top of foreign keys and let you write `doc.user` instead of a manual query.

```python
# On Document — "give me the user who owns this document"
user = relationship("User", back_populates="documents")

# On User — "give me all documents this user owns"
documents = relationship("Document", back_populates="user")
```

`back_populates` links the two sides together. The value must match the attribute name on the other class.
Without it, SQLAlchemy treats them as two unrelated relationships — bugs follow.

## schemas.py — Request & Response Shapes (Pydantic v2)

Schemas define what the API accepts (IN) and returns (OUT). They talk to the outside world — not the database.

- **Request schema** — what the frontend sends. Only include fields the user provides.
- **Response schema** — what the API returns. Only expose what's safe — never `hashed_password`.

```python
from pydantic import BaseModel, ConfigDict, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr       # validated email format
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
```

**`model_config = ConfigDict(from_attributes=True)`** — required on any response schema that is built from a SQLAlchemy object. By default Pydantic only reads plain dicts. SQLAlchemy returns objects — this setting tells Pydantic to read object attributes instead.

- Request schemas never need it — they come from JSON, not the DB.
- Response schemas need it when you do `return db_user` directly from a route.

**`EmailStr`** — validates that the string is a valid email format. Requires `pip install "pydantic[email]"`.

---

## Alembic — Full Setup Guide

Alembic is git for your database schema. Every time you change `models.py`, you generate a migration and apply it.

### One-time setup (per project)

```bash
alembic init alembic
```

Then configure 2 files:

**`alembic.ini`** — set the database URL:
```ini
sqlalchemy.url = postgresql://user:password@localhost:5432/dbname
```

**`alembic/env.py`** — tell Alembic about your models:
```python
from app.models import Base
target_metadata = Base.metadata
```

Without `target_metadata`, autogenerate produces an empty migration — it doesn't know what your tables look like.

### Every time you change models.py

```bash
# ⭐ MEMORIZE THESE
alembic revision --autogenerate -m "describe what changed"   # generate migration file
alembic upgrade head                                          # apply to DB
alembic downgrade -1                                          # undo last migration
```

### What autogenerate does

It compares your SQLAlchemy models against the actual database and writes the SQL to make them match. Always open the generated file and review `upgrade()` before applying — Alembic sometimes misses things.

### Common errors

| Error | Cause | Fix |
|---|---|---|
| `Can't locate revision` | Stale migration reference in DB | `DELETE FROM alembic_version;` |
| `NotNullViolation on add_column` | Adding NOT NULL column to table with existing rows | Truncate the table or add a default value first |
| `password authentication failed` | Wrong DB password in connection string | Check `.env` and `alembic.ini` match |

### Rule
Every schema change = new migration. Never edit an already-applied migration file.

