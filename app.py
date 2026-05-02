import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import time

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Silvazx IA ", page_icon="🤖", layout="wide")

st.title("🤖 Silvazx IA")
st.markdown("---")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    models = [
        "llama-3.1-8b-instant",
        "llama3-8b-8192",
        "gemma2-9b-it",
        "mixtral-8x7b-32768"
    ]
    selected_model = st.selectbox("Modelo:", models, index=0)

# Inicializa chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# API Key check
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "sua_chave_aqui":
    st.error("❌ **Adicione sua GROQ_API_KEY no arquivo .env!** Pegue em https://console.groq.com/keys")
    st.stop()

# Campo de input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adiciona mensagem do user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Mensagem assistente placeholder para streaming
    with st.chat_message("assistant"):
        stream = st.empty()
        full_response = ""

        # Cliente Groq
        client = Groq(api_key=api_key)

        try:
            # Stream de resposta
            for chunk in client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            ):
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    stream.markdown(full_response + "▌")
            stream.markdown(full_response)
        except Exception as e:
            st.error(f"Erro na API: {str(e)}")

    # Salva resposta no histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("Limpar Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col2:
    if st.button("Novo Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")
