import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
messages = [{"role": "system", "content": "you are a sarcastic assistant"}]
while True:
    user_input = input("enter your chat \n")

    if user_input.lower() == "quit":
        break

    messages.append(
        {
            "role": "user",
            "content": user_input,
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


print("program ended")
