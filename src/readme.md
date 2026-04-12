# Source Code (`src`) - EU AI Act Agentic Auditor

This directory contains the core Python codebase for the local Agentic Retrieval-Augmented Generation (RAG) pipeline. The system is designed to ingest raw legal texts, build a searchable vector database, and autonomously audit AI software architectures for regulatory compliance.

To ensure maintainability and clear separation of concerns, the pipeline is divided into three distinct modules: Data Cleaning, Vector Embedding, and Agentic Retrieval.

## Directory Structure

```text
src/
├── data_cleaning/       # Raw PDF extraction and metadata structuring
├── embedding/      # Text chunking, embedding generation, and vector storage
└── Retrieval/      # Agentic LLM workflows and compliance reporting


Module Breakdown
1. cleaning/ (Data Preparation)
This module is responsible for transforming unstructured legal PDFs into structured, machine-readable formats.

Key Functions: Extracts text from the official EU AI Act documents, cleans OCR artifacts, and rigorously tags metadata.

Methodology: Uses pandas to segment the law into specific Chapters, Articles, Recitals, and Annexes, ensuring that the downstream LLM has precise citation data.

2. embedding/ (Vector Database Construction)
This module handles the mathematical representation and storage of the cleaned legal text.

Key Functions: Chunks the structured text and converts it into semantic vectors.

Technology: Utilizes HuggingFace's BAAI/bge-large-en-v1.5 embedding model for high-accuracy semantic mapping, and stores the resulting vectors in a local ChromaDB instance.

3. retrieval/ (The Agentic Workflow)
This is the "brain" of the application, replacing standard RAG with an autonomous agentic pipeline.

Key Functions: Ingests software architecture summaries and executes a multi-step audit.

The Workflow: 1.  Query Generation: An initial LLM pass acts as a researcher, dynamically generating highly specific search queries based on the architecture's risk profile (e.g., biometrics, automated decision-making) to prevent vector dilution.
2.  Multi-Retrieval: Queries the ChromaDB and deduplicates the retrieved legal texts.
3.  Synthesis: A final LLM pass audits the architecture against the retrieved laws, generating a formatted, cited compliance report.

Technology: Powered by LangChain and locally hosted Ollama models (e.g., Llama 3).

Execution Pipeline
To run the full end-to-end audit, the modules should be executed in the following order:

Run the Cleaning Scripts: To generate the structured datasets (.csv or .json).

Run the Embedding Scripts: To initialize the local ChromaDB and populate it with the embedded laws. (Note: This step only needs to be run once unless the core legal text changes).

Run the Retrieval Scripts: To pass an architecture summary to the Agent and generate the final audit report.
