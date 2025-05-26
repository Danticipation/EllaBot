import os
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
