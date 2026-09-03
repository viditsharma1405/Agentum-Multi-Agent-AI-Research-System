from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import re

load_dotenv()

# Model
llm = ChatGroq(
    model="allam-2-7b",
    temperature=0,
)


# ── Search Agent — direct tool call, no ReAct loop ────────────────────────────
def build_search_agent():
    class SearchAgent:
        def invoke(self, input_dict):
            query = input_dict["messages"][0][1]
            topic = re.sub(r"Find recent.*?about:\s*", "", query, flags=re.IGNORECASE).strip()
            result = web_search.invoke(topic)
            return {"messages": [result]}
    return SearchAgent()


# ── Reader Agent — direct tool call, no ReAct loop ───────────────────────────
def build_reader_agent():
    class ReaderAgent:
        def invoke(self, input_dict):
            msg = input_dict["messages"][0][1]
            url_match = re.search(r"URL:\s*(https?://\S+)", msg)
            if url_match:
                url = url_match.group(1).strip()
                result = scrape_url.invoke(url)
            else:
                result = "No URL found in search results."
            return {"messages": [result]}
    return ReaderAgent()


# ── Writer chain ──────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise research writer. Write clear, structured reports."),
    ("human", """Write a research report on: {topic}

Research:
{research}

Format:
- Introduction (2-3 sentences)
- Key Findings (3 bullet points)
- Conclusion (2-3 sentences)
- Sources (URLs only)

Be factual and concise."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ── Critic chain ──────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research critic. Be brief and specific."),
    ("human", """Review this report:

{report}

Respond in this format:
Score: X/10
Strengths: (2 bullet points)
Improvements: (2 bullet points)
Verdict: (one line)"""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
