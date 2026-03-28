import fitz
import re






dpath = "C://Users//sudhk//Documents//Programming//Projects//EU_AI_Act//Dataset//Part_1_Recitals.pdf"

doc = fitz.open(dpath)



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


# --- HOW TO RUN IT ---
# doc = fitz.open("Part_1_Recitals.pdf")
# page_5_text = extract_clean_page_text(doc[4])
# print(page_5_text)





# --- HOW TO RUN IT ---
# doc = fitz.open("Part_1_Recitals.pdf")
# page_5_text = extract_clean_page_text(doc[4])
# print(page_5_text)


import re


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
                    "id": current_id,
                    "text": paragraph
                })

            # Start tracking the new block
            current_id = found_num
            last_text_start_index = match.end()

    # Save the final block
    if current_id is not None:
        paragraph = clean_text[last_text_start_index:].strip()
        parsed_data.append({
            "id": current_id,
            "text": paragraph
        })

    return parsed_data






# --- Test it with your text ---
sample_text = """
(1) The purpose of this Regulation is to improve the functioning of the internal market...
(2) This Regulation (3) should be applied in accordance with the values...
"""

# clean_texts = " "
# for page in doc:
#     clean_texts += extract_clean_page_text(page)
#
# cleaned_text = clean_texts.split(sep="HAVE ADOPTED THIS REGULATION:", maxsplit=1)[0]
# buffer_text = cleaned_text.split(sep="Whereas:", maxsplit=1)
# introduction_titile_text = buffer_text[0].split("(Text with EEA relevance)", maxsplit=1)
# introduction_text = introduction_titile_text[1]
# title_text = introduction_titile_text[0]
# recitals_text = buffer_text[1]
#
#
# results = parse_robust_recitals(recitals_text)
# print(type(results))

import pandas as pd


df = pd.DataFrame({'points': [10, 12, 12, 14, 13, 18],
                   'rebounds': [7, 7, 8, 13, 7, 4],
                   'assists': [11, 8, 10, 6, 6, 5]})


df.add({"points": 2, 'rebound': 7, })