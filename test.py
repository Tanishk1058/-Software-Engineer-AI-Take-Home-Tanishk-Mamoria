import chromadb
import json
from src.retriever import find_relevant_chunks
from src.llm import get_answer

db = chromadb.PersistentClient(path="chroma_db")
col = db.get_or_create_collection("docs")
loaded = set(m["file"] for m in col.get(include=["metadatas"])["metadatas"])
print(f"loaded documents: {loaded}\n")

my_questions = [
    "Give me introduction about Tanishk",
    "What are the rules of Pitch 120?",
]

results = []

for q in my_questions:
    print(f"\n{'='*55}")
    print(f"Q: {q}")
    print(f"{'='*55}")
    chunks = find_relevant_chunks(q, top_k=5)
    srcs = sorted(set(f"{c['source']} p.{c['page']}" for c in chunks))
    print(f"pulled from: {srcs}")
    ans = get_answer(q, chunks)
    print(f"A: {ans}")
    results.append({"question": q, "answer": ans, "sources": srcs})

with open("results.json", "w", encoding="utf-8") as f:
    json.dump({"documents": list(loaded), "results": results}, f, indent=2, ensure_ascii=False)

print("\nsaved to results.json")