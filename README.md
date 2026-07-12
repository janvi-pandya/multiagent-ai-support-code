# TechMart AI Customer Support System
## Multi-Agent · RAG · LLM-Powered

A production-grade AI customer support assistant using **Multi-Agent Architecture**, **Retrieval-Augmented Generation (RAG)**, and **Large Language Models**.

---

## Architecture Overview

```
Customer
    │
    ▼
React Frontend (Next.js + Tailwind)
    │
    ▼
FastAPI Backend
    │
    ├── Intent Detection Agent  (classifies query)
    │
    ├── Agent Router  (selects 1–N specialist agents)
    │       ├── 💳 Billing Agent
    │       ├── 🔧 Technical Support Agent
    │       ├── 📦 Product Agent
    │       ├── 🚨 Complaint Agent
    │       └── ❓ FAQ Agent
    │
    ├── RAG Pipeline
    │       ├── Document Chunker
    │       ├── Embedding Engine  (all-MiniLM-L6-v2)
    │       └── FAISS Vector Store
    │
    └── MongoDB  (conversation history + sessions)
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB (local or Atlas)
- Groq API key

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/techmart-ai-support
cd techmart-ai-support
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
MONGO_URI=mongodb://localhost:27017
JWT_SECRET=your-secret-key-here
ENVIRONMENT=development
```

Add PDFs to `knowledge_base/` then build the RAG index:

```bash
python rag/pipeline.py          # builds FAISS index from your PDFs
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local      # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                     # opens on http://localhost:3000
```

---

## Project Structure

```
customer-support-ai/
│
├── frontend/
│   ├── components/
│   │   ├── ChatWindow.tsx
│   │   ├── AgentPanel.tsx
│   │   ├── MessageBubble.tsx
│   │   └── RoutingVisualizer.tsx
│   ├── pages/
│   │   ├── index.tsx           # chat interface
│   │   ├── login.tsx
│   │   └── dashboard.tsx       # analytics
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useAuth.ts
│   └── services/
│       └── api.ts
│
├── backend/
│   ├── main.py                 # FastAPI app + CORS
│   ├── api/
│   │   ├── chat.py             # POST /api/chat/message
│   │   ├── auth.py             # POST /api/auth/login|register
│   │   └── analytics.py       # GET  /api/analytics/summary
│   ├── agents/
│   │   ├── base.py             # BaseAgent class
│   │   ├── router.py           # IntentDetectionAgent + AgentRouter
│   │   ├── billing.py
│   │   ├── technical.py
│   │   ├── product.py
│   │   ├── complaint.py
│   │   └── faq.py
│   ├── rag/
│   │   └── pipeline.py         # chunk → embed → store → retrieve
│   ├── database/
│   │   └── connection.py       # Motor async MongoDB
│   ├── vectorstore/            # auto-generated FAISS files
│   └── requirements.txt
│
├── knowledge_base/
│   ├── FAQ.pdf
│   ├── RefundPolicy.pdf
│   ├── ShippingPolicy.pdf
│   ├── Warranty.pdf
│   ├── Pricing.pdf
│   └── UserManual.pdf
│
└── README.md
```

---

## API Endpoints

| Method | Endpoint                    | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | `/api/auth/register`        | Create account                 |
| POST   | `/api/auth/login`           | Get JWT token                  |
| POST   | `/api/chat/message`         | Send message, get AI response  |
| GET    | `/api/chat/history/{id}`    | Fetch session history          |
| GET    | `/api/analytics/summary`    | Agent usage stats              |
| GET    | `/health`                   | Health check                   |

Interactive docs: `http://localhost:8000/docs`

---

## RAG Pipeline Details

### Ingestion (one-time / on update)
1. PDFs loaded from `knowledge_base/` using **PyPDF**
2. Text split into 400-char chunks with 80-char overlap
3. Chunks embedded via `sentence-transformers/all-MiniLM-L6-v2`
4. Stored in **FAISS** flat index (cosine similarity via inner product on L2-normalised vectors)

### Retrieval (per query)
1. User query embedded with same model
2. Top-4 chunks retrieved by cosine similarity
3. Chunks injected into agent system prompt as context
4. Agent generates grounded, policy-accurate response

### Rebuild Index After Updating Docs
```python
from rag.pipeline import RAGPipeline
RAGPipeline().rebuild()
```

---

## Recommended Datasets

| Dataset | Use Case | Link |
|---------|----------|------|
| CFPB Complaints | Real complaint training data | consumerfinance.gov |
| Banking77 | Intent classification (77 intents) | huggingface.co/PolyAI/banking77 |
| SQuAD 2.0 | QA fine-tuning | rajpurkar/SQuAD-explorer |
| MS MARCO | Semantic retrieval | microsoft/MSMARCO |
| DailyDialog | Dialogue modeling | liuzeming01/XDailyDialog |

---

## Deployment

### Frontend → Vercel
```bash
cd frontend && vercel --prod
```

### Backend → Railway
```bash
railway login && railway up
```

### Database → MongoDB Atlas
1. Create free cluster at mongodb.com/atlas
2. Set `MONGO_URI` in Railway environment variables

---

## Evaluation Criteria (100 marks)

| Component              | Marks |
|------------------------|-------|
| Frontend Design        | 10    |
| Backend APIs           | 15    |
| Multi-Agent Architecture | 20  |
| RAG Implementation     | 20    |
| LLM Integration        | 15    |
| Database Design        | 10    |
| Documentation & Deploy | 10    |

---

## Bonus Features
- [ ] Voice input/output (Web Speech API)
- [ ] Multilingual support (i18n + translation agent)
- [ ] Sentiment analysis for routing frustrated customers
- [ ] Automatic ticket creation (Zendesk / Linear)
- [ ] Human-agent handoff with WebSockets
- [ ] WhatsApp integration (Twilio)
- [ ] Admin dashboard to update knowledge base
- [ ] Customer satisfaction CSAT feedback

---

## Tech Stack

| Layer     | Technology |
|-----------|-----------|
| Frontend  | Next.js 14, Tailwind CSS, Axios |
| Backend   | Python 3.11, FastAPI, Uvicorn |
| AI        | Groq Llama 3 |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS / ChromaDB |
| Database  | MongoDB (Motor async driver) |
| Auth      | JWT (PyJWT + bcrypt) |
| Deploy    | Vercel (FE) + Railway (BE) + MongoDB Atlas |
