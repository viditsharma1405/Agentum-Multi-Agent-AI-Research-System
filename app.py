import streamlit as st
import time
import groq as groq_lib
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def invoke_with_retry(chain, inputs, max_retries=5):
    """Invoke a chain with automatic retry on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except groq_lib.RateLimitError as e:
            # Parse wait time from error message if available
            wait = 8 * (attempt + 1)
            st.toast(f"Rate limit hit — waiting {wait}s before retry ({attempt+1}/{max_retries})…", icon="⏳")
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded due to rate limiting.")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentum · AI Research Agent",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}
.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 6rem 4rem; max-width: 860px; margin: auto; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 0.9rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.6rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 1rem;
    font-weight: 300;
    color: #a09890;
    max-width: 460px;
    margin: 0 auto;
    line-height: 1.7;
    text-wrap: balance;
    text-align: center;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 1.8rem 0;
}

/* Input wrapper */
.input-wrap {
    max-width: 580px;
    margin: 0 auto 0.5rem;
}

/* Input overrides */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
}

/* Step cards */
.step-card {
    max-width: 580px;
    margin-left: auto;
    margin-right: auto;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.75rem;
}
.step-card.active {
    border-color: rgba(255,140,50,0.35);
    border-left-color: #ff8c32;
    background: rgba(255,140,50,0.04);
}
.step-card.done {
    border-color: rgba(80,200,120,0.25);
    border-left-color: #50c878;
    background: rgba(80,200,120,0.03);
}
.step-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.7;
    min-width: 24px;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.92rem;
    font-weight: 700;
    color: #f0ebe0;
    flex: 1;
}
.step-desc {
    font-size: 0.78rem;
    color: #706860;
    margin-top: 0.2rem;
    padding-left: 2.4rem;
}
.status-waiting { font-family:'DM Mono',monospace; font-size:0.65rem; color:#444; letter-spacing:0.1em; }
.status-running { font-family:'DM Mono',monospace; font-size:0.65rem; color:#ff8c32; letter-spacing:0.1em; }
.status-done    { font-family:'DM Mono',monospace; font-size:0.65rem; color:#50c878; letter-spacing:0.1em; }

/* Section label */
.section-label {
    max-width: 580px;
    margin-left: auto;
    margin-right: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 0.9rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}

/* Report / feedback panels */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #706860 !important;
    letter-spacing: 0.08em !important;
}

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid rgba(255,140,50,0.35) !important;
    color: #ff8c32 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    letter-spacing: 0.08em !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,140,50,0.08) !important;
}

/* Notice */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #3a3530;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}

/* Warning */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Step card helper ──────────────────────────────────────────────────────────
def step_card(num, title, state, desc):
    status_html = {
        "waiting": '<span class="status-waiting">WAITING</span>',
        "running": '<span class="status-running">● RUNNING</span>',
        "done":    '<span class="status-done">✓ DONE</span>',
    }.get(state, "")
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-row">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            {status_html}
        </div>
        <div class="step-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def get_step_state(step):
    r = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]
    if step in r:
        return "done"
    if st.session_state.running:
        for k in steps:
            if k not in r:
                return "running" if k == step else "waiting"
    return "waiting"


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Agent<span>um</span></h1>
    <p style="font-size:1rem;font-weight:300;color:#a09890;max-width:460px;margin:0 auto;line-height:1.7;text-align:center;">
        Four specialized AI agents collaborate — searching, scraping, writing, and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Quantum computing breakthroughs in 2025",
    key="topic_input",
)
run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

# Example chips
st.markdown("""
<div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;margin-bottom:1.8rem;justify-content:center;">
    <span style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#504840;letter-spacing:0.12em;">TRY →</span>
    <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:0.2rem 0.65rem;font-size:0.73rem;color:#a09890;font-family:'DM Sans',sans-serif;">LLM agents 2025</span>
    <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:0.2rem 0.65rem;font-size:0.73rem;color:#a09890;font-family:'DM Sans',sans-serif;">CRISPR gene editing</span>
    <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:0.2rem 0.65rem;font-size:0.73rem;color:#a09890;font-family:'DM Sans',sans-serif;">Fusion energy progress</span>
</div>
""", unsafe_allow_html=True)

# ── Pipeline status ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Pipeline Status</div>', unsafe_allow_html=True)
step_card("01", "Search Agent",  get_step_state("search"), "Gathers recent web information via Tavily")
step_card("02", "Reader Agent",  get_step_state("reader"), "Scrapes & extracts deep content from top URL")
step_card("03", "Writer Chain",  get_step_state("writer"), "Drafts a structured full research report")
step_card("04", "Critic Chain",  get_step_state("critic"), "Reviews, scores and gives feedback on the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = dict(st.session_state.results)
    topic_val = st.session_state.topic_input

    if "search" not in results:
        with st.spinner("🔍  Search Agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)
        st.rerun()

    elif "reader" not in results:
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:500]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)
        st.rerun()

    elif "writer" not in results:
        with st.spinner("✍️  Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search'][:800]}\n\n"
                f"SCRAPED CONTENT:\n{results['reader'][:800]}"
            )
            results["writer"] = invoke_with_retry(writer_chain, {
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)
        st.rerun()

    elif "critic" not in results:
        with st.spinner("🧐  Critic is reviewing the report…"):
            results["critic"] = invoke_with_retry(critic_chain, {
                "report": results["writer"][:1500]
            })
            st.session_state.results = dict(results)
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)"):
            st.text(r["search"])

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)"):
            st.text(r["reader"])

    if "writer" in r:
        st.markdown('<div class="report-panel"><div class="section-label">📝 Final Research Report</div>', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown('<div class="feedback-panel"><div class="section-label" style="color:#50c878;border-color:rgba(80,200,120,0.15);">🧐 Critic Feedback</div>', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    Agentum · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)
