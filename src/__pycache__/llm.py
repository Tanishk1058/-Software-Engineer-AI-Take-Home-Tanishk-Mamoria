import ollama
import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

LLM_MODEL = "phi3:mini"

def build_prompt(question, chunks):
    ctx_parts = []
    for c in chunks:
        ctx_parts.append(
            f"[{c['source']} | page {c['page']}]\n{c['text']}"
        )
    ctx = "\n\n---\n\n".join(ctx_parts)

    return f"""You are analyzing a set of documents. Use only the excerpts below to answer.
For each point you make, mention the file name and page number it came from.
If the information isn't present, say so clearly — do not guess.

--- Document Excerpts ---
{ctx}

--- Question ---
{question}

--- Your Answer ---"""

def get_answer(question, chunks):
    prompt = build_prompt(question, chunks)
    out = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return out["message"]["content"]