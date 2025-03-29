from g4f.client import Client
import asyncio
import sys
client = Client()
response = client.chat.completions.create(
    model="deepseek-v3",
    messages=[{"role": "user", "content": "ура?"}],
    web_search=False
)
print(response.choices[0].message.content)