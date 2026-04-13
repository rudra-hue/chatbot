import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import datetime
import json
import time
from pathlib import Path
from knowledge import GP_BHUJ_SYSTEM_PROMPT

# Load environment variables
load_dotenv()


st.set_page_config(page_title="GP Bhuj AI Assistant", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")


@st.cache_resource
def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def load_css(path: Path) -> None:
    if path.exists():
        st.markdown(f"<style>{path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def append_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})





def groq_chat(client: Groq, model: str, messages: list, temperature: float, max_tokens: int, top_p: float) -> str:
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


load_css(Path(__file__).with_name("style.css"))

# ── College Header ─────────────────────────────────────────────────────────────
st.title("🏛️ GP BHUJ ASSISTANT")
st.caption("Official Digital Inquiry Desk · Government Polytechnic Bhuj")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.85rem; color:#00d4ff;
                letter-spacing:0.15rem; padding:0.5rem 0 1rem 0; text-transform:uppercase;
                border-bottom:1px solid rgba(0,212,255,0.2); margin-bottom:1rem;">
        🏛️ College Panel
    </div>
    """, unsafe_allow_html=True)

    # System status indicators
    st.markdown("""
    <div style="font-family:'Rajdhani',sans-serif; font-size:0.85rem; color:rgba(0,212,255,0.7); margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(0,212,255,0.1);">
            <span>STATUS</span>
            <span style="color:#00ff88; font-weight:600;">● ONLINE</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(0,212,255,0.1);">
            <span>MODEL</span>
            <span style="color:#00d4ff;">LLaMA 3.1</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(0,212,255,0.1);">
            <span>PROVIDER</span>
            <span style="color:#00d4ff;">Groq</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(0,212,255,0.1);">
            <span>VERSION</span>
            <span style="color:#00d4ff;">8B Instant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Persona mode (Simplified for College)
    st.markdown("""<div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(0,212,255,0.5);
                letter-spacing:0.1rem; margin-bottom:0.4rem; text-transform:uppercase;">Response Style</div>""",
                unsafe_allow_html=True)
    persona_style = st.selectbox("", ["Campus Guide (Informal)", "Admin Office (Formal)", "Faculty Advisor"], label_visibility="collapsed")

    st.markdown("""<div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(0,212,255,0.5);
                letter-spacing:0.1rem; margin:1rem 0 0.4rem 0; text-transform:uppercase;">Model</div>""",
                unsafe_allow_html=True)
    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "Custom"
    ]
    selected_model = st.selectbox("", model_options, label_visibility="collapsed")
    custom_model = ""
    if selected_model == "Custom":
        custom_model = st.text_input("Custom model", value="", placeholder="enter model id", label_visibility="collapsed")

    st.markdown("""<div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(0,212,255,0.5);
                letter-spacing:0.1rem; margin:1rem 0 0.4rem 0; text-transform:uppercase;">Generation</div>""",
                unsafe_allow_html=True)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.7, step=0.1)
    top_p = st.slider("Top-p", min_value=0.1, max_value=1.0, value=0.95, step=0.05)
    max_tokens = st.slider("Max tokens", min_value=64, max_value=2048, value=512, step=64)

    st.markdown("""<div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(0,212,255,0.5);
                letter-spacing:0.1rem; margin:1rem 0 0.4rem 0; text-transform:uppercase;">API Key</div>""",
                unsafe_allow_html=True)
    api_key_input = st.text_input("Groq API key", type="password", label_visibility="collapsed")
    api_key = api_key_input.strip() or os.getenv("GROQ_API_KEY", "").strip()
    api_key_ok = bool(api_key)

    st.markdown("""<div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:rgba(0,212,255,0.5);
                letter-spacing:0.1rem; margin:1rem 0 0.4rem 0; text-transform:uppercase;">Controls</div>""",
                unsafe_allow_html=True)
    if st.button("🧹 CLEAR CHAT"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Message counter
    msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.markdown(f"""
    <div style="font-family:'Rajdhani',sans-serif; font-size:0.85rem; color:rgba(0,212,255,0.7);
                background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.15);
                border-radius:8px; padding:0.6rem 1rem; margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between;">
            <span>Queries Processed</span>
            <span style="color:#00d4ff; font-weight:700; font-family:'Orbitron',monospace;">{msg_count:03d}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    export_payload = {
        "exported_at": datetime.datetime.utcnow().isoformat() + "Z",
        "style": persona_style,
        "model": (custom_model or selected_model).strip(),
        "messages": st.session_state.get("messages", [])
    }
    st.download_button(
        "⬇️ EXPORT CHAT",
        data=json.dumps(export_payload, indent=2),
        file_name="jarvis_chat_export.json",
        mime="application/json",
        disabled=not st.session_state.get("messages")
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Rajdhani',sans-serif; font-size:0.7rem; color:rgba(0,212,255,0.3);
                text-align:center; letter-spacing:0.05rem;">
        GOVERNMENT POLYTECHNIC BHUJ © 2026<br>KUTCH, GUJARAT
    </div>
    """, unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Use the predefined system prompt from knowledge.py
system_msg = GP_BHUJ_SYSTEM_PROMPT.copy()

# Add style modifier to system prompt
STYLES = {
    "Campus Guide (Informal)": " Adopt a friendly, helpful campus guide tone. Use emojis where appropriate. Focus on making the student feel comfortable.",
    "Admin Office (Formal)": " Adopt a professional, concise, and formal administrative tone. Stick strictly to facts and procedures.",
    "Faculty Advisor": " Adopt an encouraging, knowledgeable, and mentorship-oriented tone. Focus on academic and career success."
}
system_msg["content"] += STYLES.get(persona_style, "")

# ── Chat Input ────────────────────────────────────────────────────────────────
selected_model_value = (custom_model or selected_model).strip() or "llama-3.1-8b-instant"
client = get_client(api_key) if api_key_ok else None

if not api_key_ok:
    st.warning("Missing GROQ API key. Add it in the sidebar to begin.")

user_input = st.chat_input("Ask about departments, fees, or faculty...", disabled=not api_key_ok)

if user_input:
    if not user_input.strip():
        st.warning("Input field is empty. Please provide a query.")
        st.stop()

    append_message("user", user_input)

    with st.chat_message("assistant", avatar="🏛️"):
        st.write("PROCESSING REQUEST...")

    # Call Groq API
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
        append_message("assistant", reply)
        st.rerun()

    except Exception as e:
        st.error(f"SYSTEM FAULT: {str(e)}")

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "👦" if msg["role"] == "user" else "🏛️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# ── Welcome message if empty ──────────────────────────────────────────────────
if not st.session_state.messages:
    st.columns([1, 2, 1])[1].subheader("SYSTEM READY")
    st.write("Welcome to the official GP Bhuj AI Assistant. I am here to help you with information about our college, departments, and admissions.")
    st.write("How may I assist you today?")

    col1, col2, col3 = st.columns(3)
    if col1.button("🎓 Fee Structure", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Tell me about the fee structure."})
        st.rerun()
    if col2.button("🏢 Departments", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "List the departments in GP Bhuj."})
        st.rerun()
    if col3.button("👨‍🏫 Faculty", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me the computer engineering faculty."})
        st.rerun()
