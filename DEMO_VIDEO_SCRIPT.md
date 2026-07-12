# TechMart AI Customer Support System
## Demo Video Script — Full Capstone Submission
**Estimated Duration: 8–10 minutes**
**Format: Screen recording with voiceover**

---

## PRE-RECORDING CHECKLIST

- [ ] Backend running: `uvicorn main:app --reload --port 8000`
- [ ] Frontend running: `npm run dev` on `localhost:3000`
- [ ] MongoDB connected (check `/health` endpoint)
- [ ] Browser zoom at 100%, dark mode enabled
- [ ] Microphone tested, background noise removed
- [ ] Knowledge base PDFs in `knowledge_base/` folder
- [ ] Screen resolution: 1920×1080 recommended
- [ ] Close all notifications (macOS: Do Not Disturb ON)

---

## SCENE 1 — HOOK & TITLE (0:00–0:30)

**[Show: A blank dark screen, then slowly reveal the TechMart chat UI]**

> "Every day, companies receive thousands of customer queries — billing issues, technical problems, product questions, and complaints, all mixed together. A single chatbot can't handle all of this well. That's why I built a Multi-Agent AI Customer Support System for TechMart Electronics — where five specialist AI agents work together in real time, powered by Retrieval-Augmented Generation, sentiment analysis, and a full-stack production architecture."

**[Text overlay fades in:]**
```
Multi-Agent AI Customer Support System
TechMart Electronics
RAG · Sentiment Routing · WhatsApp Integration
```

**[Pause 2 seconds]**

---

## SCENE 2 — ARCHITECTURE OVERVIEW (0:30–1:30)

**[Show: README.md or a clean architecture diagram]**

> "Before diving into the demo, here's a quick look at the system architecture."

**[Point to each layer as you mention it:]**

> "Customer messages arrive through a React and Next.js frontend. The FastAPI backend receives the request and immediately runs two things in parallel — an Intent Detection Agent that classifies the query, and a Sentiment Analysis Agent that checks the emotional state of the customer."

> "Based on those results, an Agent Router selects which specialist agents to invoke — Billing, Technical Support, Product, Complaint Resolution, or FAQ. These agents use RAG — Retrieval-Augmented Generation — pulling relevant chunks from a FAISS vector database built from TechMart's own knowledge base PDFs."

> "All conversations are stored in MongoDB. The system also supports WhatsApp via Twilio webhooks, and includes an analytics dashboard."

**[Pause 1 second]**

---

## SCENE 3 — KNOWLEDGE BASE & RAG PIPELINE (1:30–2:30)

**[Show: The `knowledge_base/` folder with PDFs, then switch to terminal]**

> "The knowledge base is the foundation of the RAG system. I created six documents for the fictional TechMart Electronics company — FAQ, Refund Policy, Shipping Policy, Warranty, Pricing Guide, and User Manual."

**[Open one PDF briefly — e.g. RefundPolicy.pdf]**

> "These documents are automatically ingested by the RAG pipeline. Let me show that quickly."

**[In terminal, run:]**
```bash
python rag/pipeline.py
```

**[Show the output:]**
> "The pipeline reads every PDF, splits them into overlapping 400-character chunks, generates embeddings using the sentence-transformers model `all-MiniLM-L6-v2`, and stores them in a FAISS vector index. This index is then queried on every customer message to retrieve the most semantically relevant context — which is injected directly into each agent's system prompt."

> "This means agents always respond with information grounded in the actual company policies — no hallucinations."

---

## SCENE 4 — LIVE DEMO: SIMPLE QUERY (2:30–3:30)

**[Switch to the chat UI at `localhost:3000`]**

> "Let's jump into the live demo. I'm logged in as a test user."

**[Type and send:]**
```
What are your support hours and how do I contact you?
```

**[Watch the agent panel on the left]**

> "You can see the routing log appear on the left — the system detected the intent as a general information query, and routed it to the FAQ Agent. Notice the agent card lights up with a pulsing indicator while it's processing."

