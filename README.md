# Agentum 🔬

A multi-agent AI research system that autonomously searches the web, scrapes content, writes a structured report, and critiques it — all in one pipeline. Built with LangChain, Groq, Tavily, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![LangChain](https://img.shields.io/badge/LangChain-Agents-green)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)

---

## What it does

Enter any research topic and four specialized AI agents collaborate to deliver a polished research report:

| Step | Agent | Role |
|------|-------|------|
| 1 | **Search Agent** | Queries the web via Tavily and collects recent, relevant results |
| 2 | **Reader Agent** | Picks the most relevant URL and scrapes deep content from it |
| 3 | **Writer Chain** | Synthesizes all gathered research into a structured report |
| 4 | **Critic Chain** | Reviews the report, scores it, and gives actionable feedback |

---

## Demo

```
Topic: "LLM agents 2025"

→ Search Agent finds top 3 sources
→ Reader Agent scrapes the most relevant page
→ Writer drafts: Introduction, Key Findings, Conclusion, Sources
→ Critic scores: 8/10 with strengths and improvements
→ Download report as .md
```

---

## Project Structure

```
Agentum/
├── app.py            # Streamlit UI — pipeline orchestration and display
├── agents.py         # Agent and chain definitions (Search, Reader, Writer, Critic)
├── tools.py          # LangChain tools (web_search, scrape_url)
├── pipeline.py       # CLI version of the pipeline (terminal use)
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── .gitignore
```

---

## Tech Stack

- **[LangChain](https://langchain.com)** — agent framework and chain orchestration
- **[Groq](https://groq.com)** — fast LLM inference (`qwen/qwen3.8-27b`)
- **[Tavily](https://tavily.com)** — real-time web search API
- **[Streamlit](https://streamlit.io)** — interactive web UI
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** — HTML scraping and parsing

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/viditsharma1405/Agentum.git
cd Agentum
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
TAVILY_API_KEY=your_tavily_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

- Get a free Tavily key at: https://app.tavily.com
- Get a free Groq key at: https://console.groq.com

### 5. Run the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## CLI Usage

You can also run the pipeline directly from the terminal without the UI:

```bash
python pipeline.py
```

It will prompt you to enter a topic and print all results to the console.

---

## How the Pipeline Works

```
User Input (topic)
       │
       ▼
 ┌─────────────┐
 │ Search Agent │  ── Tavily web search (top 3 results)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ Reader Agent │  ── Scrapes most relevant URL (BeautifulSoup)
 └──────┬──────┘
        │
        ▼
 ┌──────────────┐
 │ Writer Chain  │  ── LLM drafts full structured report
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ Critic Chain  │  ── LLM reviews, scores, gives feedback
 └──────────────┘
        │
        ▼
  Final Report + Feedback (downloadable .md)
```

---

## Environment Variables

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `GROQ_API_KEY` | Groq LLM API key | https://console.groq.com |
| `TAVILY_API_KEY` | Tavily search API key | https://app.tavily.com |

---

## Features

- Real-time pipeline status with animated step cards in the UI
- Download the final report as a `.md` file
- Expandable raw outputs for Search and Reader results
- Critic scoring with strengths and improvement areas
- Works fully on free API tiers (Groq + Tavily)

---

## License

MIT
