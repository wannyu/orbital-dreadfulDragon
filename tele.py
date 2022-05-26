from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

updater = Updater("5340307669:AAHcHNj6Ir58_AfUdJVDRV-aJdPk0noOL04", use_context=True)

#message to be sent to user whenever they press start in the beginning
def start(update: Update, context: CallbackContext):
    update.message.reply_text("welcome")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)
    
def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
  
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  

updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
  
updater.start_polling()                
        #new comment
