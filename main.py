

"""
Bot Telegram Business — API Bot officielle uniquement (aucune lib non officielle).

Fonctionnement :
- Le bot est connecté à un compte Telegram Business (Connected Business Bots).
- Telegram envoie alors les messages du compte Business dans le champ
  `business_message` de chaque Update (et non `message`).
- On utilise `update.effective_message`, qui pointe automatiquement vers ce
  `business_message` (PTB le gère nativement depuis la Bot API 7.2 / PTB 21.1).
- Pour répondre "au nom" du compte Business, chaque appel d'envoi doit inclure
  le paramètre officiel `business_connection_id` (documenté ici :
  https://core.telegram.org/bots/api#sendmessage /  #sendvideonote).
"""

import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

load_dotenv()



BOT_TOKEN = "8643005430:AAGlH70LtttFkE-z-ZBcuPjJ5uNDMXMqY_U"
MESSAGE_TEXT = "Tiens moi au courant 🔥"
VIDEO_NOTE_FILE_ID = "start.mp4"   # file_id Telegram OU chemin local vers un .mp4
USERS_FILE = "users.json"


def load_users() -> set:
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(json.load(f))


def save_users(user_ids: set) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(list(user_ids), f)


# Chargée une fois au démarrage, mise à jour à chaque nouvel envoi
processed_users = load_users()


async def handle_go(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message pointe vers business_message pour les updates Business
    message = update.effective_message
    if message is None or not message.text:
        return

    if message.text.strip().lower() != "go":
        return

    business_connection_id = message.business_connection_id
    chat_id = message.chat_id
    user_id = message.from_user.id

    # Vérification anti-doublon : a-t-on déjà traité cet utilisateur ?
    if user_id in processed_users:
        return

    try:
        # 1. Message texte, envoyé au nom du compte Business
        await context.bot.send_message(
            chat_id=chat_id,
            text=MESSAGE_TEXT,
            business_connection_id=business_connection_id,
        )

        # 2. Note vidéo, envoyée au nom du compte Business
        await context.bot.send_video_note(
            chat_id=chat_id,
            video_note=VIDEO_NOTE_FILE_ID,
            business_connection_id=business_connection_id,
        )
    except Exception as e:
        print(f"Erreur d'envoi pour l'utilisateur {user_id} : {e}")
        return  # on ne l'enregistre pas : il pourra être retraité au prochain "GO"

    # Enregistrement UNIQUEMENT après un envoi réussi, pour éviter tout doublon
    processed_users.add(user_id)
    save_users(processed_users)


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # filters.TEXT couvre aussi bien les messages classiques que les
    # business_message depuis PTB 21.1 (Bot API 7.2)
    app.add_handler(MessageHandler(filters.TEXT, handle_go))

    print("Bot démarré, en attente du message 'GO'...")
    # allowed_updates=Update.ALL_TYPES garantit la réception des business_message
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()