import json

import openai

from bot.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def process_content(content: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": content}], response_format={"type": "json_object"}
    )
    res = json.loads(response.choices[0].message.content)
    return res
