from pathlib import Path


# Embedding Model Used
embedding_model_name = "BAAI/bge-large-en-v1.5"

# LLM model
llm_model = "llama3"


# Data Registry Path
base_path = Path(__file__).resolve().parent.parent
data_set_path = base_path / "Dataset"
data_registry_path = data_set_path / "Data_Registry.csv"



