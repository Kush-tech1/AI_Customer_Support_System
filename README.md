# 🤖 AI Customer Support Platform

An intelligent e-commerce customer support system that uses LLM-based agents, model routing, and agentic orchestration to handle customer inquiries about orders, payments, refunds, and FAQs.

<img width="479" height="323" alt="image" src="https://github.com/user-attachments/assets/f55868d3-31b3-412d-969d-6fc585966607" />

## 📌 Overview

This project demonstrates key concepts in building AI-powered support systems:
- 🎯 **Model routing** — selecting the right model based on request complexity
- 🔄 **Agent orchestration** — coordinating multiple specialized agents via LangGraph
- 📋 **Structured outputs** — using Pydantic to validate LLM responses
- 🛡️ **Reliability patterns** — implementing retries and fallback models
- ⚙️ **Runtime control** — managing AI behavior through configuration
- 📊 **Observability** — logging model execution metrics
- 📈 **Evaluation** — measuring accuracy of triage and routing decisions

The system is intentionally lightweight and built for rapid prototyping. It is **not production-ready** and omits real authentication, distributed infrastructure, and production-scale evaluation.

---

## 🏗️ Architecture

<img width="1222" height="1287" alt="image" src="https://github.com/user-attachments/assets/38fc8739-adcc-4882-aee7-fbd95a87de38" />

### 📋 Request Flow

#### Simple Request
Customer asks: *"Where is my order 1001?"*

1. **Triage** → Detects intent=`order_status`, complexity=`simple`
2. **Order Lookup** → Queries SQLite, retrieves order details
3. **ModelRouter** → Selects `gemini-3.1-flash-lite` (default model)
4. **Response Agent** → Generates concise answer
5. **API Response** → Returns answer, confidence, selected model, latency

#### Complex Request
Customer asks: *"My order 1003 was cancelled but I was charged. When will I get my money back?"*

1. **Triage** → Detects intent=`order_cancelled`, complexity=`complex`
2. **Order/Payment Lookup** → Retrieves both order AND payment status
3. **ModelRouter** → Selects `gemini-3.8-flash` (complex model)
4. **Response Agent** → Generates detailed answer explaining refund timeline
5. **API Response** → Returns answer with model, latency, and retry count

---

## 🧭 Model Routing

The **ModelRouter** selects which model to use based on request complexity:

| Complexity | Model | When Used |
|---|---|---|
| **simple** | `gemini-3.1-flash-lite` | Straightforward questions (order status, general FAQs) |
| **complex** | `gemini-3.8-flash` | Payment issues, cancellations with disputes, multi-issue requests |

### 🔀 Routing Logic

The triage agent determines complexity:

```python
# Simple
- order_status
- refund_policy
- general_faq

# Complex
- payment_issue
- cancellation_with_payment
- refund_dispute
```

Complex intents are configured in `config.yaml` and can be adjusted without code changes.

### 🛡️ Reliability Features

**Retries (Primary Model)**
- Maximum retries: `config.runtime.max_retries` (default 2)
- Retries apply to the selected model (flash-lite or flash)
- If all retries fail, fall back to the fallback model

**Fallback Model**
- After primary model fails all retries, ModelRouter uses `gemini-3.1-flash-lite`
- Ensures a response is always attempted, even if the complex model fails
- All failures are logged with request ID for debugging

**Demo Failure Simulation**
- Set `demo.force_model_failure: true` in `config.yaml` to simulate complex model failures
- Useful for demonstrating retry and fallback behavior
- Default: `false`

---

## ⚙️ Runtime Control Plane

`config.yaml` contains lightweight runtime policies. This is a prototype mechanism for managing AI behavior without code changes:

```yaml
models:
  default: gemini-3.1-flash-lite       # Simple requests
  complex: gemini-3.8-flash              # Complex requests
  fallback: gemini-3.1-flash-lite        # Fallback after retries

runtime:
  max_retries: 2                         # Retry attempts before fallback
  timeout_seconds: 10                    # Timeout per API call

routing:
  complex_intents:
    - payment_issue                      # Trigger complex model
    - cancellation_with_payment
    - refund_dispute

demo:
  force_model_failure: false             # Simulate complex model failure
```

**Benefits:**
- 🔧 Change routing logic without redeploying code
- 📊 Model selection transparency — each request logs which model was selected
- 🧪 Reliability testing — toggle failure simulation to show retry/fallback
- 📝 Observability — logging captures all routing decisions

---

## 🔗 Agent Orchestration with LangGraph

LangGraph explicitly manages the workflow, making data flow and control flow transparent:

