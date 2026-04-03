#Production-Grade RAG AI System

A **production-oriented Retrieval-Augmented Generation (RAG) system** built with FastAPI and Python.  
This project demonstrates how to design, evaluate, and operate a **reliable AI system after deployment**, not just during model development.

---

##Why This Project?

Most AI projects stop at training a model.

This project focuses on the real-world question:

> What happens AFTER you deploy an AI system?

It demonstrates how to:

- Retrieve relevant context efficiently
- Generate structured and reliable LLM outputs
- Monitor system performance and quality
- Handle failures and edge cases safely
- Continuously improve system quality

---

##System Architecture

Client
│
▼
FastAPI Service
├── /ask → RAG pipeline (LLM + retrieval)
├── /retrieve → Retrieval inspection (debugging + evaluation)
├── /metrics-lite → System metrics
└── /health → Service status

│
▼

Hybrid Retrieval Layer

Vector Similarity Search
BM25 Keyword Search

│
▼

LLM (Gemini / OpenAI)


---

## Core Features

### Hybrid Retrieval (Vector + Keyword)
- Combines **semantic similarity** and **BM25 keyword matching**
- Improves context relevance and retrieval robustness

---

### Retrieval Observability (`/retrieve`)
- Inspect retrieved chunks before generation
- Returns:
  - Vector score
  - Keyword score
  - Hybrid score
- Enables debugging and evaluation of retrieval quality

---

### Structured LLM Outputs
- Uses **Pydantic validation** to enforce strict JSON responses
- Ensures:
  - Reliable schema
  - Consistent outputs
  - Safe parsing

---

### Caching System
- Hash-based response caching
- Reduces latency and LLM cost
- Improves system efficiency

---

### Evaluation & Monitoring
- Retrieval metrics:
  - Recall@K
  - Context Precision
- System metrics:
  - Latency
  - Error rate
  - Cache hit ratio

---

### Canary Deployment
- Supports **A/B testing of prompt variants**
- Safely compares different prompt strategies in production

---

### Robust Fallback Handling
- Graceful degradation if:
  - LLM API fails
  - Quota is exceeded
- System still returns meaningful responses

---

### Feedback Loop
- Captures low-quality responses
- Enables continuous improvement of the system

---

### Production-Ready Design
- Docker-based deployment
- Modular architecture
- Config-driven system

---

## API Endpoints

### Ask Question

```http
POST /ask

Request:

{
  "question": "What is an AI Engineer?"
} Inspect Retrieval
POST /retrieve

Request:

{
  "query": "What is an AI Engineer?",
  "top_k": 3
}

Response:

{
  "query": "...",
  "chunks": [
    {
      "id": "docs.txt#0",
      "text": "...",
      "vec_score": 0.91,
      "kw_score": 0.72,
      "hybrid_score": 0.86
    }
  ]
}
Metrics
GET /metrics-lite

Returns:

total requests
cache hits/misses
error count
latency
Health Check
GET /health
Tech Stack
Backend: FastAPI
Language: Python
Validation: Pydantic
Retrieval:
Vector Search (custom in-memory)
BM25 (rank-based keyword search)
LLM:
Gemini / OpenAI APIs
Caching: In-memory cache
Containerization: Docker
Vector DB (planned/extendable): Qdrant / ChromaDB
Running the Project
1. Install dependencies
pip install -r requirements.txt
2. Run the API
uvicorn app.main:app --reload
3. Open Swagger UI
http://localhost:8000/docs
Example Use Case
Ask a question using /ask
Inspect retrieval using /retrieve
Monitor performance using /metrics-lite
What This Project Demonstrates

This project showcases:

Production-ready AI system design
Retrieval-augmented generation (RAG)
LLM orchestration and reliability
Observability and evaluation of AI systems
Real-world deployment considerations
