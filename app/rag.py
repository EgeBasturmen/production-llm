from pathlib import Path
from .prompts import RAG_PROMPT
from openai import OpenAI
from .models import RAGAnswer

client = OpenAI()


def load_docs():
    return Path("app/data/docs.txt").read_text()

def build_prompt(question:str):
    context= load_docs()
    return RAG_PROMPT.format(
        context=context,
        question=question
    )

def ask_rag(question:str)->RAGAnswer:
    prompt=build_prompt(question)

    response= client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    raw=response.choices[0].message.content
    return RAGAnswer.model_validate_json(raw)

