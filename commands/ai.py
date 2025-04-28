import re
from openai import OpenAI

async def ask_ai(prompt: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="...",
    )

    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1-distill-qwen-32b:free",
        messages=[
            {"role": "system", "content": "Ты — умный и дружелюбный ассистент по питанию. Отвечай только на русском языке."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = completion.choices[0].message.content

    cleaned_answer = re.sub(r'[^а-яА-ЯёЁa0-9\s.,!?:;()\[\]«»\"\'\-]', '', answer)
    cleaned_answer = ' '.join(cleaned_answer.split())

    formatted_answer = format_ai_response(cleaned_answer)

    return formatted_answer
import re

def format_ai_response(text: str) -> str:
    # Сначала обработка ":" как у тебя
    matches = list(re.finditer(r'(\S+):', text))

    if len(matches) <= 1:
        formatted_text = text
    else:
        first_end = matches[1].start()
        before = text[:first_end]
        after = text[first_end:]
        after = re.sub(r'(\S+):', r'\n\n\1:\n', after)
        formatted_text = before + after

    # Теперь обработка списка (1., 2., 3. и т.д.)
    formatted_text = re.sub(r'(\d+\.)\s*', r'\n\n\1 ', formatted_text)

    return formatted_text

