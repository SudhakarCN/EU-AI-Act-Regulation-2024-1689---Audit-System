# EU AI Act Auditor: Agentic RAG Pipeline

## Description:
A completely local, privacy-first Agentic RAG system that analyzes AI software architectures and automatically generates EU AI Act compliance reports.

### Key Features:
- 100% Local Processing: Uses Ollama (Llama 3) and local HuggingFace embeddings. Zero data leaves the machine, making it safe for proprietary enterprise architectures.
- Agentic Retrieval: The system dynamically generates its own search queries based on the provided architecture to avoid vector dilution and capture niche regulatory traps.
- Automated Deduplication: Custom dictionary-based deduplication to optimize the LLM context window.

### Tech Stack:
- Python, Pandas
- LangChain & LangChain-Ollama
- ChromaDB (Vector Database)
- HuggingFace (BAAI/bge-large-en-v1.5)
- Ollama (Llama 3)

## Current Pipeline:
- Ingests and cleans EU AI Act PDFs.
- Builds local Chroma vectorstore.
- Takes an architecture summary as input.
- Agent 1 (Researcher) generates highly specific regulatory search queries.
- System retrieves and deduplicates relevant Articles and Recitals.
- Agent 2 (Auditor) generates a cited compliance report.

## Future Roadmap:
[ ] Integrate BM25 Hybrid Search for exact-keyword legal matching.

[ ] Implement LangGraph for advanced human-in-the-loop agent routing.

[ ] Wrap the pipeline in a Streamlit web interface.