# 📈 Stock AI Assistant (LangGraph + HITL)

A conversational AI assistant for stock queries and purchases, built with LangGraph, Ollama, and Streamlit. Features a **Human-in-the-Loop (HITL)** approval flow — the AI pauses and asks for your confirmation before executing any stock purchase.

---

## Features

- **Natural language stock queries** — ask about any stock by name or ticker
- **Real-time stock prices** via Alpha Vantage API
- **AI-powered responses** using a local Llama 3.2 model (via Ollama)
- **Human-in-the-Loop approval** — purchases require explicit yes/no confirmation
- **Persistent conversation memory** across interactions within a session

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Llama 3.2 via Ollama (`langchain-ollama`) |
| Agent Framework | LangGraph (StateGraph + ToolNode) |
| HITL | LangGraph `interrupt` + `Command(resume=...)` |
| Memory | LangGraph `MemorySaver` (in-memory checkpointing) |
| Stock Data | Alpha Vantage REST API |
| Frontend | Streamlit |
| Config | `python-dotenv` |

---

## Project Structure

```
Human In A Loop Project/
├── backend/
│   └── chatbot.py        # LangGraph agent, tools, graph definition
├── frontend/
│   └── frontend.py       # Streamlit UI
├── .env                  # API keys (not committed)
├── requirements.txt
└── README.md
```

### Running the App

```bash
streamlit run frontend/frontend.py
```

---

## How It Works

### Normal Query Flow

```
User: "What's the price of TSLA?"
  └─> LLM calls get_stock_price("TSLA")
        └─> Alpha Vantage API returns quote
              └─> LLM formats and returns response
```

### Purchase Flow (HITL)

```
User: "Buy 10 shares of AAPL"
  └─> LLM calls purchase_stock("AAPL", 10)
        └─> Graph pauses via interrupt()
              └─> UI shows approval prompt [✅ Yes] [❌ No]
                    └─> User clicks Yes
                          └─> Graph resumes → Purchase confirmed
```

---

## Available Tools

### `get_stock_price(symbol: str)`
Fetches the latest stock quote for a given ticker symbol using the Alpha Vantage Global Quote endpoint.

### `purchase_stock(symbol: str, quantity: int)`
Initiates a stock purchase. Pauses graph execution and requests human approval via `interrupt()` before proceeding. Returns a success or cancellation message based on the user's decision.

---

## Key Implementation Details

- **Graph checkpointing** — `MemorySaver` persists the graph state, enabling the pause/resume HITL flow across Streamlit reruns.
- **Thread ID** — all interactions use a fixed `thread_id` (`"streamlit-thread"`) to maintain a single conversation session. To support multiple users, generate a unique thread ID per session.
- **`Command(resume=...)`** — when the user approves or rejects a purchase, the frontend sends this command to resume the paused graph from exactly where it left off.

---

## Requirements

```
streamlit
langchain-core
langchain-ollama
langgraph
python-dotenv
requests
```

Generate a `requirements.txt` with:

```bash
pip freeze > requirements.txt
```

---

