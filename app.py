import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import base64

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Silvazx IA", page_icon="🤖", layout="wide")

# --- UI/Theme Otimizado ---
st.markdown(
    """
    <style>
      :root{
        --bg0:#07090f;
        --bg1:#0b1220;
        --card:#0f172a;
        --text:#e5e7eb;
        --border:rgba(255,255,255,.08);
        --shadow: 0 18px 50px rgba(0,0,0,.45);
      }
      html, body { 
        background: radial-gradient(1000px 600px at 20% 0%, rgba(255,255,255,.06), transparent 55%),
                   radial-gradient(900px 500px at 90% 10%, rgba(255,255,255,.03), transparent 50%),
                   linear-gradient(180deg, var(--bg0), var(--bg1)); 
      }
      .block-container{ padding-top: 18px; padding-bottom: 120px; }
      .stApp{ color: var(--text); }
      
      /* Chat messages */
      [data-testid="stChatMessage"]{
        border-radius: 16px;
        padding: 10px 12px;
        border: 1px solid rgba(255,255,255,.06);
        background: rgba(2,6,23,.25);
        margin-bottom: 5px;
      }
      
      div[data-baseweb="select"], input, textarea {
        background: rgba(2,6,23,.45) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
      }
      
      .stButton>button{
        background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.04)) !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        color: #fff !important;
        font-weight: 650 !important;
        border-radius: 12px !important;
      }
      .stButton>button:hover{ filter: brightness(1.05); }
      hr{ border-color: rgba(255,255,255,.10) !important; }
      
      /* Ajuste fino para os botões de popover ficarem discretos abaixo da mensagem */
      div[data-testid="stPopover"] button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #9ca3af !important;
        padding: 2px 10px !important;
        font-size: 12px !important;
        height: auto !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Silvazx IA")
st.markdown("---")

# API Key check inicial
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "sua_chave_aqui":
    st.error("Tá sem key no .env porra")
    st.stop()

# Inicializa chat history se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    models = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
    ]
    selected_model = st.selectbox("Modelo:", models, index=0)
    
    st.markdown("---")
    if st.button("Limpar Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("Novo Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CORPO PRINCIPAL: Histórico de Conversas ---
chat_container = st.container()
with chat_container:
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Copiar do histórico usando Popover flutuante (Evita a duplicação na tela principal)
            if message["role"] == "assistant":
                with st.popover("📋 Copiar resposta"):
                    st.code(message["content"], language="text")

st.markdown("---")

# --- BARRA DE INPUT ESTILO "+" (RODAPÉ) ---
with st.container():
    col_anexo1, col_anexo2 = st.columns(2)
    with col_anexo1:
        with st.expander("🎙️ Anexar/Transcrever Áudio", expanded=False):
            audio_file = st.file_uploader(
                "Selecione um áudio", 
                type=["m4a", "wav", "mp3", "ogg", "webm"], 
                key="audio_input_file",
                label_visibility="collapsed"
            )
    with col_anexo2:
        with st.expander("🖼️ Anexar Imagem", expanded=False):
            uploaded_image = st.file_uploader(
                "Selecione uma imagem", 
                type=["png", "jpg", "jpeg", "webp"], 
                key="image_input_file",
                label_visibility="collapsed"
            )

    # Formulário de envio unificado
    with st.form(key="chat_form", clear_on_submit=True):
        col_text, col_btn = st.columns([6, 1])
        with col_text:
            user_text = st.text_input("Digite sua mensagem...", key="text_prompt", label_visibility="collapsed")
        with col_btn:
            submit_button = st.form_submit_button(label="Enviar", use_container_width=True)

# --- PROCESSAMENTO LÓGICO ---
if submit_button and (user_text or audio_file or uploaded_image):
    prompt_final = user_text
    
    if audio_file is not None:
        client = Groq(api_key=api_key)
        try:
            with st.spinner("Transcrevendo áudio gravado..."):
                audio_bytes = audio_file.read()
                transcription = client.audio.transcriptions.create(
                    file=(audio_file.name, audio_bytes),
                    model="whisper-large-v3-turbo",
                    temperature=0,
                    response_format="verbose_json",
                )
                transcript_text = getattr(transcription, "text", "") or ""
                if not prompt_final:
                    prompt_final = transcript_text
                else:
                    prompt_final = f"{prompt_final}\n\n*(Áudio transcrito: {transcript_text})*"
        except Exception as e:
            st.error(f"Erro ao processar áudio: {str(e)}")

    if not prompt_final and uploaded_image is not None:
        prompt_final = "Analise esta imagem."

    if prompt_final:
        st.session_state.messages.append({"role": "user", "content": prompt_final})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_final)

            with st.chat_message("assistant"):
                stream_box = st.empty()
                full_response = ""
                client = Groq(api_key=api_key)

                try:
                    system_prompt = (
                        "Você é uma assistente de IA. Responda SEMPRE em português (Brasil). "
                        "Se o usuário pedir explicitamente outro idioma, responda nesse idioma."
                        "Seu nome é Silvaxz" 
                    )

                    messages_payload = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.messages:
                        messages_payload.append({"role": m["role"], "content": m["content"]})

                    if uploaded_image is not None:
                        image_bytes = uploaded_image.read()
                        b64 = base64.b64encode(image_bytes).decode("utf-8")
                        mime = uploaded_image.type or "image/png"
                        data_url = f"data:{mime};base64,{b64}"

                        messages_payload[-1] = {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_final},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ]
                        }

                    completion = client.chat.completions.create(
                        model=selected_model,
                        messages=messages_payload,
                        temperature=0.7,
                        max_tokens=2048,
                        stream=True,
                    )

                    for chunk in completion:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            stream_box.markdown(full_response + "▌")
                    
                    stream_box.markdown(full_response)
                    
                    # Cria o popover flutuante de cópia após finalizar o streaming atual
                    with st.popover("📋 Copiar resposta"):
                        st.code(full_response, language="text")
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                except Exception as e:
                    st.error(f"Erro na API Groq: {str(e)}")
                    
        st.rerun()
