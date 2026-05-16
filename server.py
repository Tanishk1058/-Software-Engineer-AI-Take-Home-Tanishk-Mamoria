from fastmcp import FastMCP
from src.retriever import find_relevant_chunks
from src.llm import get_answer
from src.ingest import run_ingestion

print("starting up — indexing pdfs...")
run_ingestion()

mcp = FastMCP("nexla-doc-qa")

@mcp.tool()
def query_documents(question: str) -> str:
    """
    Ask anything about the loaded PDF documents.
    The tool finds the most relevant sections and returns
    a grounded answer with file and page references.

    Args:
        question: your natural language question

    Returns:
        answer string with source citations
    """
    hits = find_relevant_chunks(question, top_k=5)
    if not hits:
        return "nothing relevant found in the current documents."
    return get_answer(question, hits)

if __name__ == "__main__":
    mcp.run(transport="stdio")