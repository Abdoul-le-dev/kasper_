


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

async def handle_go(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    message = update.effective_message

    if message is None or not message.text:
        return

    # Vérifie le message GO
    if message.text.strip().lower() != "go":
        return

    # Récupération des informations
    business_connection_id = message.business_connection_id
    chat_id = message.chat_id
    user_id = message.from_user.id

    print(
        f"[DEBUG] chat_id={chat_id} "
        f"user_id={user_id} "
        f"business_connection_id={business_connection_id}"
    )

    # Évite les doublons
    if user_id in processed_users:
        print(f"[INFO] Utilisateur déjà traité : {user_id}")
        return

    # Vérification Business
    if not business_connection_id:
        print("[ERREUR] Aucune connexion Business trouvée")
        return

    try:

        # Vérifier la connexion Business
        business_connection = await context.bot.get_business_connection(
            business_connection_id
        )

        if not business_connection.is_enabled:
            print("[ERREUR] Connexion Business désactivée")
            return

        # =========================
        # ENVOI DU MESSAGE TEXTE
        # =========================

        await context.bot.send_message(
            chat_id=chat_id,
            text=MESSAGE_TEXT,
            business_connection_id=business_connection_id
        )

        # =========================
        # ENVOI DE LA NOTE VIDÉO
        # =========================

        await context.bot.send_video_note(
            chat_id=chat_id,
            video_note=VIDEO_NOTE_FILE_ID,
            business_connection_id=business_connection_id
        )

        # =========================
        # ENREGISTREMENT UTILISATEUR
        # =========================

        processed_users.add(user_id)
        save_users(processed_users)

        print(f"[OK] Messages envoyés à {user_id}")

    except Exception as e:

        print(
            f"[ERREUR] Envoi impossible pour {user_id} : {e}"
        )

        return


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