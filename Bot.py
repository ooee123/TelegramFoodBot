#!/usr/bin/python3
import sys

from telegram.ext import BaseFilter
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters 

from Morning import Morning
from Morning import MORNING_STICKER
from Config import Config

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    if len(sys.argv) < 2:
        print("Usage {0} <bot_token> <chatroom_id>".format(sys.argv[0]))
        sys.exit(-1)
    token = sys.argv[1]
    chatroom = int(sys.argv[2])
    config = Config("{chatroom}.Morning.conf.json".format(chatroom=chatroom))
    morningBot = Morning(token, chatroom, config)

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    morning_sticker_handler = MessageHandler(MorningStickerFilter(), morningBot.morningSticker)
    dispatcher.add_handler(morning_sticker_handler)
    morningStats_handler = CommandHandler('morningStats', morningBot.morningStats)
    dispatcher.add_handler(morningStats_handler)
    morningGraph_handler = CommandHandler('morningGraph', morningBot.morningGraph)
    dispatcher.add_handler(morningGraph_handler)

    dispatcher.add_error_handler(print_error_callback)

    updater.start_polling(timeout=30)

def print_error_callback(bot, update, error):
    logger = logging.getLogger(__name__)
    logger.error("Exception: {error}, with update {update}".format(error=error, update=update))

class MorningStickerFilter(BaseFilter):
    def filter(self, message):
        return message.sticker and MORNING_STICKER == message.sticker.file_id

main()
