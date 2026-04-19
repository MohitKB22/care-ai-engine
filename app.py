import streamlit as st
import requests
import json

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="HealthRAG Chatbot",
    page_icon="🏥",
    layout="wide",
)

OLLAMA_URL = "http://localhost:11434"

# ── Knowledge Bases ────────────────────────────────────────
KNOWLEDGE_BASES = {
    "general": {
        "name": "General Health",
        "emoji": "🩺",
        "color": "#4A7CFF",
        "chips": [
            "What vitamins should I take daily?",
            "How much water should I drink?",
            "How do I improve sleep quality?",
        ],
        "context": """General Health Knowledge Base:
- Adults need 7-9 hours of sleep per night. Poor sleep is linked to obesity, heart disease, and impaired immunity.
- Daily water intake: ~3.7L for men, ~2.7L for women (includes food water). Thirst is a reliable guide.
- Key vitamins: D3 (sunlight/supplements), B12 (especially vegetarians), Iron (women), Omega-3 (fish/flaxseed).
- Regular exercise: 150 min moderate aerobic + 2 strength sessions/week reduces chronic disease risk by 30%.
- Preventive screenings: blood pressure (adults 18+), cholesterol (20+), diabetes (45+ or overweight).
- BMI 18.5–24.9 is normal; waist >35in (women) or >40in (men) signals metabolic risk.
- Smoking cessation reduces heart disease risk by 50% within one year of quitting.
- Annual check-ups help catch hypertension, pre-diabetes, and high cholesterol early.""",
    },
    "diabetes": {
        "name": "Diabetes",
        "emoji": "🩸",
        "color": "#1D9E75",
        "chips": [
            "What are early signs of diabetes?",
            "How do I manage blood sugar?",
            "What foods should diabetics avoid?",
        ],
        "context": """Diabetes Knowledge Base:
- Type 1: autoimmune, insulin-dependent, onset usually childhood. Type 2: insulin resistance, often lifestyle-related, 90% of cases.
- Early symptoms: polyuria (frequent urination), polydipsia (excess thirst), unexplained weight loss, blurred vision, slow-healing wounds.
- Normal fasting blood glucose: 70–99 mg/dL. Prediabetes: 100–125. Diabetes: ≥126 mg/dL on two tests.
- HbA1c target for diabetics: <7%. Tested every 3 months. Reflects 3-month average blood sugar.
- Foods to limit: white bread, sugary drinks, processed snacks, high-GI foods. Prefer: leafy greens, legumes, whole grains, berries.
- Medications: Metformin (first-line T2D), GLP-1 agonists (semaglutide), SGLT2 inhibitors, insulin therapy for T1D.
- Exercise improves insulin sensitivity; 30 min/day walking can reduce T2D risk by 30%.
- Complications: neuropathy, retinopathy, nephropathy, cardiovascular disease. Regular foot checks, eye exams, kidney panels essential.
- Hypoglycemia (<70 mg/dL): symptoms include shakiness, sweating, confusion. Treat with 15g fast carbs.""",
    },
    "cardio": {
        "name": "Cardiovascular",
        "emoji": "❤️",
        "color": "#D85A30",
        "chips": [
            "What are heart attack warning signs?",
            "How to lower blood pressure naturally?",
            "What is a heart-healthy diet?",
        ],
        "context": """Cardiovascular Health Knowledge Base:
- Heart attack signs: chest pain/pressure, left arm/jaw pain, shortness of breath, sweating, nausea. Call emergency services immediately.
- Normal BP: <120/80 mmHg. Stage 1 HTN: 130–139/80–89. Stage 2: ≥140/90. Hypertensive crisis: >180/120.
- DASH diet: rich in fruits, vegetables, whole grains, lean protein, low-fat dairy. Limit sodium <2.3g/day.
- Statins (atorvastatin, rosuvastatin) reduce LDL. Target LDL for high-risk patients: <70 mg/dL.
- Exercise: 150 min/week moderate cardio lowers resting HR and BP. Daily 30-min walks reduce cardiac events by 20%.
- Atrial fibrillation: irregular pulse, palpitations, fatigue. Risk of stroke — anticoagulation therapy often needed.
- Cholesterol targets: total <200, LDL <100, HDL >60 (protective), triglycerides <150.
- Stress, smoking, obesity, family history, and diabetes are major modifiable cardiac risk factors.""",
    },
    "mental": {
        "name": "Mental Health",
        "emoji": "🧠",
        "color": "#7F77DD",
        "chips": [
            "What are symptoms of anxiety?",
            "How can I manage stress better?",
            "When should I see a therapist?",
        ],
        "context": """Mental Health Knowledge Base:
- Depression symptoms: persistent low mood, loss of interest (anhedonia), fatigue, sleep changes, concentration issues, lasting ≥2 weeks.
- Anxiety disorders: GAD, panic disorder, social anxiety, phobias. Symptoms: excessive worry, restlessness, muscle tension, insomnia.
- CBT (Cognitive Behavioral Therapy) is first-line for depression and anxiety. Highly effective in 8–16 sessions.
- SSRIs (sertraline, fluoxetine) often prescribed alongside therapy. Takes 4–6 weeks for full effect.
- Stress management: regular exercise, mindfulness/meditation (reduces cortisol), social support, sleep hygiene, journaling.
- Signs to seek help: thoughts of self-harm, inability to function in daily life, substance abuse, relationship breakdown.
- Psychosis warning signs: hallucinations, delusions, disorganized thinking — requires urgent psychiatric evaluation.
- Sleep and mental health are bidirectional: poor sleep worsens mood, anxiety amplifies insomnia.
- PTSD: flashbacks, hypervigilance, avoidance after trauma. EMDR and trauma-focused CBT are evidence-based treatments.""",
    },
}