**[When response appears, point to the badge:]**

> "The response comes back tagged with the FAQ Agent badge. The answer is grounded in the actual policy documents — mentioning the exact hours, email, and phone number from the knowledge base."

---

## SCENE 5 — LIVE DEMO: MULTI-AGENT ROUTING (3:30–4:30)

**[Type and send:]**
```
I paid for Premium yesterday but my account still shows the free plan. Also, what's the difference between Pro and Ultra?
```

**[Watch the sidebar — both billing and product agents should fire]**

> "This is where the multi-agent architecture shines. This single message has two distinct concerns — a billing issue and a product question. The Intent Detection Agent picks up on both, and the router invokes two agents simultaneously — Billing and Product — running them in parallel."

**[Point to both agent cards lighting up at the same time]**

> "Both agents respond independently and their outputs are aggregated into a single, structured reply — clearly labelled by agent so the customer knows exactly what's being addressed."

**[Point to the two sections in the response]**

> "This parallel invocation means response time is roughly the same as calling one agent — not doubled."

---

## SCENE 6 — LIVE DEMO: SENTIMENT ROUTING (4:30–5:45)

**[Point to the Sentiment Monitor section in the sidebar]**

> "Now let me show the sentiment analysis feature. Watch the Sentiment Monitor panel on the left."

**[Type and send:]**
```
I've been waiting THREE WEEKS for my refund and no one is responding to my emails. This is absolutely unacceptable. I'm going to dispute this charge with my credit card company if this isn't fixed TODAY.
```

**[Watch the sentiment gauge fill up red, urgency badge appear, risk flag appear]**

> "Immediately the Sentiment Monitor detects a frustrated customer — the score shoots up to around 90%, urgency is flagged as HIGH, and crucially — it detected the phrase 'dispute this charge' and raised a risk flag for a potential chargeback."

> "Because of the frustration score, the system automatically prepended the Complaint Agent to the routing queue — even though the customer only asked about a refund. You can see the routing log shows: 'Frustration detected → complaint agent prepended.'"

**[Point to the escalation banner at the top of the chat]**

> "And because the risk threshold was crossed, an escalation was triggered — a priority case was opened, a case ID was generated, and a human specialist would be notified to follow up within two hours."

**[Point to the response — complaint agent speaks first]**

> "Notice the response — the Complaint Agent leads with empathy and acknowledgement before any solution is offered. The tone is fundamentally different from the previous responses. This was injected automatically based on the sentiment score."

---

## SCENE 7 — BACKEND API DOCS (5:45–6:30)

**[Open browser tab to `localhost:8000/docs`]**

> "Here's the FastAPI interactive documentation — automatically generated from the code. The system exposes clean REST endpoints for authentication, chat, analytics, and the WhatsApp webhook."

**[Click on POST /api/chat/message and expand it]**

> "The chat endpoint accepts a message and optional session ID. It returns the AI response, the list of agents invoked, the detected intent, and the sentiment analysis results — all in a structured JSON payload."

**[Click on POST /api/auth/login]**

> "Authentication uses JWT tokens with bcrypt password hashing. The token is included in every subsequent request via an Authorization header."

**[Click on GET /api/analytics/summary]**

> "The analytics endpoint powers the dashboard — returning conversation counts, per-agent usage distribution, response times, and satisfaction scores."

---

## SCENE 8 — ANALYTICS DASHBOARD (6:30–7:15)

**[Navigate to `localhost:3000/dashboard`]**

> "The analytics dashboard gives administrators a real-time overview of system performance."

**[Point to stat cards]**

> "The top row shows key metrics — total conversations handled, average response time, satisfaction score, and the number of active agents."

**[Point to bar chart]**

> "The agent usage chart shows which agents are being invoked most frequently. In this session, Technical Support and Billing are the busiest — which reflects the types of queries we just sent."

**[Point to the activity table]**

> "The recent conversations table shows session IDs, detected intents, which agents were used, whether the case was resolved or escalated, and timestamps. Escalated cases are highlighted in red."

