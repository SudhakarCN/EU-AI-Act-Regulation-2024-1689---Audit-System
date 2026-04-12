import fitz
import re
import pandas as pd
from pathlib import Path
from cleaning_utils import extract_clean_page, cleaning, convert_roman_to_numerical
import src.utils as utils

# Swapped "chapter" and "article" for "annex"
re_patterns = {
    "sub_clause_id": r"^\([a-z]\)",
    "clause_id": r"^\d+\.|^\(\d+\)",
    "annex": r"^ANNEX\s+([IVXLCDM]+)"
}

def processing_annexes(full_text, file_name="Annexes.pdf"):
    split_text = full_text.split("\n")
    skb_rows = []

    # State trackers
    annex_id = None
    annex_name = None
    clause_id = None
    sub_clause_id = None
    raw_text = ""

    def save_row():
        nonlocal raw_text, annex_id, annex_name, clause_id, sub_clause_id
        # We only need annex_id to be present to save.
        # This allows us to save intro text (where clause_id is None)
        if annex_id and raw_text.strip():
            skb_rows.append({
                "File_Name": file_name,
                "Document_Section": "Annexes",
                "Chapter_ID": None,
                "Chapter_Name": None,
                "Article_ID": annex_id,
                "Article_Name": annex_name,
                "Clause_ID": clause_id,
                "SubClause_ID": sub_clause_id,
                "Processed_Text": cleaning(raw_text).strip(), # Re-enable your cleaning function here
                "Raw_Text": raw_text.strip()
            })

    ind = 0
    while ind < len(split_text):
        text = split_text[ind].strip()
        if not text:
            ind += 1
            continue

        # 1. Checking for Annex
        annex_match = re.match(re_patterns["annex"], text)
        if annex_match:
            save_row()
            raw_text = ""
            annex_id = annex_match.group(1)

            # Lookahead: Check if next line is a clause (meaning no Annex name)
            next_line = split_text[ind + 1].strip() if ind + 1 < len(split_text) else ""
            if re.match(re_patterns["clause_id"], next_line):
                annex_name = None
                ind += 1
            else:
                annex_name = next_line
                ind += 2

            # Reset downstream trackers
            clause_id = None
            sub_clause_id = None
            continue

        # 2. Checking for clause
        clause_id_match = re.match(re_patterns["clause_id"], text)
        if clause_id_match:
            save_row()
            raw_text = ""
            clause_id = re.findall(r"\d+", clause_id_match.group(0))[0]
            sub_clause_id = None

            remaining_text = text[clause_id_match.end():].strip()
            if remaining_text:
                raw_text = remaining_text + " "

            ind += 1
            continue

        # 3. Checking for sub_clause
        sub_clause_id_match = re.match(re_patterns["sub_clause_id"], text)
        if sub_clause_id_match:
            save_row()
            raw_text = ""
            base_clause = clause_id if clause_id else ""
            sub_clause_id = base_clause + sub_clause_id_match.group(0)

            remaining_text = text[sub_clause_id_match.end():].strip()
            if remaining_text:
                raw_text += remaining_text + " "

            ind += 1
            continue

        # 4. Processing standard text (This catches "Section A..." and Intro text perfectly)
        raw_text += text + " "
        ind += 1

    save_row()
    return skb_rows



# --- MAIN EXECUTION ---
data_registry = pd.read_csv(utils.data_registry_path)

annex_file_path = data_registry.iloc[0]["File_Path"]
annex_file_name = data_registry.iloc[0]["File_Name"]
annex_doc = fitz.open(annex_file_path)

pages = []

for page in annex_doc:
    pages.append(extract_clean_page(page))

full_document_text = "\n".join(pages)

skb_rows = processing_annexes(full_document_text)

annex_kb = pd.DataFrame(skb_rows)
annex_kb.to_csv("Annexes.csv", index=False)



