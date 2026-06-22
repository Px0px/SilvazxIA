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
        # transcrição (whisper-large-v3-turbo) via upload, fora do modelo do chat
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "openai/gpt-oss-120b",
    ]



    selected_model = st.selectbox("Modelo:", models, index=0)

    st.caption("Dica: transcrição de áudio usa whisper-large-v3-turbo.")


# Inicializa chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Utilitário: copiar texto para área de transferência (browser)
def render_copy_button(text: str, button_label: str = "Copiar resposta"):
    # Observação: precisa de componente HTML para copiar no navegador.
    # Também usa um id único para evitar conflitos entre múltiplas mensagens.
    import uuid
    btn_id = f"copy_{uuid.uuid4().hex}"
    safe_text = text.replace("\\", "\\\\").replace("\"", "\\\"")
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-top:6px; margin-bottom:10px;">
          <button id="{btn_id}" type="button" style="
              border:1px solid #444; background:#111; color:#fff; padding:6px 10px; border-radius:8px;
              cursor:pointer; font-size:0.9rem;">
            {button_label}
          </button>
          <span id="{btn_id}_status" style="font-size:0.85rem; opacity:0.8;"></span>
        </div>
        <script>
          const btn = document.getElementById('{btn_id}');
          const statusEl = document.getElementById('{btn_id}_status');
          if (btn) {{
            btn.addEventListener('click', async () => {{
              try {{
                await navigator.clipboard.writeText("{safe_text}");
                if (statusEl) statusEl.textContent = 'Copiado!';
              }} catch (e) {{
                if (statusEl) statusEl.textContent = 'Falha ao copiar';
              }}
            }});
          }}
        </script>
        """,
        unsafe_allow_html=True,
    )


# Exibe histórico de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_copy_button(message["content"], button_label="Copiar resposta")


# API Key check
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "sua_chave_aqui":
    st.error("❌ **Adicione sua GROQ_API_KEY no arquivo .env!** Pegue em https://console.groq.com/keys")
    st.stop()

# --------- Transcrição de áudio (uploader) ---------
st.subheader("🎙️ Transcrever áudio")
audio_file = st.file_uploader(
    "Envie um arquivo de áudio (ex: m4a/wav)",
    type=["m4a", "wav", "mp3", "ogg", "webm"],
)

transcript_text = ""

if audio_file is not None:
    client = Groq(api_key=api_key)
    try:
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )
        transcript_text = getattr(transcription, "text", "") or ""
        st.text_area("Texto transcrito", value=transcript_text, height=140)

        if st.button("Usar transcrição como prompt", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": transcript_text})
            with st.chat_message("user"):
                st.markdown(transcript_text)

    except Exception as e:
        st.error(f"Erro ao transcrever: {str(e)}")

# --------- Campo de input do usuário (texto + foto) ---------
with st.container():
    uploaded_image = st.file_uploader(
        "Envie uma imagem (opcional)",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_uploader",
    )

    col_text, col_btn = st.columns([6, 1])
    with col_text:
        prompt = st.chat_input("Digite sua mensagem...")
    with col_btn:
        send = st.button("Enviar", use_container_width=True)

if (prompt is not None and prompt != "") or send:
    # Se usuário clicou enviar sem texto, ainda assim enviar prompt vazio
    if prompt is None:
        prompt = ""



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
            # Força idioma: sempre responder em PT-BR, salvo se o usuário pedir outro idioma.
            system_prompt = (
                "Você é uma assistente de IA. "
                "Responda SEMPRE em português (Brasil). "
                "Se o usuário pedir explicitamente outro idioma, responda nesse idioma. "
                "Caso contrário, mantenha a resposta em português (Brasil)."
            )

            messages_payload = [{"role": "system", "content": system_prompt}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ]


            # Se o usuário enviou imagem, anexamos como "image_url" (visão) quando o modelo suportar.
            # (Alguns modelos podem exigir formato específico; este é o padrão do Groq/OpenAI para multimodal).
            if uploaded_image is not None and prompt is not None and prompt != "":
                image_bytes = uploaded_image.read()
                import base64
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                mime = uploaded_image.type or "image/png"
                data_url = f"data:{mime};base64,{b64}"

                messages_payload = [
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ]}
                ]

            for chunk in client.chat.completions.create(
                model=selected_model,
                messages=messages_payload,
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
