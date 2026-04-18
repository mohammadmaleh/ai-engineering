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
alembic init alembic                                        # run once to set up
alembic revision --autogenerate -m "add status column"     # generate migration
alembic upgrade head                                        # apply migration
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
