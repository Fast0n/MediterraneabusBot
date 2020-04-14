import logging
import json
import requests

from telegram import Location
import telegram.error as tg_error
from telegram import (ParseMode, MessageEntity, ChatAction,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, ConversationHandler)

from settings import token, start_msg, periodList, url_api


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

DEPARTURE, ARRIVAL, MAKELIST = range(3)


def markup_test():
    json_list = json.loads(requests.get(url_api + "?lista").text)
    arr = json_list["list"]["routes"]

    arrs = []
    while len(arr) > 2:
        pice = arr[:2]
        arrs.append(pice)
        arr = arr[2:]
    arrs.append(arr)
    return arrs


reply_keyboard = markup_test()


def start(update, context):
    """Send starting message"""
    update.message.reply_text(start_msg,  parse_mode=ParseMode.MARKDOWN)


def period(update, context):
    reply_keyboard = [['Scolastico', "Non Scolastico"]]
    update.message.reply_text("Seleziona il periodo",  parse_mode=ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return DEPARTURE


def departure(update, context):
    context.user_data['period'] = update.message.text

    update.message.reply_text("Seleziona la partenza",  parse_mode=ParseMode.MARKDOWN,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return ARRIVAL


def arrival(update, context):
    # check field
    hours_raw = json.loads(requests.get(url_api + "?lista").text)
    hours = hours_raw["list"]["routes"]

    context.user_data['departure'] = update.message.text
    for i in range(0, len(hours)):
        if context.user_data['departure'] == hours[i]:
            update.message.reply_text("Seleziona l'arrivo",  parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

            return MAKELIST

        elif i == len(hours)-1 and context.user_data['departure'] != hours[len(hours)-1]:
            update.message.reply_text("Seleziona la partenza dalla tastiera",  parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))


def makelist(update, context):
    # check field
    hours_raw = json.loads(requests.get(url_api + "?lista").text)
    hours = hours_raw["list"]["routes"]

    context.user_data['arrival'] = update.message.text
    for i in range(0, len(hours)):
        if i == len(hours)-1 and context.user_data['arrival'] != hours[len(hours)-1]:
            update.message.reply_text("Seleziona la partenza dalla tastiera",  parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

        elif context.user_data['arrival'] == hours[i]:
            periodo = periodList[context.user_data['period']]

            # take info from url
            URL = url_api + \
                "?periodo=" + periodo + "&percorso_linea=" + \
                context.user_data['departure'] + \
                "&percorso_linea1=" + \
                context.user_data['arrival'] + "&sort_by=time"

            r = requests.get(URL)
            try:
                json1 = json.loads(r.text)
                print(json1)
                if json1 == []:
                    update.message.reply_text("*Non è stato trovato nessun risultato*",  parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=ReplyKeyboardRemove())
                else:
                    final_message = "🚏 Fermata *" + \
                        (context.user_data['departure']).upper() + \
                        "*\nOrari *solo* feriali da _LUN-SAB_"
                    for z in range(len(json1)):
                        final_message += "\n\n" + (json1[z]['a']).replace(
                            "Linea", "*Linea") + "*\n🕜 Orario " + json1[z]['b'] + " - " + json1[z]['c']

                    # send location
                    URL = "https://raw.githubusercontent.com/Fast0n/MediterraneabusBot/master/geocode.csv"
                    r = requests.get(URL)
                    for row in range(0, len((r.text.split("\n")))):
                        a = r.text.split("\n")
                        b = a[row].split(",")
                        if context.user_data['departure'] in b[2]:
                            latitude = b[0]
                            longitude = b[1]

                    update.message.reply_text(final_message + "\n\nDirezione *" + (
                        context.user_data['arrival']).upper() + "*",  parse_mode=ParseMode.MARKDOWN,
                        reply_markup=ReplyKeyboardRemove())

                    context.bot.send_location(
                        chat_id=update.message.chat_id, latitude=latitude, longitude=longitude)

            except Exception as e:
                print(str(e))
                update.message.reply_text("*Errore Orario! Non trovato*\nSe desideri cercare un nuovo orario clicca su /orari",  parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=ReplyKeyboardRemove())

            return ConversationHandler.END


def dona(update, context):
    update.message.reply_text("Codice sorgente: \n" +
                              "[MediterraneabusBot](https://github.com/Fast0n/MediterraneabusBot)\n\n" +
                              "Instagram: \n" +
                              "[Fast0n](instagram.com/Fast0n)\n\n" +
                              "Sviluppato da: \n" +
                              "[Fast0n](https://github.com/Fast0n)\n\n" +
                              "🍺 Se sei soddisfatto offri una birra allo sviluppatore 🍺", parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())


def error(update, context):
    """Log errors caused by updates"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot"""
    print("Avvio MediterraneabusBot")

    # Create the Updater
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & (~Filters.regex(
            '^(/start)$') & (~Filters.regex('^(/dona)$'))), period)],

        states={

            DEPARTURE: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), departure)],
            ARRIVAL: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), arrival)],
            MAKELIST: [MessageHandler(Filters.text & (~Filters.regex('^(/start)$') & (~Filters.regex('^(/dona)$'))), makelist)],

        },

        fallbacks=[MessageHandler(Filters.text & (
            Filters.regex('^(Stop)$')), start)]

    )

    # Register handlers
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("orari", period))
    dp.add_handler(CommandHandler("dona", dona))

    # Register error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
