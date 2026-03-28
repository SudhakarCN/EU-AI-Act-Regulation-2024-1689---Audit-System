import re
import fitz
import spacy
import pandas as pd
from pathlib import Path

nlp = spacy.load("en_core_web_sm")


def cleaning(text):
    # Lemmatize will keep the meaning of the word without truncating it.
    doc = nlp(text)
    protected = {"not", "no", "shall", "must", "may"}
    tokens = [
        token.lemma_.lower() for token in doc
        if (not token.is_stop or token.text.lower() in protected)
        and not token.is_punct and not token.is_space
    ]
    return " ".join(tokens)



def extract_clean_page_text(page):
    page_height = page.rect.height

    # 1. THE ABSOLUTE FLOOR (Failsafe for pages with NO footnotes)
    # The ELI line is at y=806. We allow main text to go all the way down to 805.
    dynamic_footer_cutoff = 805

    # 2. FIND THE FOOTNOTE SEPARATOR (If it exists)
    paths = page.get_drawings()
    candidate_lines = []

    for p in paths:
        r = p["rect"]
        # The Fingerprint: Thin, Left-aligned, Short, Bottom-half
        is_thin = r.height < 2
        is_left = r.x0 < 100
        is_short = 40 < r.width < 100
        is_bottom_half = r.y0 > (page_height / 2)

        if is_thin and is_left and is_short and is_bottom_half:
            candidate_lines.append(r.y0)

    # If we found footnote lines, tighten the cutoff to the HIGHEST one
    if candidate_lines:
        dynamic_footer_cutoff = min(candidate_lines) - 2

    # 3. EXTRACT AND FILTER TEXT
    clean_text = []
    blocks = page.get_text("dict")["blocks"]

    # Regex to catch page numbers like "5/144" just in case they sneak past
    page_num_pattern = re.compile(r'^\d+/\d+$')

    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                # Use the vertical CENTER of the line for safer math
                line_y_center = (l["bbox"][1] + l["bbox"][3]) / 2

                # --- FILTER 1: HEADER (Keep below y=50) ---
                if line_y_center < 80:
                    continue

                # --- FILTER 2: FOOTER / FOOTNOTES ---
                if line_y_center > dynamic_footer_cutoff:
                    continue

                line_text = "".join([s['text'] for s in l["spans"]]).strip()

                # --- FILTER 3: STRING FAILSAFES ---
                # Double-check that ELI links or page numbers didn't bypass the coordinate math
                if line_text.startswith("ELI: http") or page_num_pattern.match(line_text):
                    continue

                if line_text:
                    clean_text.append(line_text)

    return "\n".join(clean_text)



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


def processing_recitals(recitals_text):
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
        "Chapter": title_text,
        "Article_ID": None,
        "Article_Name": None,
        "Clause_ID": "INTRODUCTION",
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
            "Chapter": None,
            "Article_ID": None,
            "Article_Name": None,
            "Clause_ID": clause_id,
            "Processed_Text": processed_text,
            "Raw_Text": raw_text,
            }
        skb_rows.append(new_row)

    structured_KB = pd.DataFrame(skb_rows)
    return structured_KB




base_path = Path(__file__).resolve().parent.parent
data_set_path = base_path / "Dataset"
data_registry = pd.read_csv(data_set_path / "Data_Registry.csv")

chapters_text = ""
annexes_text = ""


# Processing Recital PDF:

recital_file_path = data_registry.iloc[4]["File_Path"]
recital_file_name = data_registry.iloc[4]["File_Name"]
recital_doc = fitz.open(recital_file_path)

clean_texts = " "
for page in recital_doc:
    clean_texts += extract_clean_page_text(page)



recitals_KB = processing_recitals(clean_texts)
recitals_KB.to_csv("Recitals_KB.csv")



