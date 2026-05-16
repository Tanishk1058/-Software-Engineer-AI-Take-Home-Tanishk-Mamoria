import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "chroma_db"
COLLECTION = "docs"

embedder = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.PersistentClient(path=DB_PATH)
col = db.get_or_create_collection(COLLECTION)

def find_relevant_chunks(query, top_k=5):
    vec = embedder.encode(query).tolist()
    hits = col.query(
        query_embeddings=[vec],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    results = []
    for text, meta in zip(hits["documents"][0], hits["metadatas"][0]):
        results.append({
            "text": text,
            "source": meta["file"],
            "page": meta["pg"]
        })
    return results