```
START
  ↓
[Triage Node] → Classifies intent, determines complexity
  ↓
[Order/Payment Node] → Performs deterministic database lookups
  ↓
[Response Node] → Generates structured response via LLM
  ↓
END
```

### ✅ Why LangGraph?

- Makes agent workflows explicit and debuggable
- Simplifies state management across multiple agents
- Enables future enhancements (parallel nodes, conditional routing)
- Standard pattern for agentic AI systems

---

## 💾 Data Layer

### SQLite Database

Mock data is stored in `app/data/support.db`:

| Table | Purpose | Schema |
|---|---|---|
| `customers` | User profiles | id, name, email |
| `orders` | Customer orders | id, customer_id, status, total_amount |
| `payments` | Payment records | id, order_id, status, amount |
| `faqs` | Frequently asked questions | id, question, answer |

### 🎯 Deterministic Lookups

The **OrderPaymentAgent** retrieves facts from SQLite. The LLM does not invent order data:

```python
order = get_order(1001)  # → {"id": 1001, "status": "shipped", ...}
payment = get_payment(1001)  # → {"id": 5001, "status": "captured", ...}
faqs = get_faqs()  # → All FAQs from database
```

These facts are passed to the response agent as context, ensuring answers are grounded in real data.

---

## 📋 Structured Outputs with Pydantic

Pydantic models define and validate LLM outputs:

### TriageResult
```python
class TriageResult(BaseModel):
    intent: Literal["order_status", "order_cancelled", "payment_issue", "refund_policy", "general_faq"]
    complexity: Literal["simple", "complex"]
    order_id: int | None
    requires_order_lookup: bool
    requires_payment_lookup: bool
```

### SupportResponse
```python
class SupportResponse(BaseModel):
    answer: str
    confidence: float  # 0.0 to 1.0
    needs_human: bool
```

### ⚠️ Important

Pydantic provides **validation and contracts**, but does **not make LLMs deterministic**. The LLM still generates probabilistic text; Pydantic ensures it conforms to a schema. If validation fails, ModelRouter retries.

---

## 📊 Observability

The system logs model execution metrics to console (JSON format):

```json
{
  "request_id": "abc-123",
  "agent": "response",
  "model": "gemini-3.8-flash",
  "latency_ms": 1250,
  "success": true,
  "retries": 0,
  "fallback": false
}
```

### 📈 Metrics Captured

- **request_id** — Unique ID for tracing a single support request
- **agent** — Which agent executed (triage, response)
- **model** — Which model was selected and used
- **latency_ms** — Time to generate response
- **success** — Whether the LLM call succeeded
- **retries** — Number of retry attempts before success/fallback
- **fallback** — Whether the fallback model was used

### 🔍 Use Cases

- Understand which models are used most frequently
- Identify slow or failing requests
- Trace the execution path of a specific request by ID
- Debug retry and fallback behavior

---

## 📈 Evaluation

The `evals/` directory contains a lightweight evaluation framework:

### 📋 Dataset

`evals/dataset.json` contains 10 test cases covering:
- Order status (simple)
- Cancellations (simple and complex)
- Payment issues (complex)
- Refund policies (simple)
- General FAQs

Each case specifies:
- Input message
- Expected intent
- Expected complexity
- Expected order ID
- Expected answer keywords

### 🏃 Running Evaluations

```bash
python evals/run_evals.py
```

The script runs the first 5 cases (to minimize API quota usage) and reports:

```
Intent accuracy:      100%
Routing accuracy:     100%
Order ID accuracy:    100%
Answer checks:        100%
```

### ⚠️ Important

These metrics are **on the current 5-case evaluation set**. Do not claim 100% real-world accuracy. The evaluation is a proof-of-concept to verify the system works end-to-end, not a production evaluation.

### 🔧 Extending Evaluations

- Add more cases to `dataset.json`
- Adjust the slice in `run_evals.py` (currently `dataset[:5]`)
- Implement custom scoring logic

---

## 💬 Streamlit UI

A simple chat interface for testing the support system.

### 🚀 Run the UI

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

### ✨ Features

- 💬 Chat history
- 🤖 Real-time model selection display
- ⏱️ Latency and retry metrics
- ↩️ Fallback status indicator
- ⚠️ Error handling for API failures

### 📺 Display Fields

For each response, the UI shows:
- **Model** — Which model answered (flash-lite or flash)
- **Latency** — Time to generate response (ms)
- **Retries** — Number of retry attempts
- **Fallback** — Whether fallback model was used

---

## 🔌 API Endpoints

### Health Check
```
GET /health

Response:
{
  "status": "ok"
}
```

