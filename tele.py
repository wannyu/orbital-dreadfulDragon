from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

updater = Updater("5340307669:AAHcHNj6Ir58_AfUdJVDRV-aJdPk0noOL04
", use_context=True)

#message to be sent to user whenever they press start in the beginning
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
            "Hello! I’m FoodSaver, I’m here to reduce food wastage. Here are some commands to use the features I provide.
/add: Everytime you purchase food, simply log in the food, the amount (in servings) and its expiry date. I’ll help to keep track of it and remind you to consume it before it expires!
/consume: Everytime you consume a certain type of food, tell me exactly what you consumed, the amount and I’ll remove it from the list.
/list: This allows you to view a list of all the available food you have at any point in time to prevent buying duplicates.
")
