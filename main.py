"""
Bot Telegram : quand un utilisateur envoie "go", il reçoit une fois
(et une seule fois) une vidéo ronde + un message texte.

Les IDs des utilisateurs déjà servis sont stockés dans un fichier JSON
pour éviter les doublons, même si le bot redémarre.
"""

import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# --- Configuration ---
BOT_TOKEN = "8643005430:AAGlH70LtttFkE-z-ZBcuPjJ5uNDMXMqY_U" # défini avant de lancer le script
VIDEO_NOTE_PATH = "start.mp4"   # ta vidéo ronde (format carré, .mp4)
TEXT_MESSAGE = "Tiens moi au courant 🔥"
SENT_USERS_FILE = "sent_users.json"


def load_sent_users() -> set:
    if not os.path.exists(SENT_USERS_FILE):
        return set()
    with open(SENT_USERS_FILE, "r") as f:
        return set(json.load(f))


def save_sent_users(user_ids: set) -> None:
    with open(SENT_USERS_FILE, "w") as f:
        json.dump(list(user_ids), f)


# Chargé une fois en mémoire au démarrage, puis tenu à jour à chaque envoi
sent_users = load_sent_users()


async def handle_go(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Vérification : déjà servi ?
    if user_id in sent_users:
        return  # on ne renvoie rien

    # Envoi de la vidéo ronde
    with open(VIDEO_NOTE_PATH, "rb") as video:
        await context.bot.send_video_note(chat_id=user_id, video_note=video)

    # Envoi du message texte
    await context.bot.send_message(chat_id=user_id, text=TEXT_MESSAGE)

    # Enregistrement pour ne plus jamais renvoyer à cet utilisateur
    sent_users.add(user_id)
    save_sent_users(sent_users)


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Déclenche uniquement sur le message exact "go" (insensible à la casse)
    app.add_handler(
        MessageHandler(filters.Regex(r"(?i)^go$"), handle_go)
    )

    print("Bot démarré, en attente du message 'go'...")
    app.run_polling()


if __name__ == "__main__":
    main()