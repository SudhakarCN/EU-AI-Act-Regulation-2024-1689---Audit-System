EU AI Act: RAG Audit & Compliance System
This repository contains the architecture and codebase for a Retrieval-Augmented Generation (RAG) system designed to act as an automated audit assistant for the EU AI Act (Regulation 2024/1689).

Navigating complex regulatory frameworks requires high-precision information retrieval. This system is being built from the ground up to eliminate hallucinations and provide highly accurate, context-aware answers to compliance and regulatory queries.

Project Architecture & Roadmap
This project is being developed in stages to ensure robust data handling and retrieval:

Phase 1: Precision Data Ingestion (Current Focus) >     Standard NLP parsers struggle with the EU's formatting, mixing footnotes with critical legal clauses. This pipeline utilizes PyMuPDF to treat the document as geometry, mathematically hunting for page dividers and acting as a "dynamic guillotine" to physically crop out footnotes before text extraction. This ensures a pristine context window.
-  Run data_registry.py file to create a data source csv file containing the paths to the pdf files.
-  Run the recitals_cleaning.py file to clean and process the recitals document.

Phase 2: Vector Search & Chunking Strategy (Upcoming)
Implementing intelligent, semantically aware chunking of the legal text and embedding it into a vector database for rapid, accurate retrieval.

Phase 3: LLM Integration & Audit Agent (Upcoming)
Connecting the retrieval pipeline to an LLM to process user queries, verify compliance requirements, and cite specific articles and annexes from the act.
