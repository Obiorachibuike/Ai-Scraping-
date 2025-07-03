

## 🔍 Research Agent with Gemini + Google Search

An intelligent research assistant powered by:

- **Flask** — REST API + HTML UI
- **Streamlit** — Visual research interface
- **LangChain** — Context-aware LLM chaining
- **Google CSE** — Real-time web search
- **FAISS** — Persistent vector memory for retrieval

---

## 📁 Project Structure

```
. 
├── docker-compose.yml 
└── research_agent/ 
    ├── Dockerfile 
    ├── requirements.txt 
    ├── main.py                # Runs Flask + Streamlit 
    ├── agent.py               # Gemini + FAISS logic 
    ├── web_search.py          # Google CSE wrapper 
    ├── streamlit_app.py       # Streamlit frontend 
    ├── templates/ 
    │   └── index.html         # Flask HTML page 
    ├── static/ 
    │   ├── css/styles.css 
    │   └── js/app.js 
    └── knowledge_base/        # Auto-created FAISS index store
```

---

## 🚀 Features

- 💬 LLM research via **Gemini Pro**
- 🔍 Real-time results from **Google Custom Search**
- 🧠 FAISS-powered memory for re-use and context
- 🌐 Dual frontend: HTML (Flask) + UI (Streamlit)
- 🧱 Dockerized for easy deployment

---

## 🔧 Requirements

- Python 3.9+
- Docker & Docker Compose
- Google Developer Keys:
  - `GEMINI_API_KEY`
  - `GOOGLE_API_KEY`
  - `GOOGLE_CSE_ID`

---

## 🔐 API Keys with `.env`

Create a `.env` file inside the `research_agent/` directory:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
```

These will be automatically loaded using python-dotenv.

---

## 🐳 Run with Docker

1. Clone the repo

   ```bash
   git clone https://github.com/your-username/research-agent.git
   cd research-agent
   ```

2. Start the app

   ```bash
   docker-compose up --build
   ```

   > 🔁 On first run, the `knowledge_base/` folder will be created automatically inside the container and mapped locally to persist FAISS data.

---

## 🌐 Access the App

| Component        | URL                       | Description            |
|------------------|---------------------------|------------------------|
| Flask HTML UI    | http://localhost:5000/    | Homepage               |
| Flask API        | http://localhost:5000/api  | Backend endpoints       |
| Streamlit UI     | http://localhost:8501/    | Research dashboard      |

---

## 📡 API Endpoints

### POST /initialize

```json
{
  "gemini_api_key": "your-key",
  "google_api_key": "your-key",
  "google_cse_id": "your-cse-id"
}
```

Initializes the agent with LLM and search credentials.

---

### POST /research

```json
{
  "query": "What are the effects of space travel on human biology?"
}
```

Performs a live search and LLM-based analysis with sources and suggestions.

---

## 📜 requirements.txt

```
flask>=2.0.0
google-api-python-client>=2.0.0
langchain-google-genai>=0.1.0
langchain>=0.1.0
faiss-cpu>=1.7.4
requests>=2.25.0
streamlit>=1.32.0
python-dotenv>=1.0.0
```

---

## 🛠️ Development Tips

### Persistent Knowledge Base

The FAISS vector index is saved in `research_agent/knowledge_base/`. To exclude it from Git:

```gitignore
# .gitignore
research_agent/knowledge_base/
```

---

## 🧠 Roadmap Ideas

- [ ] Upload PDFs or URLs for context-rich research
- [ ] User login & session-based memory
- [ ] Voice interface or mobile-friendly UI
- [ ] Cloud deployment (Render, Railway, Fly.io)

---

## 📜 License

MIT License — feel free to fork, improve, and build on it.

---

## 🙌 Built With

- LangChain
- Gemini
- FAISS
- Streamlit
- Google Custom Search

---

