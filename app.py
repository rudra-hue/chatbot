# ── Render chat history FIRST ───────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "👦" if msg["role"] == "user" else "🏛️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])


# ── Welcome message (mobile friendly) ───────────────────────────────────────
if not st.session_state.messages:
    st.markdown("## 🟢 SYSTEM READY")
    st.write("Welcome to the official GP Bhuj AI Assistant.")
    st.write("Ask about departments, fees, faculty, or admissions.")

    # ✅ Mobile responsive buttons (stack instead of columns)
    if st.button("🎓 Fee Structure", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Tell me about the fee structure."})
        st.rerun()

    if st.button("🏢 Departments", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "List the departments in GP Bhuj."})
        st.rerun()

    if st.button("👨‍🏫 Faculty", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me the computer engineering faculty."})
        st.rerun()


# ── Chat Input ALWAYS at bottom ─────────────────────────────────────────────
user_input = st.chat_input("Ask about departments, fees, or faculty...", disabled=not api_key_ok)

if user_input:
    if not user_input.strip():
        st.warning("Input field is empty. Please provide a query.")
        st.stop()

    append_message("user", user_input)

    with st.chat_message("assistant", avatar="🏛️"):
        st.write("PROCESSING REQUEST...")

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