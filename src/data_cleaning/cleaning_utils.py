import re
import spacy

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

def extract_clean_page_recitals(page):
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



def extract_clean_page(page):
    footer_cut_off = 805
    header_cut_off = 80

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
                if line_y_center < header_cut_off:
                    continue

                # --- FILTER 2: FOOTER / FOOTNOTES ---
                if line_y_center > footer_cut_off:
                    continue

                line_text = "".join([s['text'] for s in l["spans"]]).strip()

                # --- FILTER 3: STRING FAILSAFES ---
                # Double-check that ELI links or page numbers didn't bypass the coordinate math
                if line_text.startswith("ELI: http") or page_num_pattern.match(line_text):
                    continue

                if line_text:
                    clean_text.append(line_text)

    return "\n".join(clean_text)


def convert_roman_to_numerical(s):
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val[s[i]]
    return int_val