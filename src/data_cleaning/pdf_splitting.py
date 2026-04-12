from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from pathlib import Path


def split_pdfs(input_pdf):
    reader = PdfReader(input_pdf)

    chapters = [
        {"name": data_set_path / "Part_1_Recitals.pdf", "start": 0, "end": 44},
        {"name": data_set_path / "Part_2_Articles.pdf", "start": 43, "end": 123},
        {"name": data_set_path / "Part_3_Annexes.pdf", "end": len(reader.pages), "start": 123}
    ]

    for chap in chapters:
        writer = PdfWriter()

        for page_num in range(chap['start'], chap['end']):
            writer.add_page(reader.pages[page_num])

        with open(chap['name'], 'wb') as out_pdf:
            writer.write(out_pdf)
            print(f"Created {chap['name']} (Pages {chap['start'] + 1} to {chap['end']})")


base_path = Path(__file__).resolve().parent.parent
data_set_path = base_path / "Dataset"
data_registry = pd.read_csv(data_set_path / "Data_Registry.csv")
oj_l = data_registry.iloc[1]["File_Path"]

split_pdfs(oj_l)