### Support Request
```
POST /support

Request:
{
  "message": "Where is my order 1001?"
}

Response:
{
  "answer": "Order 1001 has been shipped...",
  "intent": "order_status",
  "complexity": "simple",
  "order_id": 1001,
  "confidence": 0.95,
  "needs_human": false,
  "runtime": {
    "model": "gemini-3.1-flash-lite",
    "latency_ms": 1200,
    "retries": 0,
    "fallback": false
  }
}
```

---

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, endpoints
│   ├── config.py                    # Config loading (YAML, env)
│   ├── agents/
│   │   ├── triage.py               # Classify intent, determine complexity
│   │   ├── order_payment.py        # Deterministic database lookup
│   │   └── response.py             # Generate final answer
│   ├── models/
│   │   ├── client.py               # Gemini API wrapper
│   │   └── router.py               # Model selection, retry, fallback
│   ├── schemas/
│   │   └── support.py              # Pydantic models (TriageResult, SupportResponse)
│   ├── graph/
│   │   └── workflow.py             # LangGraph workflow definition
│   ├── data/
│   │   ├── database.py             # SQLite helpers
│   │   ├── seed.py                 # Database initialization and seeding
│   │   └── support.db              # SQLite database (created at runtime)
│   └── observability/
│       └── logger.py               # Event logging
├── evals/
│   ├── dataset.json                # Test cases
│   └── run_evals.py                # Evaluation runner
├── ui/
│   └── app.py                       # Streamlit chat interface
├── config.yaml                      # Runtime configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🚀 Setup and Installation

### 📋 Prerequisites

- Python 3.9+
- Google Gemini API key
- (Optional) Windows Command Prompt or PowerShell

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Kush-tech1/AI_Customer_Support_System.git
cd AI_Customer_Support_System
```

### 2️⃣ Create Virtual Environment

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Create a `.env` file in the repository root:

```
GEMINI_API_KEY=your-api-key-here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5️⃣ Seed the Database

```bash
python -m app.data.seed
```

Output:
```
Database seeded successfully.
```

This creates `app/data/support.db` with sample customers, orders, payments, and FAQs.

### 6️⃣ Start the FastAPI Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The server will start at `http://127.0.0.1:8000`.

To verify it's running:
```bash
curl http://127.0.0.1:8000/health
```

### 7️⃣ Start the Streamlit UI (In a New Terminal)

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
streamlit run ui/app.py
```

### 8️⃣ Run Evaluations (In a New Terminal)

```bash
python evals/run_evals.py
```

This runs 5 test cases and reports accuracy metrics. **Note:** Each case includes a 4-second delay to manage API quota.

---

## 💡 Example Usage

### Via Streamlit UI

1. Navigate to `http://localhost:8501`
2. Type a message: *"Where is my order 1001?"*
3. Observe:
   - 💬 Assistant answer
   - 🤖 Model used
   - ⏱️ Latency
   - 🔄 Retries count
   - ↩️ Fallback status

### Via cURL

```bash
curl -X POST http://127.0.0.1:8000/support \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I cancel order 1004?"}'
```

Response:
```json
{
  "answer": "Yes, you can cancel order 1004 before it ships...",
  "intent": "order_cancelled",
  "complexity": "simple",
  "order_id": 1004,
  "confidence": 0.92,
  "needs_human": false,
  "runtime": {
    "model": "gemini-3.1-flash-lite",
    "latency_ms": 980,
    "retries": 0,
    "fallback": false
  }
}
```

### 🔥 Trigger Complex Model (Complex Request)

```bash
curl -X POST http://127.0.0.1:8000/support \
  -H "Content-Type: application/json" \
  -d '{"message": "My order 1003 was cancelled but I was charged. When will I get my money back?"}'
```

Response:
```json
{
  "answer": "I understand your concern. Order 1003 was cancelled and the payment was captured. Refunds are processed within 5 business days...",
  "intent": "order_cancelled",
  "complexity": "complex",
  "order_id": 1003,
  "confidence": 0.89,
  "needs_human": false,
  "runtime": {
    "model": "gemini-3.8-flash",
    "latency_ms": 1500,
    "retries": 0,
    "fallback": false
  }
}
```

Notice: Model is `gemini-3.8-flash` (complex model) due to complexity routing.

### 🧪 Simulate Fallback

1. Set `config.yaml`:
   ```yaml
   demo:
     force_model_failure: true
   ```

2. Send a complex request:
   ```bash
   curl -X POST http://127.0.0.1:8000/support \
     -H "Content-Type: application/json" \
     -d '{"message": "I have a payment problem with order 1004."}'
   ```

3. Response shows:
   ```json
   {
     "runtime": {
       "model": "gemini-3.1-flash-lite",
       "fallback": true,
       "retries": 2
     }
   }
   ```

   The complex model fails, retries fail, then fallback model succeeds.

---





