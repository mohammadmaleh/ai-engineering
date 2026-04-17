import json
import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()


groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    }
]

while True:
    user_input = input("What do you want to research? \n")
    
    if user_input.lower() == "quit":
        break

    # Step 1: search
    search_results = tavily_client.search(user_input)
    context = "\n".join([r["content"] for r in search_results["results"]])

    # Step 2: summarize with Groq
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Summarize the search results to answer the user's question."},
            {"role": "user", "content": f"Question: {user_input}\n\nSearch results:\n{context}"}
        ]
    )
    
    print(response.choices[0].message.content)