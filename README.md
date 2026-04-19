# Healthcare RAG Chatbot — Ollama (No API Key Required)

A fully local RAG-powered healthcare chatbot using **Streamlit** + **Ollama**.  
No API key, no internet connection needed after setup, completely free.

---

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed on your machine

---

## Setup

### 1. Install Ollama

Download and install from **https://ollama.com/download**

### 2. Pull a model

```bash
# Recommended (fast, good quality, ~2GB)
ollama pull llama3.2

# Lighter option (~1GB, faster on low-RAM machines)
ollama pull llama3.2:1b

# More capable option (~4.7GB)
ollama pull llama3.1:8b

# Medical-focused (optional)
ollama pull medllama2
```

### 3. Start Ollama

```bash
ollama serve
```

> Ollama runs on `http://localhost:11434` by default.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## Features

| Feature | Details |
|---|---|
| 🔒 100% Local | No data leaves your machine |
| 🆓 Free | No API key, no account needed |
| 🩺 4 Knowledge Bases | General Health, Diabetes, Cardiovascular, Mental Health |
| 🚨 Emergency Detection | Intercepts life-threatening queries before LLM call |
| 🔄 3 Response Modes | Safe & Cautious · Detailed Explanation · Simple Language |
| 🧠 Multi-turn Memory | Last 6 exchanges sent with every request |
| ⚡ Quick Chips | One-click example questions per KB |
| 🤖 Model Selector | Switch between any locally pulled Ollama model |

---

## Recommended Models

| Model | Size | Best For |
|---|---|---|
| `llama3.2` | ~2GB | Best balance of speed and quality |
| `llama3.2:1b` | ~1GB | Low-RAM machines |
| `llama3.1:8b` | ~4.7GB | More detailed answers |
| `mistral` | ~4GB | Alternative quality model |
| `phi3` | ~2.3GB | Fast, lightweight |

---

## Troubleshooting

**Ollama not detected?**
- Make sure Ollama is installed and running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`

**No models found?**
- Pull a model first: `ollama pull llama3.2`

**Response too slow?**
- Use a smaller model like `llama3.2:1b`
- Close other heavy applications to free up RAM

**Port conflict?**
- If port 11434 is in use, set `OLLAMA_HOST=0.0.0.0:11435` before `ollama serve`
- Update `OLLAMA_URL` in `app.py` to match

---

## Security & Privacy

- All processing is local — no queries or responses leave your machine.
- No API keys, no accounts, no telemetry from this app.
- Ollama itself may have its own telemetry settings (see Ollama docs).

---

## License

MIT — free to use, modify, and distribute.
