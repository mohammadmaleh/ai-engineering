# Agents & RAG — Cheat Sheet

## LLM Basics (01-llm-basics/chat.py)

- LLMs have no memory — you must send the full message history every single call
- `messages` is a list of dicts: `{"role": "user/assistant/system", "content": "..."}`
- System prompt sets the assistant's behavior — add it once at the start of `messages`
- Streaming: `stream=True` → iterate chunks → `chunk.choices[0].delta.content or ""`
- Build `full_response` by concatenating chunks, then append it to `messages` as assistant role

```python
messages = [{"role": "system", "content": "you are a sarcastic assistant"}]
# each turn: append user message → stream response → append full_response as assistant
```

---

## RAG — Retrieval Augmented Generation (02-rag/rag.py)

**Problem:** LLMs have a limited context window — you can't paste a whole document into the prompt.

**Solution:** chunk → embed → store → query → inject relevant chunks only.

### Steps
1. **Chunk** the document into smaller pieces with overlap (so context doesn't cut off mid-sentence)
2. **Store** in ChromaDB (a vector database — it converts text to embeddings automatically)
3. **Query** by similarity: `collection.query(query_texts=[user_input], n_results=2)`
4. **Inject** the results into the prompt as context

```python
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks

# Store
collection.add(documents=data_chunks, ids=[str(i) for i in range(len(data_chunks))])

# Query
results = collection.query(query_texts=[user_input], n_results=2)
context = "\n---\n".join(results["documents"][0])

# Inject into prompt
{"role": "user", "content": user_input + " " + context}
```

- System prompt: `"only answer from the context provided"` — prevents hallucination
- ChromaDB `PersistentClient` saves to disk so you don't re-embed every run

---

## Agents (03-agents/)

### Two Patterns

**Pattern B — hardcoded (what you built in old-practice):**
1. User asks question
2. Always call search tool first
3. Inject search results into prompt
4. Model summarizes

No decision-making. Model never decides whether to search.

**Pattern A — real agent loop (what we're building next):**
1. Send user message + available tools to model
2. Model returns `tool_calls` if it wants to use a tool (instead of `content`)
3. Your code executes the tool
4. Append both the tool call and the result to messages
5. Send again → model gives final answer
6. Repeat until model stops calling tools

### Tool Definition (JSON schema)
```python
tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    }
}]
```

### What the model returns when it wants a tool
```python
response.choices[0].message.tool_calls
# → list of tool calls, each has:
#   .function.name       → "search"
#   .function.arguments  → '{"query": "Berlin weather"}'  ← JSON string, must parse it
```

### Message Roles

Every message in the `messages` list has a `role`. The model uses this to understand who said what.

| Role | Sent by | Purpose |
|---|---|---|
| `system` | You | Sets model behavior. Sent once at the start. Never shown to user. |
| `user` | You | The human's message |
| `assistant` | Model | Model's response — either a final answer or a tool call request |
| `tool` | You | Result of executing a tool. Must include `tool_call_id` to link it back. |

The model sees the full history every request — roles tell it who said each thing.

### The loop (pattern A skeleton)
```python
while True:
    response = client.chat.completions.create(model=..., messages=messages, tools=tools)
    message = response.choices[0].message

    if message.tool_calls:
        # model wants to call a tool
        messages.append(message)  # append the assistant's tool_call message
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = run_tool(tool_call.function.name, args)
            messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})
        # loop again — model will now respond with the final answer
    else:
        # model gave a final answer, stop looping
        print(message.content)
        break
```
