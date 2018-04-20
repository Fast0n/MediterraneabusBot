from bs4 import BeautifulSoup
from settings import token, client_file, start_msg, orari
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
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
arr1 = {}


period = {
    "Scolastico": "invernale",
    "Non scolastico": "estiva"
}

markup = ReplyKeyboardMarkup(keyboard=orari)


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
                [InlineKeyboardButton(text="Dona", url='https://paypal.me/Fast0n/')],
            ])
        bot.sendMessage(chat_id, "Codice sorgente: \n" +
                        "[MediterraneabusBot](https://github.com/Fast0n/MediterraneabusBot)\n\n" +
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
        for i in range(0, len(orari)):
            for o in range(0, len(orari[i])):
                if command_input != orari[i][o]:
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
        # se la partenza è uguale all'arrivo
        arrivo[chat_id] = command_input
        if partenza[chat_id] == arrivo[chat_id]:
            user_state[chat_id] = 2
            bot.sendMessage(
                chat_id, "Non puoi usare la stessa destinazione, ricomincia")
        else:
            for i in range(0, len(orari)):
                for o in range(0, len(orari[i])):
                    if command_input != orari[i][o]:
                        arr[chat_id] = 3
                    else:
                        arr[chat_id] = 2
                        arrivo[chat_id] = command_input

                        # take info from url
                        URL = "http://www.mediterraneabus.com/linee"

                        tipo_linee = "percorso"
                        stagione = periodo[chat_id]
                        giorno = "feriale"
                        percorso_linea = partenza[chat_id]
                        percorso_linea1 = arrivo[chat_id]

                        data = {
                            "tipo_linee": tipo_linee,
                            "stagione": stagione,
                            "giorno": giorno,
                            "percorso_linea": percorso_linea,
                            "percorso_linea1": percorso_linea1,
                            "btLineePercorso": "",
                            "statetoken": "eyJqYXIiOnsidmVyc2lvbiI6InRvdWdoLWNvb2tpZUAyLjMuMSIsInN0b3JlVHlwZSI6Ik1lbW9yeUNvb2tpZVN0b3JlIiwicmVqZWN0UHVibGljU3VmZml4ZXMiOnRydWUsImNvb2tpZXMiOlt7InZhbHVlIjoiYzRzM2pvMXJxNm11czQwMGE3YjhkMmRxMjQiLCJleHBpcmVzIjoiMjAyMy0wMy0yNVQyMDoyNToxMy40MjZaIiwiaHR0cE9ubHkiOmZhbHNlLCJzZWN1cmUiOmZhbHNlLCJrZXkiOiJQSFBTRVNTSUQiLCJtYXhBZ2UiOjE1Nzc2NjQwMCwiZG9tYWluIjoibWVkaXRlcnJhbmVhYnVzLmNvbSIsInBhdGgiOiIvIiwiaG9zdE9ubHkiOmZhbHNlLCJjcmVhdGlvbiI6IjIwMTgtMDMtMjVUMjA6MjU6MTMuNDI2WiIsImxhc3RBY2Nlc3NlZCI6IjIwMTgtMDMtMjVUMjA6MjU6MTMuNDI2WiJ9LHsidmFsdWUiOiJhY2NlcHRlZCIsImV4cGlyZXMiOiIyMDIzLTAzLTI1VDIwOjI1OjEzLjQ0OFoiLCJodHRwT25seSI6ZmFsc2UsInNlY3VyZSI6ZmFsc2UsImtleSI6ImNiLWVuYWJsZWQiLCJtYXhBZ2UiOjE1Nzc2NjQwMCwiZG9tYWluIjoibWVkaXRlcnJhbmVhYnVzLmNvbSIsInBhdGgiOiIvIiwiaG9zdE9ubHkiOmZhbHNlLCJjcmVhdGlvbiI6IjIwMTgtMDMtMjVUMjA6MjU6MTMuNDQ4WiIsImxhc3RBY2Nlc3NlZCI6IjIwMTgtMDMtMjVUMjA6MjU6MTMuNDQ4WiJ9XX19"
                        }

                        r = requests.post(url=URL, data=data)
                        soup = BeautifulSoup(r.text, "lxml")
                        html = r.text

                        # replace bad string
                        html1 = html.replace('<td><strong>Corse', '<td><titolo>Corse').replace(
                            '<td nowrap><strong>Fermate', '<td nowrap><null>Fermate').replace(
                            '<strong>Stagione', '<null>Stagione').replace(
                            '<strong>Orario', '<null>Orario').replace(
                            '<td><strong>', '<ts><strong>')

                        # move html to json
                        soup1 = BeautifulSoup(html1, "lxml")
                        f1 = open('file.txt', 'w+')
                        f1.write('{\n')
                        for table in soup1.find_all('tr'):
                            keys = [th.get_text(strip=True)
                                    for th in table.find_all('strong')]
                            values = [td.get_text(strip=True)
                                      for td in table.find_all('td')]
                            title = [title.get_text(strip=True)
                                     for title in table.find_all('titolo')]

                            for f in range(len(title)):
                                if title[f] != None:
                                    f1.write(
                                        ']},\n"' + title[f].replace("  ", " ") + '": {\n')

                            for i in range(len(keys)):
                                f1.write('],\n"' + keys[i] + '":[')
                                for o in range(len(values)):
                                    f1.write('"' + values[o] + '",')

                        f1.write("]\n}\n}")
                        f1.close()

                        # refactoring json file
                        with open('file.txt', 'r') as file:
                            filedata = file.read()
                        filedata = filedata.replace('",],', '"],')
                        filedata = filedata.replace('{\n],', '{')
                        filedata = filedata.replace(',]},', ']},')
                        filedata = filedata.replace('",]', '"]')
                        with open(str(chat_id) + '.json', 'w') as file:
                            file.write(filedata)

                        os.remove("file.txt")

                        # delete second row from json file
                        lines = open(str(chat_id) + '.json').readlines()
                        open(str(chat_id) + '.json', 'w').writelines(
                            lines[:1] + lines[2:])

                        with open(str(chat_id) + ".json") as json_file:
                            try:
                                json_data = json.load(json_file)
                                final_message = "🚏 Fermata *" + \
                                    (partenza[chat_id]).upper() + \
                                    "*\nOrari *solo* feriali da _LUN-SAB_"

                                for key in json_data.keys():
                                    for key1 in json_data[key].keys():
                                        if key1 == partenza[chat_id]:
                                            final_message += "\n\n" + \
                                                key.replace("Linea", "*Linea") + \
                                                "*\n🕜 Orari "
                                            for i in range(0, len(json_data[key][partenza[chat_id]])):
                                                if json_data[key][partenza[chat_id]][i] != "":
                                                    final_message += (
                                                        "_" + json_data[key][partenza[chat_id]][i].replace(".", ":") + "_ - ")
                                            final_message = final_message[:-3]
                                            break

                                        elif arrivo[chat_id].split("-")[0] in key1:
                                            break
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
                                    print("Error location")

                                # send messagge
                                bot.sendMessage(chat_id, final_message + "\n\n" + "Direzione *" + (
                                    arrivo[chat_id]).upper() + "*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                            except:
                                bot.sendMessage(chat_id, "*Errore Orario! Non trovato*\nSe desideri cercare un nuovo orario clicca su /orari", parse_mode='Markdown',
                                                reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        return

        if arr[chat_id] == 3:
            bot.sendMessage(
                chat_id, "Seleziona la partenza dalla tastiera", reply_markup=markup)


def register_user(chat_id):
    """
    Register given user to receive news
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
print("Avvio Mediterraneabusbot")

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
