import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Document
from schemas import CreateDocument, DocumentResponse

load_dotenv()

APP_SECRET = os.getenv("APP_SECRET")
if not APP_SECRET:
    raise RuntimeError("APP_SECRET is not set. Add it to your .env file.")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/documents", response_model=list[DocumentResponse])
async def list_documents(search: str = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))
    return query.all()


@app.get("/documents/{id}", response_model=DocumentResponse)
async def get_document(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(body: CreateDocument, db: Session = Depends(get_db)):
    doc = Document(title=body.title, content=body.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@app.delete("/documents/{id}", status_code=204)
async def delete_document(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
