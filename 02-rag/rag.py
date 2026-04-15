import os

import chromadb
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


messages = [{"role": "system", "content": "only answer from the context provided. "}]


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)

    return chunks


with open("./sample.txt", "r") as f:
    data = f.read()

data_chunks = chunk_text(data)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("my_docs")


collection.add(documents=data_chunks, ids=[str(i) for i in range(len(data_chunks))])


while True:
    user_input = input("what is your question about the uploaded file ?\n")

    if user_input.lower() == "quit":
        break
    results = collection.query(query_texts=[user_input], n_results=2)
    context = "\n---\n".join(results["documents"][0])
    messages.append(
        {
            "role": "user",
            "content": user_input + " " + context,
        }
    )
    chat_completion = client.chat.completions.create(
        messages=messages, model="llama-3.3-70b-versatile", stream=True
    )

    full_response = ""
    for chunk in chat_completion:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        full_response += delta

    messages.append({"role": "assistant", "content": full_response})
