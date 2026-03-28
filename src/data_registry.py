import pandas as pd
from pathlib import Path


if __name__ == "__main__":
    data_paths = pd.DataFrame(columns=["File_Name", "File_Path"])

    file_name = []
    file_paths = []


    base_path = Path(__file__).resolve().parent.parent
    data_set_path = base_path / "Dataset"
    data_list = []
    pdf_files = list(data_set_path.rglob("*.pdf"))

    for file in pdf_files:
        file_name.append(Path(file).name)
        file_paths.append(file)

    data_paths["File_Name"] = file_name
    data_paths["File_Path"]= file_paths

    data_paths.to_csv(data_set_path / "Data_Registry.csv", index=False)