# ── Emergency detection ────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "chest tightness", "heart attack", "cardiac arrest",
    "can't breathe", "cannot breathe", "difficulty breathing", "not breathing",
    "stopped breathing", "no pulse", "stroke", "face drooping", "arm weakness",
    "speech difficulty", "sudden severe headache", "unconscious", "unresponsive",
    "collapsed", "seizure", "convulsion", "suicidal", "suicide", "kill myself",
    "want to die", "end my life", "self harm", "self-harm", "cutting myself",
    "hurt myself", "severe bleeding", "overdose", "poisoning", "swallowed something",
    "anaphylaxis", "severe allergic reaction", "throat closing", "epipen",
    "heavy bleeding pregnancy", "baby not moving",
]

def is_emergency(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in EMERGENCY_KEYWORDS)

# ── System prompts ─────────────────────────────────────────
SYSTEM_PROMPTS = {
    "safe": "You are a cautious healthcare assistant. Always remind users to consult a doctor for personal medical decisions. Avoid making definitive diagnoses. Use hedging language such as 'may,' 'could,' or 'it's possible.' End every response with a brief recommendation to seek professional advice. Keep answers under 150 words.",
    "detailed": "You are a knowledgeable healthcare assistant providing detailed, evidence-based medical information. Use clinical terminology accompanied by clear plain-English explanations. Structure responses with relevant clinical detail. Note that this is informational only and not a substitute for professional care. Keep answers under 220 words.",
    "simple": "You are a friendly healthcare helper who explains things in very simple, everyday language. Avoid medical jargon entirely. Use short sentences and bullet points where helpful. Imagine you are explaining to someone with no medical background. Always suggest talking to a doctor for personal advice. Keep answers under 130 words.",
}

MODE_LABELS = {
    "safe": "🛡️ Safe & Cautious",
    "detailed": "🔬 Detailed Explanation",
    "simple": "💬 Simple Language",
}

# ── Ollama helpers ─────────────────────────────────────────
def get_ollama_models():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            return models
        return []
    except Exception:
        return []

