


import os
import json

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================
# CONFIGURATION
# =========================


BOT_TOKEN = "8643005430:AAGlH70LtttFkE-z-ZBcuPjJ5uNDMXMqY_U"
MESSAGE_TEXT = "Tiens moi au courant 🔥"
VIDEO_NOTE_FILE_ID = "start.mp4"   # file_id Telegram OU chemin local vers un .mp4
USERS_FILE = "users.json"


# =========================
# GESTION DES UTILISATEURS
# =========================

def load_users() -> set:
    if not os.path.exists(USERS_FILE):
        return set()

    with open(USERS_FILE, "r") as f:
        return set(json.load(f))


def save_users(user_ids: set) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(list(user_ids), f)


processed_users = load_users()


# =========================
# TRAITEMENT DU MESSAGE GO
# =========================

async def handle_go(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.business_message

    if not message or not message.text:
        return

    if message.text.strip().lower() != "go":
        return

    user_id = message.from_user.id

    if user_id in processed_users:
        return

    try:
        # 1. Réponse texte
        await message.reply_text(MESSAGE_TEXT)

        # 2. Réponse note vidéo
        await message.reply_video_note(
            video_note=VIDEO_NOTE_FILE_ID
        )

        # Enregistrer après succès
        processed_users.add(user_id)
        save_users(processed_users)

        print(f"[OK] Messages envoyés à {user_id}")

    except Exception as e:
        print(f"[ERREUR] {e}")
# =========================
# DÉMARRAGE DU BOT
# =========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT,
            handle_go
        )
    )

    print("Bot démarré, en attente de GO...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()