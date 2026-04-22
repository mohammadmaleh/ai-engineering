# RAG — Retrieval Augmented Generation

## PyMuPDF (fitz)

Used to extract raw text from PDF files. The package is installed as `pymupdf` but imported as `fitz` (historical name).

```python
import fitz

doc = fitz.open(stream=file_bytes, filetype="pdf")
for page in doc:
    text += str(page.get_text("text"))
doc.close()
```

## Chunking

After extracting text, we split it into smaller overlapping chunks before embedding.

**Why chunk:**
- Embedding models have a token limit — you can't embed a 50-page document as one vector
- Smaller chunks give more precise search results — a whole document as one vector can't pinpoint which section answered the question
- Overlap between chunks ensures context isn't lost at boundaries — the model can follow meaning across chunks

```python
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

while start < len(text):
    chunks.append(text[start : start + CHUNK_SIZE])
    start += CHUNK_SIZE - CHUNK_OVERLAP
```

## Embeddings

An embedding is an **array of numbers** (a vector) that represents the *meaning* of text.

Example: `[0.23, -0.81, 0.44, ...]` — 1536 numbers for `text-embedding-3-small`.

We use OpenAI to embed each chunk:
```python
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=chunks,
)
```

## Pinecone

A managed vector database. Stores vectors and lets you search by meaning (semantic search), not by exact text match.

We store each vector alongside the original chunk text in metadata:
```python
{
    "id": "1-0-abc123",
    "values": [0.23, -0.81, ...],  # the vector
    "metadata": {
        "doc_id": 1,
        "chunk_index": 0,
        "text": "the original chunk text"  # needed to return to the LLM
    }
}
```

**Why store text in metadata:** Pinecone finds the most similar vectors but only returns the vector and metadata — not the original text unless you stored it. Without `text` in metadata, you'd know *which* chunk matched but not *what it says*.

## Full Upload Flow

```
User uploads PDF
    → FastAPI reads file bytes
    → PyMuPDF extracts raw text
    → chunk_text() splits into 500-char overlapping chunks
    → OpenAI embeds all chunks → arrays of 1536 numbers
    → Pinecone stores vectors + chunk text in metadata
    → PostgreSQL stores filename + full text + status
    → Return document record to user
```

Two databases working together:
- **PostgreSQL** — document metadata, full text, user ownership
- **Pinecone** — vectors + chunk text for semantic search (used in chat/RAG)
