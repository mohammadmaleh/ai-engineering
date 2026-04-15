# AI Engineer Learning Project

## Who I Am
- Senior frontend dev (React, Next.js, TypeScript, Angular, Vue)
- Comfortable Python, outdated junior backend
- Complete AI/LLM beginner
- Goal: get hired as AI Engineer ASAP (1 month target)
- Stack choice: Python for AI backend, Groq API (free tier) for LLM calls

## Learning Plan
2 weeks to interview-ready → apply while building → learn from interviews

### Week 1 — Core Skills
- **Day 1 (done):** LLM API basics — streaming, history, system prompts
- **Day 2–3:** RAG — "chat with a PDF" (ChromaDB + FastAPI + Groq)
- **Day 4–5:** Agents + tool use — research agent that searches the web
- **Day 6:** Next.js frontend on the RAG app (your edge over other candidates)
- **Day 7:** CV, GitHub READMEs, deploy, start applying

### Week 2 — Depth + Job Hunt
- Keep applying every day
- Learn from interview questions — they tell you exactly what to study next
- Add evals, observability, or fine-tuning basics depending on what comes up
- Build one more small project based on a real job posting's requirements

### What gets you hired
1. 2 live projects on GitHub with clean READMEs and demos
2. Can explain RAG, agents, embeddings without notes
3. Polished frontend on at least one project — most AI candidates can't do this
4. Applying volume: 10+ applications/day starting Day 7

## Current Status
- [x] Day 1 (done): LLM API basics — streaming, history, system prompts
- [x] Day 2–3: RAG
- [ ] Day 4–5: Agents
- [ ] Day 6: Next.js frontend
- [ ] Day 7: CV + apply

## What's Built
- `01-llm-basics/chat.py` — CLI chat, streaming, multi-turn history (working)

## Key Decisions
- Using Groq (free) instead of Anthropic/OpenAI (paid)
- Python for all AI backend code
- This repo is the learning playground: `~/projects/ai-engineer/`

## Concepts I Can Explain

- i remembered about venv , I installed groq , and leared about load_dotenv 
- i learned how to loop inside teminal
- i learned how that chats has an array called messages , the messages consist of users messages and the ai messages
- i learned that llms has no memory and i have to send all the chat message eachtime , both the user and the ai messages , i learned about streams 
- im still not quite confident about the chunk.choices[0].delta.content, because i dont know the full object 
- i learned that streaming has to be set to true , and the stream is breakable  
- i learned about  the rag system
- if you have a big data, you chunk them into smaller arrays ,  with overlaps between the chunks so the context is not missleading or cutted
- you feed these chunks into a victor based database
- victor is an array of number that represent strings
- i used chroma to convert my chunked array into vector database 
- when i asked chroma about something , it returned only the chunks relevant to my question 
- then i passed the question and the chunks that are related to my question to groq client , and told gorq client to only consider my context 
- groq clienet answered me within my context only

## Questions / Blockers
_(fill in as they come up)_