---

## SCENE 9 — WHATSAPP INTEGRATION (7:15–7:50)

**[Show the `api/whatsapp.py` file in VS Code]**

> "The final bonus feature is WhatsApp integration using Twilio. When a customer sends a WhatsApp message to the TechMart support number, Twilio forwards it to the `/api/whatsapp/webhook` endpoint."

**[Scroll through the key sections of the file]**

> "The webhook validates the Twilio signature for security, then runs the full sentiment-aware routing pipeline — exactly the same as the web chat. Special commands like 'reset' or 'help' are handled separately."

> "The response is formatted for WhatsApp — markdown converted to WhatsApp bold syntax, long messages truncated at 1,580 characters — and returned as a TwiML response that Twilio delivers to the customer."

**[Point to the escalation section]**

> "If a case is escalated, the WhatsApp reply includes a priority case card with a case ID — so the customer has a reference number even on mobile."

---

## SCENE 10 — PROJECT STRUCTURE & CODE QUALITY (7:50–8:30)

**[Show VS Code with the full project tree open]**

> "Here's the complete project structure. The frontend is a full Next.js TypeScript application with custom hooks — useChat manages the entire conversation state machine, useAuth handles JWT authentication. All API calls are centralised in the services layer."

**[Expand backend folder]**

> "The backend follows clean separation of concerns — agents are independent classes that inherit from a BaseAgent, the RAG pipeline is fully decoupled, and each API route is in its own file. The codebase is production-ready."

**[Show docker-compose.yml briefly]**

> "The entire stack is containerised with Docker Compose — one command, `docker-compose up --build`, spins up the MongoDB database, the FastAPI backend, and the Next.js frontend together."

---

## SCENE 11 — WRAP-UP & SUMMARY (8:30–9:00)

**[Return to the chat UI with all the previous messages visible]**

> "To summarise — this project implements a complete, production-grade Multi-Agent AI Customer Support System featuring:"

**[Read this list slowly and clearly:]**

> "Five specialised AI agents with custom system prompts — Intent Detection and routing — a full RAG pipeline with FAISS vector search and real knowledge-base PDFs — Sentiment analysis with automatic frustration detection, tone injection, and escalation — JWT authentication and MongoDB persistence — A Next.js analytics dashboard — WhatsApp integration via Twilio — and full Docker containerisation."

> "All source code, knowledge base documents, and setup instructions are included in the submission. Thank you."

**[Hold on the chat UI for 3 seconds, then fade out]**

---

## POST-RECORDING NOTES

### Backup Test Messages (in case live demo fails)
- Simple: `"What is your return policy?"`
- Multi-agent: `"My invoice is wrong and I also want to know about TechMart Ultra features"`
- Sentiment: `"I'm extremely disappointed. My device stopped working after 2 days and no one is helping me"`
- Technical: `"I keep getting ERR_002 when I try to open the app on my MacBook"`

### Common Issues During Demo
| Issue | Fix |
|-------|-----|
| Backend not responding | Check `uvicorn` is running on port 8000 |
| MongoDB error | Run `docker-compose up mongodb` separately |
| FAISS index missing | Run `python rag/pipeline.py` to rebuild |
| Slow agent responses | Normal — LLM calls take 2-4s each |
| WhatsApp not receiving | Check Twilio webhook URL and ngrok tunnel |

### Marks Alignment
| Section Demonstrated | Marks |
|---------------------|-------|
| Scene 4–6: Chat UI + multi-agent | Frontend Design (10) |
| Scene 7: API docs + endpoints | Backend APIs (15) |
| Scene 5: Parallel routing | Multi-Agent Architecture (20) |
| Scene 3: RAG pipeline | RAG Implementation (20) |
| Scene 4–6: Live responses | LLM Integration (15) |
| Scene 2: MongoDB + models | Database Design (10) |
| Scene 10–11: Docker + README | Documentation & Deployment (10) |

**Total: 100 marks**
