import json
import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for current information",
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


def run_tool(name, args):
    if name == "search":
        results = tavily_client.search(args["query"], max_results=3)
        content = "\n".join([r["content"][:500] for r in results["results"]])
        return content[:1500]
    return "Tool not found"


messages: list[dict] = [
    {
        "role": "system",
        "content": "You are a helpful research assistant. You have ONE tool available: 'search'. Only use the 'search' tool. Never call any other tool. After 2-3 searches, summarize what you found and stop searching.",
    }
]

while True:
    user_input = input("\nWhat do you want to know? (or 'quit'): ")
    if user_input.lower() == "quit":
        break

    messages.append({"role": "user", "content": user_input})

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,  # type: ignore
            tools=tools,  # type: ignore
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append({"role": "assistant", "tool_calls": message.tool_calls})
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                print(f"\n[calling tool: {tool_call.function.name} with {args}]")
                result = run_tool(tool_call.function.name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result,
                    }
                )
        else:
            print("\n" + (message.content or ""))
            messages.append({"role": "assistant", "content": message.content or ""})
            break
    else:
        # hit max iterations — force a final answer without tools
        messages.append({"role": "user", "content": "Summarize what you found so far."})
        final = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,  # type: ignore
        )
        answer = final.choices[0].message.content or ""
        print("\n" + answer)
        messages.append({"role": "assistant", "content": answer})
