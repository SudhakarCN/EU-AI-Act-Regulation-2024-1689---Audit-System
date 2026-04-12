import fitz
import re
import pandas as pd
from pathlib import Path
from cleaning_utils import extract_clean_page, cleaning, convert_roman_to_numerical
import src.utils as utils

# Updated regex patterns with anchors (^) to prevent false positives mid-sentence
re_patterns = {
    "sub_clause_id": r"^\([a-z]\)",
    "clause_id": r"^\d+\.|^\(\d+\)",
    "chapter": r"^CHAPTER\s+([IVXLCDM]+)",
    "article": r"^Article\s+(\d+)\s*$"
}


def processing_full_document(full_text, file_name):
    split_text = full_text.split("\n")
    skb_rows = []

    # State trackers moved INSIDE the function
    chapter_id = None
    chapter_name = None
    article_id = None
    article_name = None
    clause_id = None
    sub_clause_id = None
    raw_text = ""
    # Helper function moved INSIDE to easily access the local state trackers
    def save_row():
        nonlocal raw_text, chapter_id, chapter_name, article_id, article_name, clause_id, sub_clause_id
        if chapter_id and article_id and raw_text.strip():
            skb_rows.append({
                "File_Name": file_name,
                "Document_Section": "Articles",
                "Chapter_ID": chapter_id,
                "Chapter_Name": chapter_name,
                "Article_ID": article_id,
                "Article_Name": article_name,
                "Clause_ID": clause_id,
                "SubClause_ID": sub_clause_id,
                "Processed_Text": cleaning(raw_text).strip(),
                "Raw_Text": raw_text.strip()
            })

    ind = 0
    while ind < len(split_text):
        text = split_text[ind].strip()
        if not text:
            ind += 1
            continue

        # 1. Checking for chapter
        chapter_match = re.match(re_patterns["chapter"], text)
        if chapter_match:
            save_row()
            raw_text = ""
            chapter_id = chapter_match.group(1)

            # Lookahead: Check if next line is an Article
            next_line = split_text[ind + 1].strip() if ind + 1 < len(split_text) else ""
            if re.match(re_patterns["article"], next_line):
                chapter_name = None
                ind += 1
            else:
                chapter_name = next_line
                ind += 2

            article_name = None
            article_id = None
            clause_id = None
            sub_clause_id = None
            continue

        # 2. Checking for article
        article_match = re.match(re_patterns["article"], text)
        if article_match:
            save_row()
            raw_text = ""
            article_id = article_match.group(1)

            # Lookahead: Check if next line is a clause
            next_line = split_text[ind + 1].strip() if ind + 1 < len(split_text) else ""
            if re.match(re_patterns["clause_id"], next_line) or re.match(re_patterns["sub_clause_id"], next_line):
                article_name = None
                ind += 1
            else:
                article_name = next_line
                ind += 2

            clause_id = None
            sub_clause_id = None
            continue

        # 3. Checking for clause
        clause_id_match = re.match(re_patterns["clause_id"], text)
        if clause_id_match:
            save_row()
            raw_text = ""
            # Safely extract the numbers using .group(0)
            clause_id = re.findall(r"\d+", clause_id_match.group(0))[0]
            sub_clause_id = None

            remaining_text = text[clause_id_match.end():].strip()
            if remaining_text:
                raw_text = remaining_text + " "

            ind += 1
            continue

        # 4. Checking for sub_clause
        sub_clause_id_match = re.match(re_patterns["sub_clause_id"], text)
        if sub_clause_id_match:
            save_row()
            raw_text = ""
            # Ensure clause_id exists before concatenating
            base_clause = clause_id if clause_id else ""
            sub_clause_id = base_clause + sub_clause_id_match.group(0)

            remaining_text = text[sub_clause_id_match.end():].strip()
            if remaining_text:
                raw_text += remaining_text + " "

            ind += 1
            continue

        # 5. Processing standard text
        raw_text += text + " "
        ind += 1

    # Save whatever text is remaining at the very end of the document
    save_row()

    return skb_rows


# --- MAIN EXECUTION ---
data_registry = pd.read_csv(utils.data_registry_path)

article_file_path = data_registry.iloc[1]["File_Path"]
article_file_name = data_registry.iloc[1]["File_Name"]
article_doc = fitz.open(article_file_path)

pages = []
# Removing header and footer from the pages
for page in article_doc:
    pages.append(extract_clean_page(page))

# Removing recitals from the introduction page
introduction_page = pages[0].split(sep="HAVE ADOPTED THIS REGULATION:", maxsplit=1)[1]
pages.pop(0)
pages.insert(0, introduction_page)

# THE FIX: Combine all pages into one continuous string before processing
full_document_text = "\n".join(pages)

# Process the entire document at once
skb_rows = processing_full_document(full_document_text, article_file_name)

# Export to CSV
articles_kb = pd.DataFrame(skb_rows)
articles_kb.to_csv("Articles_KB.csv", index=False)