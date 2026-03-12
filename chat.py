import os
from dotenv import load_dotenv
import os
from groq import Groq

# Install required dependencies: pip install groq python-dotenv

def get_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or not api_key.startswith("gsk_"):
        while True:
            api_key = input("Enter your GROQ API key (must start with 'gsk_'): ")
            if api_key.startswith("gsk_"):
                break
            print("Invalid API key format. It must start with 'gsk_'.")
    return api_key

# Initialize API key and client
api_key = get_api_key()
client = Groq(api_key=api_key)

# Start chatbot interaction
def chat_with_bot():
    print("\n🤖 Chatbot is ready! Type 'exit' to end the conversation.\n")
    
    messages = [
        {"role": "system", "content": "You are a helpful and friendly AI assistant."}
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            model_name = os.environ.get('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.8,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            print("Chatbot: ", end="")
            bot_reply = ""
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="")
                bot_reply += content
            print("\n")

            messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    chat_with_bot()
