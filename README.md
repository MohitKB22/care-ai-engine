# Healthcare RAG Chatbot — Streamlit

A RAG-powered healthcare chatbot built with Streamlit and the Anthropic Claude API.

## Features

- 4 Knowledge Bases: General Health, Diabetes, Cardiovascular, Mental Health
- Emergency Detection: intercepts life-threatening queries before any API call
- 3 Response Modes: Safe & Cautious · Detailed Explanation · Simple Language
- Multi-turn Memory: last 6 exchanges sent with every request
- Context Grounding: active KB context injected as RAG retrieval into every prompt
- Quick Chips: one-click example questions per KB

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Enter your API key

Enter your Anthropic API key (`sk-ant-...`) in the sidebar when the app loads.  
Get one at: https://console.anthropic.com

## Optional: Real FAISS Retrieval Backend

The original project includes a FastAPI + FAISS backend (`retriever.py`).  
To use real semantic retrieval:

### Install backend dependencies

```bash
pip install fastapi uvicorn faiss-cpu sentence-transformers
```

### Run the retrieval server

```bash
uvicorn retriever:app --reload --port 8000
```

### Connect to Streamlit

In `app.py`, replace the static `kb_data['context']` in `call_anthropic()` with:

```python
import requests
res = requests.get(f"http://localhost:8000/retrieve", params={"kb": st.session_state.active_kb, "q": user_query, "top_k": 5})
context = res.json()["context"]
```

## Security Notes

- Never commit your API key to version control.
- For production, use environment variables or Streamlit secrets:
  ```toml
  # .streamlit/secrets.toml
  ANTHROPIC_API_KEY = "sk-ant-..."
  ```
  Then access with `st.secrets["ANTHROPIC_API_KEY"]` in `app.py`.

## License

MIT — free to use, modify, and distribute.
