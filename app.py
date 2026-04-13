import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import datetime
import json
import time
from pathlib import Path
from knowledge import GP_BHUJ_SYSTEM_PROMPT

# ── Load Environment Variables ────────────────────────────────────────────────
load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GP Bhuj AI Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Helper Functions ──────────────────────────────────────────────────────────
@st.cache_resource
def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def load_css(path: Path) -> None:
    if path.exists():
        st.markdown(
            f"<style>{path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True
        )


def append_message(role: str, content: str) -> None:
    st.session_state.messages.append({
        "role": role,
        "content": content
    })


def groq_chat(client: Groq, model: str, messages: list,
              temperature: float, max_tokens: int, top_p: float) -> str:

    last_error = None

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )
            return response.choices[0].message.content

        except Exception as exc:
            last_error = exc
            time.sleep(0.6 * (2 ** attempt))

    raise last_error


# ── Load CSS ──────────────────────────────────────────────────────────────────
load_css(Path(__file__).with_name("style.css"))

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏛️ GP BHUJ ASSISTANT")
st.caption("Official Digital Inquiry Desk · Government Polytechnic Bhuj")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        font-family:'Orbitron', monospace;
        font-size:0.85rem;
        color:#00d4ff;
        letter-spacing:0.15rem;
        padding:0.5rem 0 1rem 0;
        text-transform:uppercase;
        border-bottom:1px solid rgba(0,212,255,0.2);
        margin-bottom:1rem;
    ">
        🏛️ College Panel
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        font-family:'Rajdhani', sans-serif;
        font-size:0.85rem;
        color:rgba(0,212,255,0.7);
        margin-bottom:1rem;
    ">
        <div style="display:flex; justify-content:space-between; padding:4px 0;">
            <span>STATUS</span>
            <span style="color:#00ff88; font-weight:600;">● ONLINE</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:4px 0;">
            <span>MODEL</span>
            <span style="color:#00d4ff;">LLaMA 3.1</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:4px 0;">
            <span>PROVIDER</span>
            <span style="color:#00d4ff;">Groq</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    persona_style = st.selectbox(
        "Response Style",
        [
            "Campus Guide (Informal)",
            "Admin Office (Formal)",
            "Faculty Advisor"
        ]
    )

    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "Custom"
    ]

    selected_model = st.selectbox("Model", model_options)

    custom_model = ""
    if selected_model == "Custom":
        custom_model = st.text_input(
            "Custom Model ID",
            placeholder="Enter model id..."
        )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1
    )

    top_p = st.slider(
        "Top-p",
        min_value=0.1,
        max_value=1.0,
        value=0.95,
        step=0.05
    )

    max_tokens = st.slider(
        "Max Tokens",
        min_value=64,
        max_value=2048,
        value=512,
        step=64
    )

    api_key_input = st.text_input(
        "Groq API Key",
        type="password"
    )

    api_key = api_key_input.strip() or os.getenv("GROQ_API_KEY", "").strip()
    api_key_ok = bool(api_key)

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    export_payload = {
        "exported_at": datetime.datetime.utcnow().isoformat() + "Z",
        "style": persona_style,
        "model": (custom_model or selected_model).strip(),
        "messages": st.session_state.messages
    }

    st.download_button(
        "⬇️ Export Chat",
        data=json.dumps(export_payload, indent=2),
        file_name="gp_bhuj_chat_export.json",
        mime="application/json",
        disabled=not st.session_state.messages,
        use_container_width=True
    )

# ── API Setup ─────────────────────────────────────────────────────────────────
selected_model_value = (
    custom_model.strip()
    if selected_model == "Custom" and custom_model.strip()
    else selected_model
)

client = get_client(api_key) if api_key_ok else None

# ── System Prompt ─────────────────────────────────────────────────────────────
system_msg = GP_BHUJ_SYSTEM_PROMPT.copy()

STYLES = {
    "Campus Guide (Informal)": (
        " Adopt a friendly and helpful campus guide tone."
    ),
    "Admin Office (Formal)": (
        " Adopt a concise and professional administrative tone."
    ),
    "Faculty Advisor": (
        " Adopt an encouraging and mentorship-oriented tone."
    )
}

system_msg["content"] += STYLES.get(persona_style, "")

# ── Missing API Key Warning ───────────────────────────────────────────────────
if not api_key_ok:
    st.warning("Please enter your Groq API key in the sidebar.")

# ── Chat History ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "👨‍🎓" if msg["role"] == "user" else "🏛️"

    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# ── Welcome Screen (Responsive) ──────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("## 🟢 System Ready")
    st.write(
        "Welcome to the official GP Bhuj AI Assistant. "
        "Ask about departments, admissions, fees, faculty, hostel, "
        "placement, or college facilities."
    )

    st.markdown("### Quick Actions")

    # Mobile-friendly stacked buttons
    if st.button("🎓 Fee Structure", use_container_width=True):
        append_message("user", "Tell me about the fee structure.")
        st.rerun()

    if st.button("🏢 Departments", use_container_width=True):
        append_message("user", "List all departments in GP Bhuj.")
        st.rerun()

    if st.button("👨‍🏫 Faculty", use_container_width=True):
        append_message("user", "Show me the Computer Engineering faculty.")
        st.rerun()

    if st.button("📝 Admission Process", use_container_width=True):
        append_message("user", "Explain the admission process.")
        st.rerun()

# ── Chat Input (Always at Bottom) ────────────────────────────────────────────
user_input = st.chat_input(
    "Ask about departments, fees, admissions, faculty...",
    disabled=not api_key_ok
)

# ── Handle User Input ─────────────────────────────────────────────────────────
if user_input:
    cleaned_input = user_input.strip()

    if not cleaned_input:
        st.warning("Please enter a message.")
        st.stop()

    append_message("user", cleaned_input)

    with st.chat_message("user", avatar="👨‍🎓"):
        st.write(cleaned_input)

    with st.chat_message("assistant", avatar="🏛️"):
        thinking = st.empty()
        thinking.markdown("`PROCESSING REQUEST...`")

        try:
            api_messages = [system_msg] + st.session_state.messages

            reply = groq_chat(
                client=client,
                model=selected_model_value,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            thinking.empty()
            st.write(reply)

            append_message("assistant", reply)

        except Exception as e:
            thinking.empty()
            st.error(f"System Error: {str(e)}")