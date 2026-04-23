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

---

## RAG Chat Pipeline (ENG-7)

When a user sends a message, this is what happens in order:

```
1. Embed the question → vector
2. Query Pinecone (filter by user_id) → top 5 relevant chunks
3. Build prompt: system message with chunks + user message
4. Call Groq with stream=True → yield tokens one by one
5. Save user message to DB
6. Save full assistant reply to DB after stream ends
```

### Why always search Pinecone (not let the model decide)

This is NOT an agent. We always search, every time. The model doesn't decide when to look things up — we always inject context. Simpler, more reliable, easier to test.

### Why filter by user_id not doc_id

Sessions are not tied to a single document. A user can ask about anything across all their uploaded documents. Pinecone filters by `user_id` so we only search that user's vectors.

### Embedding the question

You can't query Pinecone with raw text. Pinecone only understands vectors. So you must embed the question first:

```python
response = openai_client.embeddings.create(model="text-embedding-3-small", input=[content])
embedding = response.data[0].embedding  # list of 1536 floats
```

### Querying Pinecone

```python
results = pinecone_index.query(
    vector=embedding,
    top_k=5,
    include_metadata=True,
    filter={"user_id": user_id},
)
chunks = [match["metadata"]["text"] for match in results["matches"]]
```

`top_k=5` means return the 5 most similar chunks. The text is in `metadata["text"]` — you stored it there during upload.

### Building the prompt

```python
context = "\n\n".join(chunks)
messages = [
    {
        "role": "system",
        "content": (
            "You are a medical document assistant. "
            "Answer only from the document excerpts below. "
            "If the answer is not in the excerpts, say so.\n\n"
            f"Document excerpts:\n{context}"
        ),
    },
    {"role": "user", "content": content},
]
```

### SSE Streaming with yield

`yield` makes a function a **generator** — it produces values one at a time instead of returning everything at once. FastAPI's `StreamingResponse` needs a generator.

```python
async def handle_message(...):
    stream = groq_client.chat.completions.create(model=..., messages=..., stream=True)
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta  # sends each token to the client as it arrives
```

If you used `return` instead of `yield`, you'd have to wait for the full response before sending anything. `yield` sends each token immediately.

### SSE vs WebSockets

- **SSE** — one direction only: server → client. Used for streaming LLM responses. Simpler.
- **WebSockets** — two-way real-time. Used for chat apps, live cursors, multiplayer. More complex.

For LLM streaming, always use SSE.

### Auto-creating a session

If `session_id` is `None`, create a session before saving the message:

```python
if session_id is None:
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    session_id = session.id
```

This means the user never explicitly creates a session — it happens automatically on the first message.

### Query param vs request body

- **Request body** — data sent inside the POST request (e.g. `content`). Defined in the Pydantic schema.
- **Query parameter** — appended to the URL (e.g. `/chat/messages?session_id=3`). Defined as a function parameter with a default.

`session_id` is a query param because it's optional and modifies the behaviour of the request — it's not part of the message data itself.