def ollama_running():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def call_ollama(model: str, user_query: str) -> str:
    kb_data = KNOWLEDGE_BASES[st.session_state.active_kb]
    system = (
        SYSTEM_PROMPTS[st.session_state.mode]
        + f"\n\nYou have access to the following retrieved knowledge base context. Ground your answer in this context:\n\n"
        f"--- RETRIEVED CONTEXT ({kb_data['name']}) ---\n{kb_data['context']}\n--- END CONTEXT ---\n\n"
        f"If the user's question falls outside the retrieved context, answer helpfully from general medical knowledge but note that it's outside the current knowledge base focus."
    )

    # Build messages (last 12 turns)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("user", "assistant")
    ][-12:]

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + history,
        "stream": False,
    }

    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]

# ── Session state init ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_kb" not in st.session_state:
    st.session_state.active_kb = "general"
if "mode" not in st.session_state:
    st.session_state.mode = "safe"

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0F1117; }
[data-testid="stSidebar"] { background: #1A1D27 !important; }
[data-testid="stSidebar"] * { color: #CDD0D8 !important; }

.emergency-box {
    background: #2D1212;
    border: 1.5px solid #E24B4A;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 8px 0;
    color: #F5A0A0 !important;
    font-size: 0.97rem;
    line-height: 1.7;
}
.user-bubble {
    background: #1E3A5F;
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px;
    margin: 6px 0 6px auto;
    max-width: 75%;
    color: #E8EDF5;
    font-size: 0.97rem;
    line-height: 1.55;
}
.bot-bubble {
    background: #1E2130;
    border: 1px solid #2A2E42;
    border-radius: 4px 14px 14px 14px;
    padding: 12px 16px;
    margin: 6px auto 6px 0;
    max-width: 80%;
    color: #CDD0D8;
    font-size: 0.97rem;
    line-height: 1.6;
}
.kb-badge {
    font-size: 0.72rem;
    color: #8A90A2;
    margin-bottom: 5px;
    letter-spacing: 0.03em;
}
.status-ok {
    background: #0D2B1A;
    border: 1px solid #1D9E75;
    border-radius: 8px;
    padding: 8px 12px;
    color: #4FD3A0 !important;
    font-size: 0.82rem;
}
.status-err {
    background: #2D1212;
    border: 1px solid #E24B4A;
    border-radius: 8px;
    padding: 8px 12px;
    color: #F5A0A0 !important;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 HealthRAG")
    st.markdown("*Local RAG chatbot — no API key required.*")
    st.divider()

    # Ollama status
    running = ollama_running()
    models = get_ollama_models() if running else []

    if running and models:
        st.markdown(
            f'<div class="status-ok">✅ Ollama running &nbsp;|&nbsp; {len(models)} model(s) found</div>',
            unsafe_allow_html=True,
        )
    elif running and not models:
        st.markdown(
            '<div class="status-err">⚠️ Ollama running but no models pulled.<br>'
            'Run: <code>ollama pull llama3.2</code></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-err">❌ Ollama not detected.<br>'
            'Install from <strong>ollama.com</strong> and run <code>ollama serve</code></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Model selector
    st.markdown("**Model**")
    if models:
        selected_model = st.selectbox(
            "Model",
            options=models,
            label_visibility="collapsed",
            key="selected_model",
        )
    else:
        st.selectbox("Model", options=["(none available)"], label_visibility="collapsed", disabled=True)
        selected_model = None

    st.divider()

    # Knowledge Base
    st.markdown("**Knowledge Base**")
    kb_options = {k: f"{v['emoji']} {v['name']}" for k, v in KNOWLEDGE_BASES.items()}
    selected_kb = st.radio(
        "KB",
        options=list(kb_options.keys()),
        format_func=lambda k: kb_options[k],
        index=list(kb_options.keys()).index(st.session_state.active_kb),
        label_visibility="collapsed",
    )
    if selected_kb != st.session_state.active_kb:
        st.session_state.active_kb = selected_kb
        st.rerun()

    st.divider()

    # Response Mode
    st.markdown("**Response Mode**")
    selected_mode = st.selectbox(
        "Mode",
        options=list(MODE_LABELS.keys()),
        format_func=lambda m: MODE_LABELS[m],
        index=list(MODE_LABELS.keys()).index(st.session_state.mode),
        label_visibility="collapsed",
    )
    st.session_state.mode = selected_mode

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.markdown(
        '<p style="color:#E24B4A;font-size:0.82rem;">⚠️ For emergencies call <strong>112</strong></p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#5A5F72;font-size:0.75rem;">Informational only — not a substitute for medical advice.</p>',
        unsafe_allow_html=True,
    )

# ── Main area ──────────────────────────────────────────────
kb = KNOWLEDGE_BASES[st.session_state.active_kb]

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"### {kb['emoji']} {kb['name']} Knowledge Base")
with col2:
    st.markdown(
        f'<div style="text-align:right;padding-top:8px;color:{kb["color"]};font-size:0.8rem;font-weight:600;">'
        f'{MODE_LABELS[st.session_state.mode]}</div>',
        unsafe_allow_html=True,
    )

# Quick chips
st.markdown("**Quick questions:**")
chip_cols = st.columns(len(kb["chips"]))
chip_clicked = None
for i, chip in enumerate(kb["chips"]):
    with chip_cols[i]:
        if st.button(chip, key=f"chip_{i}_{st.session_state.active_kb}"):
            chip_clicked = chip

# ── Chat history ───────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        f'<div class="bot-bubble">'
        f'<div class="kb-badge">{kb["name"]} KB</div>'
        f"Hello! I'm your local Healthcare Assistant powered by Ollama — running entirely on your machine, no internet needed.<br><br>"
        f"Select a knowledge base and response mode from the sidebar, then ask me anything about health and wellness.<br><br>"
        f"For emergencies, always call <strong>112</strong> or go to your nearest hospital."
        f"</div>",
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif msg["role"] == "emergency":
        st.markdown(
            f'<div class="emergency-box">'
            f"🚨 <strong>Emergency Detected</strong><br><br>"
            f"Based on your message, this may be a <strong>medical emergency</strong>. Please act immediately:<br><br>"
            f"• <strong>Call 112</strong> (or your local emergency number) right now<br>"
            f"• Go to your nearest <strong>Emergency Room</strong><br>"
            f"• Do <strong>not</strong> drive yourself — call for help or ask someone nearby<br><br>"
            f"<strong>Mental health crisis?</strong><br>"
            f"• iCall (India): <strong>9152987821</strong><br>"
            f"• Vandrevala Foundation: <strong>1860-2662-345</strong> (24/7)<br><br>"
            f"<em>Please seek immediate professional help. I am not equipped to handle emergencies.</em>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        badge = msg.get("badge", kb["name"])
        st.markdown(
            f'<div class="bot-bubble">'
            f'<div class="kb-badge">{badge}</div>'
            f'{msg["content"]}'
            f"</div>",
            unsafe_allow_html=True,
        )

# ── Handle send ────────────────────────────────────────────
def handle_send(text: str):
    text = text.strip()
    if not text:
        return
    if not running:
        st.error("❌ Ollama is not running. Please start it with `ollama serve`.")
        return
    if not selected_model:
        st.error("❌ No model available. Run `ollama pull llama3.2` in your terminal.")
        return

    st.session_state.messages.append({"role": "user", "content": text})

    if is_emergency(text):
        st.session_state.messages.append({"role": "emergency", "content": ""})
        st.rerun()
        return

    with st.spinner(f"🤔 Thinking with **{selected_model}**…"):
        try:
            reply = call_ollama(selected_model, text)
            badge = f"{kb['name']} KB · {MODE_LABELS[st.session_state.mode]} · {selected_model}"
            st.session_state.messages.append({"role": "assistant", "content": reply, "badge": badge})
        except requests.exceptions.Timeout:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⏱️ <strong>Timeout:</strong> The model took too long to respond. Try a smaller/faster model.",
                "badge": "Error",
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ <strong>Error:</strong> {str(e)}",
                "badge": "Error",
            })

    st.rerun()

if chip_clicked:
    handle_send(chip_clicked)

user_input = st.chat_input("Ask a health question…")
if user_input:
    handle_send(user_input)

