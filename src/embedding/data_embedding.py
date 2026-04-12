from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd
import src.utils as utils

recitals_df = pd.read_csv("../Recitals_KB.csv")
article_df = pd.read_csv("../Articles_KB.csv")
annexes_df = pd.read_csv("../Annexes.csv")

article_df = article_df.drop(columns=['Processed_Text', 'Unnamed: 0'], errors='ignore')
recitals_df = recitals_df.drop(columns=['Processed_Text', 'Unnamed: 0'], errors='ignore')
annexes_df = annexes_df.drop(columns=['Processed_Text', 'Unnamed: 0'], errors='ignore')

article_loader = DataFrameLoader(data_frame=article_df, page_content_column="Raw_Text")
recitals_loader = DataFrameLoader(data_frame=recitals_df, page_content_column="Raw_Text")
annexes_loader = DataFrameLoader(data_frame=annexes_df, page_content_column="Raw_Text")

all_documents_loader = recitals_loader.load() + article_loader.load() + annexes_loader.load()

print(f"Successfully Loaded the {len(all_documents_loader)} document chunks in LangChain")

model_name = utils.embedding_model_name
embedder = HuggingFaceEmbeddings(model_name=model_name)

print("Starting the embedding process")

db = Chroma.from_documents(
    documents=all_documents_loader,
    embedding=embedder,
    persist_directory="../eu_act_db"
)

print("Database successfully loaded and saved to eu_act_db!")