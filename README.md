#  LLM-RAG (Retrieval-Augmented Generation Pipeline)

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline that allows users to upload documents and ask questions based on their content. It leverages **vector databases** for efficient retrieval and **LLM APIs** (Google Gemini, OpenAI, etc.) for contextual answer generation. The application is containerized using **Docker** and can be deployed both locally and on the cloud.

---

##  Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
- [API Usage](#api-usage)
  - [Upload Document](#1-upload-document)
  - [Query System](#2-query-system)
  - [View Processed Document Metadata](#3-view-processed-document-metadata)
- [Configuration Details](#configuration-details)
- [Testing](#testing)
- [Scalability Considerations](#scalability-considerations)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

##  Features

###  Document Ingestion & Processing
- Upload up to 20 documents (each max 1000 pages)
- Smart chunking for efficient storage and retrieval
- Embeds text chunks into vector database (ChromaDB)
- Stores metadata in MongoDB

###  Retrieval-Augmented Generation (RAG)
- Semantic search and context retrieval
- Sends relevant chunks to LLM (e.g., Gemini) for answer generation
- Outputs concise and accurate results with sources

###  API & Deployment
- REST API using FastAPI
- Endpoints for uploading, querying, and viewing document metadata
- Docker Compose support for full stack deployment
- Cloud-ready: deploy to AWS, GCP, Azure, etc.

---

##  Architecture

User --> FastAPI[FastAPI App]

FastAPI -- Upload --> DocumentProcessor

DocumentProcessor --> VectorDB[ChromaDB]

DocumentProcessor --> MetadataDB[MongoDB]

FastAPI -- Query --> VectorDB

VectorDB -- Chunks --> FastAPI

FastAPI -- LLM Call --> LLM[Google Gemini API]

LLM --> FastAPI

FastAPI --> User

User --> MetadataDB


---

##  Technology Stack

| Component              | Tech Used                  |
|------------------------|----------------------------|
| Backend                | FastAPI (Python)           |
| Document Parsing       | `pypdf`                    |
| Chunking               | `langchain`                |
| Embeddings             | `sentence-transformers`    |
| Vector DB              | `ChromaDB` with SQLite     |
| Metadata DB            | `MongoDB` (`pymongo`)      |
| LLM Provider           | Google Gemini (`google-generativeai`) |
| Containerization       | Docker, Docker Compose     |
| Testing                | `pytest`, `httpx`, `pytest-mock` |
| Env Management         | `python-dotenv`            |

---

## ⚙️ Setup and Installation

###  Prerequisites

- Python 3.9+
- pip
- Git
- Docker & Docker Compose
- Google Gemini API Key
- MongoDB Atlas (or local MongoDB)

---

###  Local Development Setup

```bash
git clone https://github.com/your-username/llm-rag.git
cd llm-rag
python3 -m venv venv
source venv/bin/activate       # Windows: .\venv\Scripts\activate.bat
pip install -r requirements.txt

Create a .env file:
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
MONGO_URI="mongodb://localhost:27017/"
MONGO_DB_NAME="ragsystem_db"
MONGO_COLLECTION_NAME="document_metadata"

Run the app:
uvicorn main:app --reload
Visit: http://127.0.0.1:8000/docs

🐳 Docker Setup 
Create your .env with the following for local Docker Mongo:
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
MONGO_URI="mongodb://mongo:27017/"
MONGO_DB_NAME="ragsystem_db"
MONGO_COLLECTION_NAME="document_metadata"

Build and run containers:
docker compose build
docker compose up -d
Access the app at: http://localhost:8000/docs

To stop:
docker compose stop
To stop and remove volumes:
docker compose down --volumes

API Usage
1. Upload Document
Endpoint: POST /upload_document/
Content-Type: multipart/form-data
curl -X POST "http://localhost:8000/upload_document/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"

2. Query System
Endpoint: POST /query/
Content-Type: application/json
{
  "query": "What is the main topic discussed in the document?"
}
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic discussed in the document?"}'

3. View Processed Document Metadata
Endpoint: GET /documents_metadata/
curl -X GET "http://localhost:8000/documents_metadata/" -H "accept: application/json"


⚙️ Configuration Details
🔑 LLM Provider
Model: models/gemini-2.5-flash-lite

Update .env with your API key

To switch to OpenAI: update app/llm.py and install langchain-openai

💾 Vector DB
Local: ChromaDB (with SQLite)
Replace with Pinecone, Weaviate, etc. by modifying vector_store.py

🗃️ Metadata DB
MongoDB URI in .env controls local vs Atlas cloud

🧾 Document Storage
PDFs are saved to ./uploaded_documents/

🧪 Testing
pytest
Tests use mocked LLMs and isolated test DBs/directories. Ensure Mongo is running.

🚀 Scalability Considerations
-Use cloud-based vector DBs (Pinecone, Qdrant) for production

-Use Celery for async chunking

-Scale FastAPI with Docker containers and a load balancer

-Integrate logging and monitoring tools (ELK, Datadog, etc.)

🌟 Future Enhancements
-Support .docx, .txt, .csv with unstructured.io

-Semantic/heading-aware chunking

-User authentication & authorization

-Hybrid + Re-ranking Search

-Cloud IaC (Terraform/AWS CloudFormation)

-Frontend UI for easier access
