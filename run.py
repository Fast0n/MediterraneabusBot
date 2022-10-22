import json
import logging
import os
import os.path
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pid.decorator import pidfile
from telegram import (Bot, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update)
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from config import start_msg, token

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DEPARTURE, ARRIVAL, MAKELIST = range(3)

bot = Bot(token)


def generateJsonSelect():

    if not Path(os.getcwd() + "/data.json").is_file():
        url = "https://www.mediterraneabus.com/"
        response = requests.request("GET", url)

        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.find_all('script'):
            if 'connections[widget_id]' in item.text:
                script = re.findall(
                    "connections\[widget_id\] = \[(.*)\]", str(item))[0]

                obj = open(os.getcwd() + "/data.json", "w")
                obj.write(json.dumps(json.loads("["+script+"]")))
                obj.close()
                with open(os.getcwd() + "/data.json", "r") as f:
                    readData = json.load(f)
                return(readData)
    else:
        str_d1 = time.ctime(os.path.getctime(os.getcwd() + "/data.json"))
        str_d2 = time.strftime("%a %b %d %H:%M:%S %Y")

        d1 = datetime.strptime(str_d1, "%a %b %d %H:%M:%S %Y")
        d2 = datetime.strptime(str(str_d2), "%a %b %d %H:%M:%S %Y")

        delta = d2 - d1

        if delta.days == 5:
            os.remove(os.getcwd() + "/data.json")
            return generateJsonSelect()
        else:
            with open(os.getcwd() + "/data.json", "r") as f:
                readData = json.load(f)
            return(readData)


def markup_departure():
    json_list = generateJsonSelect()

    arrs = []
    for i in range(len(json_list)):
        arrs.append(json_list[i]['description'])

    n = int(len(arrs)/3)
    reply_keyboard = [[] for _ in range(n)]
    for index, item in enumerate(arrs):
        reply_keyboard[index % n].append(item)

    return reply_keyboard


markup_departure = ReplyKeyboardMarkup(
    markup_departure(), one_time_keyboard=True, resize_keyboard=True, )


def startHandler(update: Update, _):
    """Send starting message"""
    update.message.reply_text(start_msg,  parse_mode=ParseMode.MARKDOWN)


def departure(update: Update, context):
    context.user_data['last_message'] = bot.send_message(
        chat_id=update.message.chat_id, text="Seleziona la partenza",
        parse_mode=ParseMode.MARKDOWN, reply_markup=markup_departure)
    update.message.delete()
    return ARRIVAL


def arrival(update: Update, context):
    last_message = context.user_data['last_message']
    bot.delete_message(
        chat_id=update.effective_chat.id, message_id=last_message.message_id)
    update.message.delete()

    try:
        context.user_data['departure'] = update.message.text
        json_list = generateJsonSelect()

        arrs = []
        for i in range(len(json_list)):
            if json_list[i]['description'] == context.user_data['departure']:
                for j in range(len(json_list[i]['connections'])):
                    arrs.append(json_list[i]['connections'][j]['description'])
        if len(arrs) < 4:
            n = int(3/len(arrs))
        else:
            n = int(len(arrs)/3)
        reply_keyboard = [[] for _ in range(n)]
        for index, item in enumerate(arrs):
            reply_keyboard[index % n].append(item)

        markup_arrival = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.user_data['last_message'] = bot.send_message(
            chat_id=update.message.chat_id,

            text="Seleziona l'arrivo", parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup_arrival
        )

        return MAKELIST
    except:
        return DEPARTURE


def makelist(update, context):
    last_message = context.user_data['last_message']
    bot.delete_message(
        chat_id=update.effective_chat.id, message_id=last_message.message_id)
    update.message.delete()

    context.user_data['arrival'] = update.message.text
    # take info from url
    URL = f"https://api.mediterraneabus.com/search/weekly?departure={context.user_data['departure']}&arrival={context.user_data['arrival']}&excludeExternals=false"

    response = requests.get(URL).json()
    result = json.loads(json.dumps(response))

    if len(result) == 0:
        update.message.reply_text("*Non è stato trovato nessun risultato*",  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardRemove())
    else:
        final_message = f"🚏 Fermata *{(context.user_data['departure']).upper()}*\nOrari *solo* feriali da _LUN-SAB_"

        for i in range(len(result)):

            departureName = result[i]['data']['departure']
            arrivalName = result[i]['data']['arrival']

            for j in range(len(result[i]['routes'][0]['stops'])):
                if result[i]['routes'][0]['stops'][j]['stopId'] == departureName:
                    departureName = result[i]['routes'][0]['stops'][j]['description']

                if result[i]['routes'][0]['stops'][j]['stopId'] == arrivalName:
                    arrivalName = result[i]['routes'][0]['stops'][j]['description']

            departureTime = f"{str(result[i]['data']['departureTime']['hours']).zfill(2)}:{str(result[0]['data']['departureTime']['minutes']).zfill(2)}"
            arrivalTime = f"{str(result[i]['data']['arrivalTime']['hours']).zfill(2)}:{str(result[0]['data']['arrivalTime']['minutes']).zfill(2)}"

            final_message += f"\n\n🚌{departureName}\n📍{arrivalName}*\n🕜 Orario {departureTime} - {arrivalTime}*"

        bot.send_message(
            chat_id=update.message.chat_id,
            text=final_message + "\n\nDirezione *" + (
                context.user_data['arrival']).upper() + "*",  parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def dona(update, context):
    update.message.reply_text("Codice sorgente: \n" +
                              "[MediterraneabusBot](https://github.com/Fast0n/MediterraneabusBot)\n\n" +
                              "Telegram: \n" +
                              "[Fast0n](t.me/Fast0n)\n\n" +
                              "Sviluppato da: \n" +
                              "[Fast0n](https://github.com/Fast0n)\n\n" +
                              "🍺 Se sei soddisfatto offri una birra allo sviluppatore 🍺", parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())


@ pidfile('/tmp/Mediterraneabus.pid')
def main():
    print("--- Starting MediterraneabusBot ---")
    # Setup bot

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & (~Filters.regex(
            '^(/start)$') & (~Filters.regex('^(/dona)$'))), departure)],

        states={

            DEPARTURE: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), departure)],
            ARRIVAL: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), arrival)],
            MAKELIST: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), makelist)],

        },

        fallbacks=[MessageHandler(Filters.text & (
            Filters.regex('^(Stop)$')), startHandler)]

    )

    # Register handlers
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", startHandler))
    dp.add_handler(CommandHandler("orari", departure))
    dp.add_handler(CommandHandler("dona", dona))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
