# FastAPI

## Setup

FastAPI for routes, uvicorn as the server (like nodemon).

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

- `/docs` — auto-generated API explorer, test every endpoint here

## Creating an App

```python
from fastapi import FastAPI

app = FastAPI()
```

## Routes

Like `app.get()` in Express but with decorators.

```python
@app.get("/documents")
async def list_documents():
    return []

@app.post("/documents", status_code=201)
async def create_document():
    ...

@app.delete("/documents/{id}", status_code=204)
async def delete_document(id: int):
    ...
```

- `{id}` in the path = path param, FastAPI passes it as a function argument
- Always `async def` for route handlers

## Pydantic — Request Body Validation

Like a Zod schema. Defines and validates the shape of incoming JSON.

```python
from pydantic import BaseModel

class CreateDocument(BaseModel):
    title: str
    content: str

@app.post("/documents", status_code=201)
async def create_document(body: CreateDocument):
    print(body.title)    # validated, typed
    print(body.content)
```

- If `title` is missing → FastAPI returns 422 automatically
- `BaseModel` is Pydantic's base class — every schema extends it

## Raising Errors

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Document not found")
```

- Like `res.status(404).json(...)` in Express

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK (default) |
| 201 | Created |
| 204 | No content (delete success) |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 422 | Validation error (Pydantic rejected the body) |
| 500 | Server error |

## Global Variables

```python
next_id = 1

def create_document():
    global next_id      # required to modify a variable defined outside the function
    next_id += 1
```

## Dict as Temporary Storage (no database yet)

```python
documents = {}

documents[1] = {"id": 1, "title": "hello"}   # store
documents[1]                                   # get by id
list(documents.values())                       # get all as list
del documents[1]                               # delete
1 in documents                                 # check if key exists
```

- `documents.values()` returns a dict_values object — wrap in `list()` to return as JSON

## CORS

Required so your frontend (Next.js on port 3000) can call the API (port 8000).

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- Never use `allow_origins=["*"]` in production — allows any website to call your API

## Env Vars

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file in the same folder as main.py

SECRET = os.getenv("SECRET")
if not SECRET:
    raise RuntimeError("SECRET is not set. Add it to your .env file.")
```

- Crash loudly on startup if a required env var is missing — never fail silently
- Always add `.env` to `.gitignore`
