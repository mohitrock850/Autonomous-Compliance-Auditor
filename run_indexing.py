import os
import faiss
import numpy as np
import pandas as pd
import pypdf
import docx
from sentence_transformers import SentenceTransformer 

# --- Configuration ---
KNOWLEDGE_DIR = "knowledge_base"
FAISS_INDEX_FILE = "knowledge.index"
# We're using a free, local model. This is a very popular one.
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' 

# --- Initialize Model (Runs on your CPU) ---
try:
    # This will download the model the first time you run it
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"Successfully loaded local model: {EMBEDDING_MODEL_NAME}")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    print("Please ensure you are connected to the internet to download the model.")
    exit()

# --- Helper Functions for File Reading (No Changes) ---

def get_text_from_pdf(file_path):
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

def get_text_from_docx(file_path):
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

def get_text_from_txt(file_path):
    """Extracts text from a TXT file."""
    print(f"Reading TXT: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def get_text_from_csv(file_path):
    """Converts CSV rows into natural language sentences."""
    print(f"Reading CSV: {file_path}")
    all_text = ""
    try:
        df = pd.read_csv(file_path)
        for index, row in df.iterrows():
            sentence = f"Row {index} contains: "
            for col_name, val in row.items():
                sentence += f"{col_name} is {val}, "
            all_text += sentence[:-2] + ".\n"
    except Exception as e:
        print(f"Error reading CSV {file_path}: {e}")
    return all_text

def get_text_from_excel(file_path):
    """Converts Excel rows (all sheets) into natural language sentences."""
    print(f"Reading Excel: {file_path}")
    all_text = ""
    try:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = df.dropna(how='all')
            for index, row in df.iterrows():
                sentence = f"In sheet '{sheet_name}', row {index} contains: "
                for col_name, val in row.items():
                    if pd.notna(val):
                        sentence += f"{col_name} is {val}, "
                all_text += sentence[:-2] + ".\n"
    except Exception as e:
        print(f"Error reading Excel {file_path}: {e}")
    return all_text

def get_file_text(file_path):
    """Auto-detects file type and calls the correct reader."""
    if file_path.endswith(".pdf"):
        return get_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return get_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return get_text_from_txt(file_path)
    elif file_path.endswith(".csv"):
        return get_text_from_csv(file_path)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return get_text_from_excel(file_path)
    else:
        print(f"Skipping unsupported file: {file_path}")
        return None

# --- Chunking Function (No Changes) ---
def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """Splits text into overlapping chunks."""
    if text is None or not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - chunk_overlap)
    return chunks

# --- Embedding Function (UPDATED) ---
def get_embeddings(texts):
    """Gets embeddings for a list of text chunks using local model."""
    if not texts:
        return []
    
    # Filter out any None or empty strings
    valid_texts = [text for text in texts if text and text.strip()]
    if not valid_texts:
        return []

    print(f"Creating embeddings for {len(valid_texts)} chunks...")
    try:
        # 'model.encode' is the function from sentence-transformers
        # It handles batching automatically.
        embeddings = model.encode(valid_texts, show_progress_bar=True)
        return embeddings, valid_texts
    except Exception as e:
        print(f"Error during embedding: {e}")
        return [], []

# --- Main Indexing Logic (UPDATED) ---

def main():
    print("Starting indexing process...")
    all_chunks = []
    chunk_metadata = [] 

    # 1. Read and Chunk all files
    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.isfile(file_path):
            text = get_file_text(file_path)
            if text:
                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    if chunk and chunk.strip(): # Only add non-empty chunks
                        all_chunks.append(chunk)
                        chunk_metadata.append(
                            {"source": filename, "chunk_num": i, "content": chunk}
                        )
    
    if not all_chunks:
        print("No text found in knowledge_base. Exiting.")
        return
        
    print(f"Total documents read. Found {len(all_chunks)} valid text chunks.")

    # 2. Get Embeddings for all chunks
    print("Getting embeddings from local model...")
    embeddings, valid_chunks = get_embeddings(all_chunks)
    
    if len(embeddings) == 0:
        print("No embeddings generated. Exiting.")
        return
    
    # 3. Create and Save FAISS Index
    embeddings_np = np.array(embeddings).astype("float32")
    
    # The dimension is determined by the model. 
    # 'all-MiniLM-L6-v2' creates 384-dimension vectors.
    dimension = embeddings_np.shape[1] 
    print(f"Embedding dimension: {dimension}")
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    print(f"Created FAISS index with {index.ntotal} vectors.")

    faiss.write_index(index, FAISS_INDEX_FILE)
    
    # Save the metadata for the *valid* chunks that were embedded
    import json
    with open("chunk_metadata.json", "w", encoding="utf-8") as f:
        # We must use the metadata that matches the 'valid_chunks'
        json.dump(chunk_metadata, f, indent=2) 
        
    print(f"Successfully saved index to {FAISS_INDEX_FILE}")
    print(f"Successfully saved metadata to chunk_metadata.json")
    print("Indexing complete!")


if __name__ == "__main__":
    main()