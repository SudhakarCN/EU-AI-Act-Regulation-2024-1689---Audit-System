import fitz
import pandas as pd
from pathlib import Path
import re
from src.data_cleaning.cleaning_utils import extract_clean_page_recitals, cleaning
import src.utils as utils

def parse_robust_recitals(text):
    pattern = re.compile(r'\s*\((\d+)\)\s*')
    parsed_data = []

    current_id = None
    last_text_start_index = 0

    # Flatten the text
    clean_text = text.replace('\n', ' ')

    for match in pattern.finditer(clean_text):
        found_num = int(match.group(1))

        # --- CONTEXT ANALYSIS ---
        # Look at the text immediately before and after the (Number)
        preceding_text = clean_text[:match.start()].strip()
        following_text = clean_text[match.end():].lstrip()

        is_start_of_text = len(preceding_text) == 0

        # Does the previous sentence end with punctuation?
        ends_with_punctuation = preceding_text.endswith(('.', '!', '?', '...', ';', ':', '"', '”'))

        # Does the next word start with a capital letter?
        starts_with_capital = following_text[0].isupper() if following_text else False

        # --- THE LOGIC GATES ---
        # Gate 1: The number must be going UP (Clauses don't go backwards)
        is_increasing = current_id is None or found_num > current_id

        # Gate 2: It must grammatically look like a new paragraph
        is_paragraph_start = is_start_of_text or (ends_with_punctuation and starts_with_capital)

        if is_increasing and is_paragraph_start:
            # Save the previous block
            if current_id is not None:
                paragraph = clean_text[last_text_start_index:match.start()].strip()
                parsed_data.append({
                    "ID": current_id,
                    "TEXT": paragraph
                })

            # Start tracking the new block
            current_id = found_num
            last_text_start_index = match.end()

    # Save the final block
    if current_id is not None:
        paragraph = clean_text[last_text_start_index:].strip()
        parsed_data.append({
            "ID": current_id,
            "TEXT": paragraph
        })

    return parsed_data

def processing_recitals(clean_texts):
    cleaned_text = clean_texts.split(sep="HAVE ADOPTED THIS REGULATION:", maxsplit=1)[0]
    buffer_text = cleaned_text.split(sep="Whereas:", maxsplit=1)
    introduction_titile_text = buffer_text[0].split("(Text with EEA relevance)", maxsplit=1)
    introduction_text = introduction_titile_text[1]
    title_text = introduction_titile_text[0]
    recitals_text = buffer_text[1]
    recitals_lst = parse_robust_recitals(recitals_text)

    skb_rows = []
    intro_row = {
        "File_Name": recital_file_name,
        "Document_Section": "Recitals",
        "Chapter_ID": None,
        "Chapter_Name": title_text,
        "Article_ID": None,
        "Article_Name": None,
        "Clause_ID": "INTRODUCTION",
        "SubClause_ID": None,
        "Processed_Text": cleaning(introduction_text),
        "Raw_Text": introduction_text
    }
    skb_rows.append(intro_row)

    # Cleaning the points and adding it to the Knowledge Base
    for item in recitals_lst:
        clause_id = item["ID"]
        raw_text = item["TEXT"]
        processed_text = cleaning(raw_text)
        new_row = {
            "File_Name": recital_file_name,
            "Document_Section": "Recitals",
            "Chapter_ID": None,
            "Chapter_Name": None,
            "Article_ID": None,
            "Article_Name": None,
            "Clause_ID": clause_id,
            "SubClause_ID": None,
            "Processed_Text": processed_text,
            "Raw_Text": raw_text,
            }
        skb_rows.append(new_row)

    structured_KB = pd.DataFrame(skb_rows)
    return structured_KB



data_set_path = utils.data_set_path
data_registry = pd.read_csv(data_set_path / "Data_Registry.csv")

annexes_text = ""


# Processing Recital PDF:

recital_file_path = data_registry.iloc[4]["File_Path"]
recital_file_name = data_registry.iloc[4]["File_Name"]
recital_doc = fitz.open(recital_file_path)

recital_texts = " "
for page in recital_doc:
    recital_texts += extract_clean_page_recitals(page)



recitals_KB = processing_recitals(recital_texts)
recitals_KB.to_csv("Recitals_KB.csv")



