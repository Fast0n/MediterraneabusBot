from bs4 import BeautifulSoup
from settings import token, client_file, start_msg, hours, period
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from random import randint
import json
import os
import requests
import sys
import telepot

# State for user
user_state = {}

periodo = {}
partenza = {}
arrivo = {}
arr = {}

markup = ReplyKeyboardMarkup(keyboard=hours)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command_input = msg['text']

    # Check user state
    try:
        user_state[chat_id] = user_state[chat_id]
    except:
        user_state[chat_id] = 0

    # start command
    if command_input == "/start":
        if register_user(chat_id):
            bot.sendMessage(chat_id, start_msg, parse_mode='Markdown')
            command_input = "/orari"

    # donate command
    if command_input == '/dona':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Dona", url='https://paypal.me/Fast0n/')],
        ])
        bot.sendMessage(chat_id, "Codice sorgente: \n" +
                        "[MediterraneabusBot](https://github.com/Fast0n/MediterraneabusBot)\n\n" +
                        "App Android: \n" +
                        "[Mediterraneabus App](https://play.google.com/store/apps/details?id=com.fast0n.mediterraneabus)\n\n" +
                        "Instagram: \n" +
                        "[Mediterraneabus](instagram.com/mediterraneabus)\n\n" +
                        "Sviluppato da: \n" +
                        "[Fast0n](https://github.com/Fast0n)\n\n" +
                        "🍺 Se sei soddisfatto offri una birra allo sviluppatore 🍺", parse_mode='Markdown', reply_markup=keyboard)
        user_state[chat_id] = 0

    # orari command
    if command_input == '/orari':
        msg = "Seleziona il periodo"
        markup1 = ReplyKeyboardMarkup(keyboard=[["Scolastico", "Non scolastico"]
                                                ])
        bot.sendMessage(chat_id, msg, reply_markup=markup1)
        user_state[chat_id] = 1

    elif user_state[chat_id] == 1:
        msg = "Seleziona la partenza"
        bot.sendMessage(chat_id, msg, reply_markup=markup)
        user_state[chat_id] = 2
        periodo[chat_id] = period[command_input]

    elif user_state[chat_id] == 2:
        # check field
        for i in range(0, len(hours)):
            for o in range(0, len(hours[i])):
                if command_input != hours[i][o]:
                    arr[chat_id] = 1
                else:
                    arr[chat_id] = 0
                    partenza[chat_id] = command_input
                    msg = "Seleziona l'arrivo"
                    bot.sendMessage(chat_id, msg, reply_markup=markup)
                    user_state[chat_id] = 3
                    return

        # if field is false
        if arr[chat_id] == 1:
            bot.sendMessage(
                chat_id, "Seleziona la partenza dalla tastiera", reply_markup=markup)

    elif user_state[chat_id] == 3:
        # if the departure is equal on arrival
        arrivo[chat_id] = command_input
        if partenza[chat_id] == arrivo[chat_id]:
            user_state[chat_id] = 2
            bot.sendMessage(
                chat_id, "Non puoi usare la stessa destinazione, ricomincia...")
        else:
            for i in range(0, len(hours)):
                for o in range(0, len(hours[i])):
                    if command_input != hours[i][o]:
                        arr[chat_id] = 3
                    else:
                        arr[chat_id] = 2
                        arrivo[chat_id] = command_input

                        # take info from url
                        URL = "https://mediterraneabus-api.herokuapp.com/?periodo=" + \
                            periodo[chat_id] + "&percorso_linea=" + \
                            partenza[chat_id] + \
                            "&percorso_linea1=" + arrivo[chat_id]

                        r = requests.get(URL)
                        try:
                            json1 = json.loads(r.text)

                            final_message = "🚏 Fermata *" + \
                                (partenza[chat_id]).upper() + \
                                "*\nOrari *solo* feriali da _LUN-SAB_"

                            for z in range(len(json1['linee'])):
                                final_message += "\n\n" + (json1['linee'][z]['corsa']).replace(
                                    "Linea", "*Linea") + "*\n🕜 Orari "
                                for x in range(len(json1['linee'][z]['orari'])):
                                    final_message += "_" + \
                                        json1['linee'][z]['orari'][x]['partenza'] + " _ - "

                                    if x + 1 == len(json1['linee'][z]['orari']):
                                        final_message = final_message[:-3]

                            try:
                                # send location
                                response = requests.get(
                                    'https://maps.googleapis.com/maps/api/geocode/json?address=' + partenza[chat_id].replace("-", " ") + ',+IT')
                                resp_json_payload = response.json()
                                a = str(
                                    resp_json_payload['results'][0]['geometry']['location']).split(",")
                                latitude = a[0].replace("{'lat': ", "")
                                longitude = a[1].replace("'lng': ", "").replace(
                                    " ", "").replace("}", "")
                                bot.sendLocation(chat_id, latitude, longitude, reply_markup=ReplyKeyboardRemove(
                                    remove_keyboard=True))
                            except:
                                pass

                            bot.sendMessage(
                                chat_id, final_message + "\n\nDirezione *" + (
                                    arrivo[chat_id]).upper() + "*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                                                     
                            random = randint(1, 3);
                            if random == 1:
                             bot.sendMessage(
                                chat_id, "Sei un utente Android?\n\nScarica l'app [Mediterraneabus](https://play.google.com/store/apps/details?id=com.fast0n.mediterraneabus)", parse_mode='Markdown')
                            elif random == 2:
                               keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(
                                    text="Dona", url='https://paypal.me/Fast0n/')],
                            ])
                            bot.sendMessage(chat_id, "Codice sorgente: \n" +
                                            "[MediterraneabusBot](https://github.com/Fast0n/MediterraneabusBot)\n\n" +
                                            "Instagram: \n" +
                                            "[Mediterraneabus](instagram.com/mediterraneabus)\n\n" +
                                            "Sviluppato da: \n" +
                                            "[Fast0n](https://github.com/Fast0n)\n\n" +
                                            "🍺 Se sei soddisfatto offri una birra allo sviluppatore 🍺", parse_mode='Markdown', reply_markup=keyboard)
                            user_state[chat_id] = 0
                            
                            return

                        except:
                            bot.sendMessage(chat_id, "*Errore Orario! Non trovato*\nSe desideri cercare un nuovo orario clicca su /orari", parse_mode='Markdown',
                                            reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        return


def register_user(chat_id):
    """
    Register given user
    """
    insert = 1

    try:
        f = open(client_file, "r+")

        for user in f.readlines():
            if user.replace('\n', '') == str(chat_id):
                insert = 0

    except IOError:
        f = open(client_file, "w")

    if insert:
        f.write(str(chat_id) + '\n')

    f.close()

    return insert


# Main
print("Avvio MediterraneabusBot")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/mediterraneabusbot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working
try:

    bot = telepot.Bot(token)
    bot.message_loop(on_chat_message)
    while(1):
        sleep(10)
finally:
    os.unlink(pidfile)
