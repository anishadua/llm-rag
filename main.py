# main.py (Updated for Modular Structure)

import os
import shutil 
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime

# --- Import components from my app modules ---
from app.config import UPLOAD_DIR, MAX_DOCUMENTS_LIMIT 
from app.models import DocumentMetadataResponse, QueryRequest, QueryResponse 
from app.database import metadata_collection 
from app.vector_store import vectorstore 
from app.llm import gemini_model
from app.document_processor import process_document_and_embed

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="RAG Pipeline",
    description="A Retrieval-Augmented Generation (RAG) pipeline for document querying. This version uses a modular architecture with MongoDB and Google Gemini.",
    version="1.0.0",
)

# --- API Endpoints ---

@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    """
    [cite_start]**Endpoint for Uploading Documents** [cite: 1, 19]

    Allows users to upload PDF documents for processing. The system will then
    chunk the document, generate embeddings, and store its metadata and embeddings.

    **Requirements:**
    - [cite_start]Supports uploading up to 20 documents, each with a maximum of 1000 pages[cite: 8].
    - [cite_start]Chunks documents into manageable sizes[cite: 9].
    - [cite_start]Uses text embeddings to store chunks in a vector database[cite: 10].
    - [cite_start]Stores document metadata in a NoSQL database (MongoDB)[cite: 22].
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided in the upload.")

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension != ".pdf":
        raise HTTPException(status_code=400, detail=f"Unsupported file type: '{file_extension}'. Only PDF files are accepted.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    doc_count = metadata_collection.count_documents({})
    if doc_count >= MAX_DOCUMENTS_LIMIT:
        raise HTTPException(status_code=400, detail=f"Maximum number of documents ({MAX_DOCUMENTS_LIMIT}) reached. Please remove existing documents before uploading more.")
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        original_size_kb = os.path.getsize(file_location) / 1024

        num_chunks = await process_document_and_embed(file_location, file.filename)

        # [cite_start]Prepare and insert metadata into MongoDB [cite: 22]
        new_doc_metadata = {
            "filename": file.filename,
            "original_size_kb": int(original_size_kb),
            "upload_date": datetime.utcnow(),
            "num_chunks": num_chunks,
            "status": "processed",
            "file_path": file_location
        }
        
        insert_result = metadata_collection.insert_one(new_doc_metadata)

        return {
            "message": f"Document '{file.filename}' uploaded and processed successfully!",
            "metadata_id": str(insert_result.inserted_id),
            "num_chunks": num_chunks
        }
    except DuplicateKeyError:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=409, detail=f"Document with filename '{file.filename}' already exists. Please use a unique filename.")
    except (PyMongoError, Exception) as e: 
        if os.path.exists(file_location):
            os.remove(file_location) 
        if isinstance(e, PyMongoError):
            raise HTTPException(status_code=500, detail=f"Database error during document upload: {e}")
        elif isinstance(e, HTTPException): 
            raise e
        else:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during document processing: {e}")


@app.get("/documents_metadata/", response_model=List[DocumentMetadataResponse])
async def get_documents_metadata():
    """
    **Endpoint for Viewing Processed Document Metadata**

    Retrieves metadata for all documents that have been successfully processed
    and stored in the system.
    """
    documents = list(metadata_collection.find({}))
        
    return documents


@app.post("/query/", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    """
    [cite_start]**Endpoint for Querying the System (RAG Pipeline)** [cite: 20]

    [cite_start]Accepts a user query, retrieves relevant document chunks from the vector database[cite: 12],
    [cite_start]and then passes these chunks along with the query to an LLM (Google Gemini) [cite: 14]
    to generate a contextual and informed response.
    """
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(request.query, k=4)
    
    if not retrieved_docs_with_scores:
        return QueryResponse(response="No relevant documents found for your query. Please upload documents first or try a different query.", source_documents=[])

    context_text = ""
    source_documents_info = []
    # Iterate through the retrieved documents to build the context for the LLM
    for doc, score in retrieved_docs_with_scores:
        context_text += doc.page_content + "\n\n"
        source_documents_info.append({
            "content_preview": doc.page_content[:200] + "...", 
            "metadata": doc.metadata, 
            "relevance_score": score 
        })

    # This prompt instructs the LLM to use the provided context to answer the question.
    prompt = f"""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context:
    {context_text}

    Question: {request.query}

    Answer:
    """

    try:
        response = gemini_model.generate_content(prompt)
        llm_response_text = response.text 
    except Exception as e:
        print(f"ERROR: Failed to get response from LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating LLM response: {e}. Please check your API key and network connection.")

    return QueryResponse(
        response=llm_response_text,
        source_documents=source_documents_info
    )
