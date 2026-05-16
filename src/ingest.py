import fitz
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

# --- config ---
PDF_FOLDER = Path("pdfs")
DB_PATH = "chroma_db"
COLLECTION = "docs"
MAX_CHUNK = 480
OVERLAP = 60

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_collection(reset=False):
    db = chromadb.PersistentClient(path=DB_PATH)
    if reset:
        try:
            db.delete_collection(COLLECTION)
            print("old index cleared.")
        except:
            pass
    return db.get_or_create_collection(COLLECTION)

def split_into_chunks(raw_text):
    result = []
    i = 0
    while i < len(raw_text):
        result.append(raw_text[i:i + MAX_CHUNK])
        i += MAX_CHUNK - OVERLAP
    return result

def run_ingestion():
    col = get_collection(reset=True)
    files = list(PDF_FOLDER.glob("*.pdf"))

    if not files:
        print("no pdfs found. drop files into /pdfs and retry.")
        return

    print(f"found {len(files)} file(s): {[f.name for f in files]}\n")

    for fpath in files:
        print(f"processing: {fpath.name}")
        pdf = fitz.open(fpath)

        for pg_idx, page in enumerate(pdf, start=1):
            content = page.get_text().strip()
            if not content:
                continue

            chunks = split_into_chunks(content)
            for c_idx, chunk in enumerate(chunks):
                uid = f"{fpath.name}__p{pg_idx}__c{c_idx}"
                vec = embedder.encode(chunk).tolist()
                col.add(
                    ids=[uid],
                    embeddings=[vec],
                    documents=[chunk],
                    metadatas=[{"file": fpath.name, "pg": pg_idx}]
                )

        print(f"  done: {fpath.name}")

    print(f"\nall done. {len(files)} pdf(s) ready to query.\n")

if __name__ == "__main__":
    run_ingestion()