# nexla-mcp-server

MCP server that answers questions from PDF documents using a local LLM. Built for the Nexla take-home assignment.

## How it works

Drop PDFs into the pdfs/ folder. Run ingest to index them. Then ask questions and the system finds relevant chunks from the documents and passes them to a local model to generate an answer with source citations.

Everything runs locally. No API keys needed.

## Stack

- FastMCP for the MCP server
- PyMuPDF for reading PDFs page by page
- sentence-transformers for creating embeddings locally
- ChromaDB for storing and querying vectors
- llama3.2 via Ollama for generating answers
- Plain HTML and JS for the results viewer UI

## RAM Warning

The local LLM model requires a minimum amount of free RAM to run. If your system does not have enough free memory the model will crash with an error like "llama runner process has terminated" or "model requires more system memory than is available".

In that case open src/llm.py and change this one line:

```
LLM_MODEL = "llama3.2"
```

Replace llama3.2 with a lighter model. Some options to try in order of size:

```
ollama pull phi3:mini
ollama pull tinyllama
```

Then update the line in src/llm.py to match whichever model you pulled. No other changes needed anywhere.

## Setup

Install Ollama from ollama.com and pull the model:

```
ollama pull llama3.2
```

Clone the repo:

```
git clone https://github.com/YOUR_USERNAME/nexla-mcp-server
cd nexla-mcp-server
```

Create virtual environment and install dependencies:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add your PDFs to the pdfs/ folder.

Ingest the PDFs:

```
python -m src.ingest
```

You will see each file processed one by one. Re-run this only when PDFs change.

Open test.py and edit the my_questions list to add your own questions. The questions are hardcoded and need to be changed manually inside the file before running:

```
my_questions = [
    "Your first question here",
    "Your second question here",
]
```

Run the questions:

```
python test.py
```

This prints answers in the terminal and saves everything to results.json.

Start a local server to view results in browser:

```
python -m http.server 8080
```

Open your browser and go to:

```
http://127.0.0.1:8080/ui.html
```

This page reads results.json and displays all questions and answers with source document and page number.

To run the MCP server for agent connections:

```
python -m src.server
```

Server runs at http://127.0.0.1:8000 and accepts connections from any MCP compatible client.

## MCP Tool

query_documents(question)

- Accepts any natural language question about the indexed documents
- Retrieves top 5 most relevant chunks from ChromaDB
- Passes them as context to the local LLM
- Returns an answer with source file name and page number cited
- Works across multiple documents at once

Example:

```
Q: What are the rules of Pitch 120?
A: Teams must have 2 to 4 members. Each person can only be on one team.
   Composition must stay the same across all rounds.
   [Pitch120 Rulebook.pdf | page 3]
```

## Project files

- src/ingest.py reads each PDF page by page, splits text into chunks, embeds them and stores in ChromaDB
- src/retriever.py takes a question, embeds it, queries ChromaDB and returns the closest matching chunks
- src/llm.py builds a prompt using the retrieved chunks as context and calls llama3.2 via Ollama. Change the LLM_MODEL variable here to switch models
- src/server.py runs the MCP server using FastMCP and also serves the HTTP endpoints and ui.html
- test.py contains a list of questions that you define manually inside the file. Open test.py and edit the my_questions list to add or change questions. Run python test.py to get answers printed in terminal and saved to results.json
- ui.html opens in browser at http://127.0.0.1:8080/ui.html and displays the results from results.json

## Vibe Coding

I used Claude in the browser as my main tool throughout this project. Shared the assignment PDF at the start and described my constraints clearly which were Windows machine, no API budget and fully local setup. Then worked through it one file at a time, pasting errors back in when things broke and asking follow up questions when behaviour was unexpected.

Specific prompts worked much better than vague ones. Asking Claude to write ingest.py that reads PDFs page by page using PyMuPDF, chunks at 480 characters with 60 overlap, embeds with sentence-transformers and stores in ChromaDB with file name and page as metadata gave clean usable output. Asking something broad like build the ingestion pipeline gave generic code that needed heavy rewriting.

Had to override the AI on several things. It suggested llama3.2 which crashed immediately on my machine because I had very little free RAM on an 8GB system. Went through phi3:mini, gemma2:2b and tinyllama before finding what actually worked. The AI had no idea about my hardware situation and just suggested the most capable model. The AI also generated separate ChromaDB connections in different files which caused UUID mismatch errors at runtime. Traced that myself and fixed it by consolidating into one shared function. The first UI it produced looked like a standard chat interface which did not fit the use case so I pushed back and asked for a static results viewer instead which reads from a JSON file.

Overall the tool is genuinely useful for getting a working skeleton fast and for handling the repetitive parts of development. It is less reliable for anything that depends on the actual runtime environment like hardware limits, library conflicts or how separately generated files interact when run together. Those parts needed real hands on debugging. My approach throughout was to read every file before running it, understand what it does and not trust anything hardware dependent without testing it first. Best used as something that speeds up the known parts while you stay responsible for the actual problem solving.

## Hardware note

Built on an 8GB RAM Windows machine with around 750MB free RAM available during development. Model selection was limited by what could actually run on the hardware. Switching to a stronger model only requires changing one line in src/llm.py.