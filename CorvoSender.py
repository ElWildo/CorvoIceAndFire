import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()

TOKEN = "731613577:AAHizFkxozKhXpxTcA9I2x08fFroMStzCUs"
URL = "https://api.telegram.org/bot{}".format(TOKEN)
ADMINCHAT ="-318490472"

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "/getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

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

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["results"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "/sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)

def build_keyboard(items):
    keyboard = [[items]]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            username = update["message"]["chat"]["username"]
#            items = db.get_user_chat(chat)
#            if lasttextandsend == "/done":
#                keyboard = build_keyboard("Nuovo Corvo",)
#                send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
            if text == "/done":
                keyboard = build_keyboard("Nuovo Corvo",)
                send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
            elif text == "/start":
                send_message("Bnvenuto viaggiatore. Sono il corvo della Role di Ice and Fire", chat)
                db.add_item_chat(chat,username)
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
                if chatReceiver == [] or sender == []:
                    send_message("Errore. Riprova di nuovo",chat)
                    keyboard = build_keyboard("Nuovo Corvo",)
                    send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
                send_message(message, chatReceiver[0])
                print(message)
                print(chatReceiver)
                send_message("Corvo inviato", chat)
                send_message("Done", chat)
                messageAdm = ["Da:" , sender[0] , "A:" , receiver , message]
                print("\n".join(messageAdm))
                send_message("\n".join(messageAdm), ADMINCHAT)
            elif text == "Nuovo Corvo":
                msg= "Per mandare un nuovo corvo devi inserire il tag del destinatario ed andare a capo per scrivere poi il messaggio che vuoi recapitargli"
                send_message(msg, chat)
                msg= "Esempio:"
                send_message(msg, chat)
                msg= "@TizioCaio\nChe bella questa role\nCorvo di Ice and Fire"
                send_message(msg, chat)
                msg= "Ricordati che se vuoi che la persona a cui stai inviando il corvo sappia chi sei devi firmarti alla fine"
                send_message(msg, chat)
#                db.delete_item_chat(text, chat)
#                items = db.get_user_chat(chat)
#                keyboard = build_keyboard(items)
#                send_message("Select an item to delete", chat, keyboard)
            else:
#                db.add_item(text, chat)
#                items = db.get_user_chat(chat)
#                message = "\n".join(items)
                send_message("Errore. Riprova di nuovo",chat)
                keyboard = build_keyboard("Nuovo Corvo",)
                send_message("Premi \"Nuovo Corvo\" per mandare un nuovo messaggio", chat, keyboard)
        except KeyError:
            pass

def main():
    last_update_id = None
    db.setup()
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
#            lasttextandsend = get_last_update_text_from_bot(updates)
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()