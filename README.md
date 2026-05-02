# 🤖 IA Local com Groq API

## 📋 O que é isso?
App de chat IA rodando **localmente** no seu navegador, usando a **API da Groq** (super rápida com modelos como Llama 3.1, Gemma, Mixtral). Sem servidor externo além da API Groq.

## 🚀 Como usar (em 2 minutos)

1. **Crie ambiente virtual (venv):**
   ```
   cd "c:/Users/usuario/Desktop/Silvazx"
   python -m venv venv
   ```

2. **Ative o venv:**
   ```
   venv\Scripts\activate
   ```
   (Você verá `(venv)` no prompt.)

3. **Instale dependências NO VENV (OBRIGATÓRIO para fix httpx):**  \n   ```\n   pip install -r requirements.txt\n   ```\n   **IMPORTANTE:** Rode SEMPRE no venv ativado (veja (venv) no prompt) para evitar erro 'proxies'!

4. **Pegue sua chave GRATUITA da Groq:**
   - Vá em [console.groq.com/keys](https://console.groq.com/keys)
   - Crie conta (grátis) e gere uma API key.

5. **Configure a chave:**
   - Abra `.env` no editor.
   - Substitua `sua_chave_aqui` por sua key real:
     ```
     GROQ_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```
   - Salve!

6. **Rode o app:**
   ```
   streamlit run app.py
   ```

7. **Abra no navegador:** http://localhost:8501
   - Chat pronto! Escolha modelo na sidebar.
   - Limpe ou novo chat com botões.

## 🔧 Funcionalidades
- **Streaming:** Respostas em tempo real.
- **Histórico:** Mantém conversa.
- **Modelos:** Llama3, Gemma, Mixtral (selecione sidebar).
- **Seguro:** Chave local no .env.

## 🛠️ Problemas comuns
- **Erro API key:** Verifique .env e se key é válida (teste em playground.groq.com).
- **Streamlit não encontrado:** Reinstale no venv.
- **Porta ocupada:** Mate processos ou use `streamlit run app.py --server.port 8502`.
- **Windows:** Use aspas em caminhos com espaços.

## 📱 Screenshot
![App](https://i.imgur.com/placeholder-chat.png) *(abra e teste!)*

**Feito com ❤️ por BLACKBOXAI. Divirta-se chateando com IA local!**
