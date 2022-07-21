@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.send_message(message.from_user.id,"You are currently in the main menu and have no operation to cancel. \nPlease only use /cancel when you want to exit the /add, /addmany, /consume, /consumemany or /edit operation.")
