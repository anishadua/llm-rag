# app/document_processor.py

import os
import pypdf 
from typing import List
from fastapi import HTTPException 

from app.config import UPLOAD_DIR, MAX_PAGES_PER_DOCUMENT
from app.vector_store import text_splitter, vectorstore

async def process_document_and_embed(file_path: str, filename: str) -> int:
    """
    Reads a document (currently only PDF), extracts text, chunks it,
    and adds the text chunks with their embeddings to the vector store.
    
    Args:
        file_path (str): The full path to the uploaded document file.
        filename (str): The original filename of the document.
        
    Returns:
        int: The number of text chunks processed and added to the vector store.
        
    Raises:
        HTTPException: If the file type is unsupported, PDF reading fails,
                       no text is extracted, or page limit is exceeded.
    """
    # 1. Validate File Type
    if not file_path.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF is supported.")

    text = ""
    try:
        # 2. Read and Extract Text from PDF
        with open(file_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            
            if len(pdf_reader.pages) > MAX_PAGES_PER_DOCUMENT:
                raise HTTPException(status_code=400, detail=f"Document '{filename}' exceeds the maximum limit of {MAX_PAGES_PER_DOCUMENT} pages.")
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text: 
                    text += page_text + "\n"
    except Exception as e:
        print(f"ERROR: Failed to read PDF '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Error reading PDF '{filename}': {e}")

    # 3. Check if any text was extracted
    if not text.strip():
        print(f"WARNING: No readable text extracted from '{filename}'.")
        raise HTTPException(status_code=400, detail="No readable text extracted from the document.")

    # 4. Chunk the extracted text
    chunks = text_splitter.split_text(text)
    
    # 5. Prepare metadata for each chunk
    metadatas = []
    for i, chunk_content in enumerate(chunks):
        metadatas.append({"source": filename, "chunk_index": i + 1}) 
    
    # 6. Add chunks and their metadata to the vector store
    vectorstore.add_texts(texts=chunks, metadatas=metadatas)
    
    print(f"INFO: Successfully processed {len(chunks)} chunks from document: '{filename}'")
    return len(chunks)
