from cffi.cffi_opcode import PRIM_INT8
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
import src.utils as utils

## ollama run llama3


# ==========================================
# PHASE 1: WAKE UP THE SYSTEM
# ==========================================

# Configuring Embedding Model
print("Waking up the embedding model")
embd_model = utils.embedding_model_name
llm_model = utils.llm_model

embedder = HuggingFaceEmbeddings(model_name=embd_model)
db = Chroma(persist_directory="../eu_act_db", embedding_function=embedder)

# Connecting to Local LLM Model
print("\nConnecting to Local Llama 3")
llm = OllamaLLM(model=llm_model)


# Define the Architecture to be audited
architecture_summary = """
System Name: TalentVision Pro AI
System Version: 2.4.1 (Enterprise Deployment)
Target Market: Large enterprise Human Resources (HR) departments operating within the European Union.

Core Function: 
TalentVision Pro is an end-to-end automated recruitment, candidate screening, and employee performance prediction platform. It is designed to reduce the time-to-hire by 60% by automating the initial stages of the recruitment funnel.

Architecture & Data Flow:
1. Ingestion Layer: The system ingests applicant resumes (PDF/Word), scrapes public LinkedIn profile data, and securely stores one-way asynchronous video interviews recorded by the candidates. Data is hosted on AWS Frankfurt (eu-central-1) to maintain data residency.
2. NLP & Resume Scoring: We utilize a fine-tuned Mistral-7B Large Language Model to extract skills, education, and work history. The AI compares this against historical company hiring data to assign a "Candidate Fit Score" (1-100).
3. Video & Biometric Analysis: During the video interview phase, a proprietary computer vision model analyzes the candidate's facial micro-expressions, eye tracking, and voice tone to generate an "Engagement and Emotional Stability Score." This is used to assess culture fit.
4. Automated Decision Engine: To handle high-volume applications, the system is configured to automatically send rejection emails to any candidate who scores below a 40/100 aggregate score, without a human recruiter reviewing the file.
5. Post-Hire Tracking: The system connects to the company's internal Slack and email servers to monitor employee communication patterns, predicting flight risk or burnout based on sentiment analysis.

Security & Infrastructure: 
The application relies on a microservices architecture managed via Kubernetes. All data at rest is encrypted using AES-256. API endpoints are secured via OAuth 2.0. The system processes Personally Identifiable Information (PII) and inferential biometric data.
"""



# ==========================================
# PHASE 2: AGENT 1 - THE RESEARCHER
# ==========================================

print("--- Agent 1: Generating the search queries ---")

query_generator_prompt = f"""
You are an expert AI compliance researcher. 
Read the following AI architecture and extract 5 highly specific search queries to find relevant regulations in the EU AI Act.

### ARCHITECTURE
{architecture_summary}

### INSTRUCTIONS
Focus on identifying the core risk triggers within the architecture, regardless of the industry. Your queries should target:
1. The system's intended purpose and target domain (e.g., critical infrastructure, education, medical, law enforcement).
2. The sensitivity of the data processed (e.g., biometrics, PII, emotional data).
3. The degree of automated decision-making and the level of human oversight.
4. The potential impact on human health, safety, or fundamental rights.

Output ONLY a numbered list of the 5 queries. Do not include any introductory or concluding text.ding text.
"""

generated_queries = llm.invoke(query_generator_prompt)
queries_list = [q.strip() for q in generated_queries.split("\n") if q.strip()]



# ==========================================
# PHASE 3: THE MULTI-RETRIEVAL (Defeating Vector Dilution)
# ==========================================

print("\n --- Running Multi-Search against database --- \n")

unique_docs = {}

for queries in queries_list:
    results = db.similarity_search(query=queries, k=2)
    for doc in results:
        unique_docs[doc.page_content] = doc

context_text = ""

for doc in unique_docs.values():
    section = doc.metadata.get("Document_Section", "Unknown")
    chapter_id = doc.metadata.get("Chapter_ID", "NA")
    chapter_name = doc.metadata.get("Chapter_Name", "NA")
    article_id = doc.metadata.get("Article_ID", "NA")
    article_name = doc.metadata.get("Article_Name", "NA")
    clause_id = doc.metadata.get("Clause_ID", "NA")
    subclause_id = doc.metadata.get("SubClause_ID", "NA")

    citation = f"{section} | Article ID: {article_id} | Article Name: {article_name} | Clause/Recital: {clause_id} | Subclause: {subclause_id}"
    context_text += f"{citation} \n {doc.page_content} \n \n"




# ==========================================
# PHASE 4: AGENT 2 - THE AUDITOR
# ==========================================

print("--- Agent 2: Writing final audit report ---")

# The Master Prompt
audit_prompt = f"""
You are an expert EU AI Act Compliance Auditor. 
Your task is to review an AI System Architecture and identify its regulatory obligations based strictly on the provided legal text.
If you reference any law, article, or rule that is NOT explicitly written in the 'RETRIEVED EU AI ACT LAWS' section above, you will be penalized. 
Say 'I do not have enough information' instead of using outside knowledge

### SYSTEM ARCHITECTURE
{architecture_summary}

### RETRIEVED EU AI ACT LAWS
{context_text}

### INSTRUCTIONS:
1. Classify the system (e.g., High-Risk, Prohibited, Minimal Risk) based on the context.
2. List the specific obligations the deployer/provider must follow.
3. For every obligation, you MUST cite the specific Article or Recital provided. 
4. Do not invent rules. If the answer is not in the legal text, state that more information is needed.
"""




# Send the prompt to the LLM
response = llm.invoke(audit_prompt)

print("\n" + "="*50)
print("=== FINAL EU AI ACT COMPLIANCE AUDIT ===")
print("="*50 + "\n")
print(response)
