# Source Code (`src`) - EU AI Act Agentic Auditor

This directory contains the core Python codebase for the local Agentic Retrieval-Augmented Generation (RAG) pipeline. The system is designed to ingest raw legal texts, build a searchable vector database, and autonomously audit AI software architectures for regulatory compliance.

To ensure maintainability and clear separation of concerns, the pipeline is divided into three distinct modules: Data Cleaning, Vector Embedding, and Agentic Retrieval.

## Directory Structure

```text
src/
├── data_cleaning/       # Raw PDF extraction and metadata structuring
├── embedding/      # Text chunking, embedding generation, and vector storage
└── Retrieval/      # Agentic LLM workflows and compliance reporting


