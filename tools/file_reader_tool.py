import os
import pandas as pd
import pypdf
import docx

# --- File Reading Functions ---

def read_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    print(f"Reading PDF: {file_path}")
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def read_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    print(f"Reading DOCX: {file_path}")
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def read_txt(file_path: str) -> str:
    """Extracts text from a TXT file."""
    print(f"Reading TXT: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def read_csv(file_path: str) -> str:
    """Converts CSV rows into natural language sentences."""
    print(f"Reading CSV: {file_path}")
    all_text = ""
    try:
        df = pd.read_csv(file_path)
        for index, row in df.iterrows():
            sentence = f"Row {index} from {os.path.basename(file_path)} contains: "
            for col_name, val in row.items():
                sentence += f"{col_name} is {val}, "
            all_text += sentence[:-2] + ".\n"
    except Exception as e:
        print(f"Error reading CSV {file_path}: {e}")
    return all_text

def read_excel(file_path: str) -> str:
    """Converts Excel rows (all sheets) into natural language sentences."""
    print(f"Reading Excel: {file_path}")
    all_text = ""
    try:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = df.dropna(how='all')
            for index, row in df.iterrows():
                sentence = f"In sheet '{sheet_name}' from {os.path.basename(file_path)}, row {index} contains: "
                for col_name, val in row.items():
                    if pd.notna(val):
                        sentence += f"{col_name} is {val}, "
                all_text += sentence[:-2] + ".\n"
    except Exception as e:
        print(f"Error reading Excel {file_path}: {e}")
    return all_text

# --- Main Tool Function ---

def read_document_content(file_path: str) -> str | None:
    """
    Auto-detects file type and calls the correct reader.
    This is the main function the Ingestion Agent will call.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        return read_pdf(file_path)
    elif file_extension == ".docx":
        return read_docx(file_path)
    elif file_extension == ".txt":
        return read_txt(file_path)
    elif file_extension == ".csv":
        return read_csv(file_path)
    elif file_extension in [".xlsx", ".xls"]:
        return read_excel(file_path)
    else:
        print(f"Unsupported file type: {file_extension}. Skipping.")
        return None
