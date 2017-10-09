import json
from ChatroomConnection import ChatroomConnection
from Config import Config
from messages import MessageBuilder
from messages.Sticker import Sticker
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class Bot:

    def __init__(self, token, chatroom, timeout=0):
        self.bot = telegram.Bot(token=token)
        self.chatroom = chatroom
        self.updater = Updater(token=token)
        self.config = Config("{chatroom}.conf.json".format(chatroom=str(chatroom)))
        self.timeout = timeout
    
    def getNewMessages(self):
        self.updater.start_polling()

def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def getUpdateID(update):
    return int(update["update_id"])

def morningStats(bot, update):
    bot.send_message(chat_id=self.chatroom, text=text)

def morningSticker(bot, update):
    done
