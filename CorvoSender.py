import json
import requests
import time
import urllib
#import telepot
from dbhelper import DBHelper
from flask import Flask, request

# Inizialize database

db = DBHelper()

# Configuring the script for the bot

TOKEN = "youauthtoken"
URL = "https://api.telegram.org/bot{}".format(TOKEN)
ADMINCHAT ="-securecode"

# Getting bot URL

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# Getting JSON

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

# Getting updates from the bot

def get_updates(offset=None):
    url = URL + "/getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

# Getting the id for the last Update

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

# Getting the last message sent by the bot

def get_last_update_text_from_bot(updates):
    update_ids = []
    for update in updates["result"]:
        print(update["message"]["from"]["username"])
        if update["message"]["from"]["username"] == "corvo_iceandfire_bot":
            update_ids.append(int(update["update_id"]))
    if len(update_ids) == 0:
        return None
    else:
        last_update_id = max(update_ids)
    for update in updates["result"]:
        if last_update_id == int(update["update_id"]):
            return (updates["result"][last_update_id]["message"]["text"])
        else:
            return ("error")

# Getting the last Chat ID and text

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["results"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

# Sending Message

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "/sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

# Rpinting all the messages

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)

# Bulding keyboard

def build_keyboard(items):
    keyboard = [[items]]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

# Core Funtion: handleing messages sent to the bot

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            username = update["message"]["chat"]["username"]
            if text == "/done":
                keyboard = build_keyboard("Nuovo Corvo",)
                send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
            elif text == "/start":
                send_message("Benvenuto viaggiatore. Sono il corvo della Role di Ice and Fire", chat)
                db.add_item_chat(chat,username)
                send_message("L'utente "+username+" si è registrato al bot Corvo", ADMINCHAT)
                keyboard = build_keyboard("Nuovo Corvo",)
                send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
            elif text.startswith("/"):
                continue
            elif text.startswith("@"):
                text = text.partition("@")[2]
                text = text.partition("\n")
                receiver = text[0]
                message = text[2]
                chatReceiver = db.get_user_chat(receiver)
                sender = db.get_user_name(chat)
                if not sender:
                    keyboard = build_keyboard("/start",)
                    send_message("**Errore**. Potresti non essere registrato al Bot.\npremi sul trasto /start per registrarti",chat, keyboard)
                if not chatReceiver:
                    keyboard = build_keyboard("Nuovo Corvo",)
                    send_message("**Errore**. Riprova di nuovo.\nPotresti aver sbagliato il destinatario",chat, keyboard)
                else:
                    send_message(message, chatReceiver[0])
                    send_message("Corvo inviato", chat)
                    messageAdm = ["**Da:** @"+sender[0] , "**A:** @"+receiver , "__" + message + "__"]
                    send_message("\n".join(messageAdm), ADMINCHAT)
            elif text == "Nuovo Corvo":
                msg= "Per mandare un nuovo corvo devi inserire il tag del destinatario ed andare a capo per scrivere poi il messaggio che vuoi recapitargli"
                send_message(msg, chat)
                msg= "**Esempio:**\n@TizioCaio\nChe bella questa role\nCorvo di Ice and Fire"
                send_message(msg, chat)
                msg= "Ricordati che se vuoi che la persona a cui stai inviando il corvo sappia chi sei devi **firmarti** alla fine"
                send_message(msg, chat)
            else:
                keyboard = build_keyboard("Nuovo Corvo",)
                send_message("**Errore**. Riprova di nuovo",chat, keyboard)
        except KeyError:
            pass

# Running on webApp

def main():
    last_update_id = None
    db.setup()
    while True:
        updates = get_updates(last_update_id)
        print(updates)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()