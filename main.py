import os
from groq import Groq

MODEL = os.environ.get('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')

client = Groq()
completion = client.chat.completions.create(
    model=MODEL,
    messages=[
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")   
