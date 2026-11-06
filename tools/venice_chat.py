"""Small Venice chat check. The key stays in .env as VENICE_API_KEY."""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

client = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)

completion = client.chat.completions.create(
    model="zai-org-glm-5-2",
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
    max_tokens=20,
)

print(completion.choices[0].message.content)
