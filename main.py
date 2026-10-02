import http.server
import logging
import os
import socketserver
import threading
from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Configuração de logs
logging.basicConfig(level=logging.INFO)

# Chaves vindas do ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


# Função para responder no Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sistemas online, Phelipe! Como posso ajudar hoje?"
    )


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem_usuario = update.message.text

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Você é o Jarvis, um assistente virtual altamente inteligente, direto e eficiente.",
            },
            {"role": "user", "content": mensagem_usuario},
        ],
        model="llama-3.3-70b-versatile",
    )

    resposta = chat_completion.choices[0].message.content
    await update.message.reply_text(resposta)


# Servidor web fake para enganar a checagem gratuita do Render
def rodar_servidor_dummy():
    port = int(os.environ.get("PORT", 8080))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Jarvis Online!")

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    # Inicia o servidor web em segundo plano
    threading.Thread(target=rodar_servidor_dummy, daemon=True).start()

    # Inicia o bot do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), responder)
    )

    print("Jarvis rodando na nuvem...")
    app.run_polling()