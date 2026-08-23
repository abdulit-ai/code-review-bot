import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

st.set_page_config(page_title="CODEX · Code Review Bot", page_icon="🔬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
:root {
    --bg:#0f0f13;--surface:#141419;--card:#1a1a22;--border:#252530;
    --border2:#31313f;--cyan:#00e5ff;--cyan2:#00b8d4;--purple:#7c4dff;
    --green:#00e676;--red:#ff1744;--yellow:#ffea00;
    --text:#e0e0ef;--muted:#6060ff80;--mono:'Space Mono',monospace;
    --sans:'Space Grotesk',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[data-testid="stApp"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],.stDeployButton{visibility:hidden!important;display:none!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
.block-container{padding:2rem 2.5rem!important;max-width:1300px!important;}

.codex-header{
    background:var(--surface);border:1px solid var(--border);border-radius:16px;
    padding:1.8rem 2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;
    display:flex;align-items:center;gap:20px;
}
.codex-header::after{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--purple),var(--cyan),var(--green));
}
.codex-logo{
    width:52px;height:52px;border-radius:14px;
    background:linear-gradient(135deg,#7c4dff33,#00e5ff33);
    border:1px solid var(--cyan);
    display:flex;align-items:center;justify-content:center;font-size:24px;
    box-shadow:0 0 20px rgba(0,229,255,0.15);
}
.codex-name{font-size:2rem;font-weight:700;letter-spacing:-0.03em;}
.codex-name span{color:var(--cyan);}
.codex-sub{font-family:var(--mono);font-size:0.68rem;color:#6060aa;margin-top:4px;letter-spacing:0.12em;}

.review-panel{
    background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:1.5rem;height:100%;
}
.panel-label{font-family:var(--mono);font-size:0.62rem;color:var(--cyan);
    letter-spacing:0.18em;text-transform:uppercase;margin-bottom:12px;
    display:flex;align-items:center;gap:8px;
}
.panel-label::before{content:'';width:6px;height:6px;border-radius:50%;
    background:var(--cyan);box-shadow:0 0 8px var(--cyan);}

.issue-card{
    border:1px solid var(--border);border-radius:10px;padding:12px 16px;
    margin-bottom:10px;transition:border-color 0.2s;
}
.issue-critical{border-left:3px solid var(--red)!important;}
.issue-warning {border-left:3px solid var(--yellow)!important;}
.issue-info    {border-left:3px solid var(--cyan)!important;}
.issue-good    {border-left:3px solid var(--green)!important;}
.issue-badge{
    display:inline-block;font-family:var(--mono);font-size:0.6rem;
    padding:2px 8px;border-radius:4px;margin-bottom:6px;font-weight:700;
}
.badge-critical{background:#ff174422;color:var(--red);}
.badge-warning{background:#ffea0022;color:var(--yellow);}
.badge-info{background:#00e5ff22;color:var(--cyan);}
.badge-good{background:#00e67622;color:var(--green);}
.issue-text{font-size:0.85rem;color:var(--text);line-height:1.5;}
.issue-fix{font-family:var(--mono);font-size:0.75rem;color:#9090cc;margin-top:6px;}

.score-ring{
    width:90px;height:90px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;flex-direction:column;
    border:3px solid;margin:0 auto 1rem;
}
.score-num{font-size:1.6rem;font-weight:700;font-family:var(--mono);}
.score-lbl{font-size:0.55rem;letter-spacing:0.1em;color:#6060aa;}

.stTextArea textarea{background:var(--card)!important;border:1px solid var(--border)!important;
    border-radius:10px!important;color:var(--text)!important;font-family:var(--mono)!important;
    font-size:0.82rem!important;}
.stTextArea textarea:focus{border-color:var(--cyan)!important;box-shadow:0 0 0 2px rgba(0,229,255,0.1)!important;}
.stSelectbox>div>div{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
.stButton>button{background:linear-gradient(135deg,var(--purple),var(--cyan))!important;
    color:#0f0f13!important;border:none!important;border-radius:8px!important;
    font-family:var(--sans)!important;font-weight:700!important;font-size:0.85rem!important;
    padding:0.55rem 1.4rem!important;box-shadow:0 4px 16px rgba(0,229,255,0.2)!important;
    transition:all 0.2s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(0,229,255,0.35)!important;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {"api_ready": False, "reviews": [], "last_result": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 CODEX Settings")
    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza…")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.session_state.api_ready = True
            st.success("✓ Connected", icon="🟢")
        except Exception:
            st.error("Invalid key")
    st.markdown("---")
    model = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    review_focus = st.multiselect(
        "Review focus",
        ["Bugs & errors", "Security vulnerabilities", "Performance",
         "Code style & readability", "Best practices", "Test coverage",
         "Documentation", "Complexity"],
        default=["Bugs & errors", "Security vulnerabilities", "Performance", "Code style & readability"],
    )
    strictness = st.select_slider("Strictness", ["Lenient", "Balanced", "Strict", "Senior Engineer"], value="Balanced")
    st.markdown("---")
    st.metric("Reviews Done", len(st.session_state.reviews))
    if st.button("Clear History", use_container_width=True):
        st.session_state.reviews = []
        st.session_state.last_result = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="codex-header">
  <div class="codex-logo">🔬</div>
  <div>
    <div class="codex-name">CODE<span>X</span></div>
    <div class="codex-sub">AI-POWERED CODE REVIEW BOT · FINDS BUGS BEFORE PRODUCTION DOES</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown('<div class="review-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Code Input</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["Python", "JavaScript", "TypeScript", "Java",
                                          "C++", "Go", "Rust", "SQL", "Bash", "Other"])
    code_input = st.text_area("Paste your code here", height=320,
                               placeholder="def calculate_discount(price, discount):\n    return price - discount\n\nresult = calculate_discount('100', 20)\nprint(result)")
    context = st.text_input("Context (optional)", placeholder="e.g. This is an e-commerce checkout function…")

    if st.button("🔬 Run Code Review", use_container_width=True):
        if not code_input.strip():
            st.warning("Paste some code first.")
        elif not st.session_state.api_ready:
            st.error("Add your Gemini API key in the sidebar.")
        else:
            focus_str = ", ".join(review_focus) if review_focus else "general quality"
            with st.spinner("Analysing code…"):
                prompt = f"""You are a {strictness}-level code reviewer. Review the following {language} code.
Focus areas: {focus_str}
{f'Context: {context}' if context else ''}

Return ONLY a JSON object in this exact format:
{{
  "score": <0-100 integer>,
  "grade": "<A+|A|B|C|D|F>",
  "summary": "<2 sentence overall assessment>",
  "issues": [
    {{
      "severity": "<critical|warning|info|good>",
      "category": "<category>",
      "title": "<short title>",
      "description": "<detailed explanation>",
      "suggestion": "<how to fix or improve>"
    }}
  ],
  "refactored_snippet": "<improved version of the most critical part, or empty string>"
}}

Code to review:
```{language.lower()}
{code_input}
```"""
                try:
                    model_obj = genai.GenerativeModel(
                        model,
                        generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=3000),
                    )
                    raw = model_obj.generate_content(prompt).text
                    import re
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if match:
                        result = json.loads(match.group())
                        st.session_state.last_result = result
                        st.session_state.reviews.append({
                            "lang": language, "score": result.get("score", 0),
                            "time": datetime.now().strftime("%H:%M"),
                            "code": code_input[:100],
                        })
                        st.rerun()
                    else:
                        st.error("Could not parse review. Try again.")
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Output ────────────────────────────────────────────────────────────────────
with col_out:
    st.markdown('<div class="review-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Review Results</div>', unsafe_allow_html=True)

    result = st.session_state.last_result
    if result:
        score = result.get("score", 0)
        grade = result.get("grade", "?")
        color = "#00e676" if score >= 80 else "#ffea00" if score >= 60 else "#ff1744"
        st.markdown(f"""
        <div class="score-ring" style="border-color:{color}">
            <div class="score-num" style="color:{color}">{score}</div>
            <div class="score-lbl">QUALITY SCORE</div>
        </div>
        <div style="text-align:center;margin-bottom:1rem;">
            <span style="font-size:1.5rem;font-weight:700;color:{color}">{grade}</span>
            <span style="font-family:'Space Mono',monospace;font-size:0.7rem;color:#6060aa;margin-left:8px;">GRADE</span>
        </div>
        <div style="font-size:0.85rem;color:#9090cc;margin-bottom:1.2rem;line-height:1.6;padding:12px;background:#1a1a22;border-radius:8px;">
            {result.get('summary','')}
        </div>
        """, unsafe_allow_html=True)

        severity_map = {
            "critical": ("badge-critical", "issue-critical", "🔴 CRITICAL"),
            "warning":  ("badge-warning",  "issue-warning",  "🟡 WARNING"),
            "info":     ("badge-info",     "issue-info",     "🔵 INFO"),
            "good":     ("badge-good",     "issue-good",     "🟢 GOOD"),
        }
        for issue in result.get("issues", []):
            sev = issue.get("severity", "info").lower()
            badge_cls, card_cls, label = severity_map.get(sev, ("badge-info", "issue-info", "🔵 INFO"))
            st.markdown(f"""
            <div class="issue-card {card_cls}">
                <div class="issue-badge {badge_cls}">{label} · {issue.get('category','')}</div>
                <div class="issue-text"><strong>{issue.get('title','')}</strong><br>{issue.get('description','')}</div>
                <div class="issue-fix">💡 {issue.get('suggestion','')}</div>
            </div>
            """, unsafe_allow_html=True)

        if result.get("refactored_snippet"):
            with st.expander("✨ View Suggested Refactor"):
                st.code(result["refactored_snippet"], language=language.lower())

        export = json.dumps(result, indent=2)
        st.download_button("⬇ Export Review (JSON)", data=export,
                           file_name=f"review_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                           mime="application/json")
    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#404060;">
            <div style="font-size:3rem">🔬</div>
            <div style="font-family:'Space Mono',monospace;font-size:0.75rem;margin-top:12px;">
                Paste code and click Review<br>to see results here
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.reviews:
    with st.expander(f"📋 Review History ({len(st.session_state.reviews)})"):
        for r in reversed(st.session_state.reviews):
            color = "#00e676" if r['score'] >= 80 else "#ffea00" if r['score'] >= 60 else "#ff1744"
            st.markdown(f"""
            <div style="display:flex;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid #252530;">
                <span style="font-family:'Space Mono',monospace;font-size:0.7rem;color:{color};font-weight:700">{r['score']}/100</span>
                <span style="font-size:0.8rem;color:#9090cc">{r['lang']}</span>
                <span style="font-size:0.78rem;color:#6060aa;flex:1">{r['code']}…</span>
                <span style="font-family:'Space Mono',monospace;font-size:0.65rem;color:#404060">{r['time']}</span>
            </div>
            """, unsafe_allow_html=True)
