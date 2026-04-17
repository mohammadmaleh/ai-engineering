from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

documents = {}
next_id = 1


class CreateDocument(BaseModel):
    title: str
    content: str


@app.get("/documents")
async def list_documents(search: str = None):
    all_docs = list(documents.values())
    if search:
        return [d for d in all_docs if search.lower() in d["title"].lower()]
    return all_docs


@app.post("/documents", status_code=201)
async def create_document(body: CreateDocument):
    global next_id
    doc = {"id": next_id, "title": body.title, "content": body.content}
    documents[next_id] = doc
    next_id += 1
    return doc


@app.delete("/documents/{id}", status_code=204)
async def delete_document(id: int):
    if id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents[id]
