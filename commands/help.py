"""
/help command in bot 
"""
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, """Here are some commands to use the features I provide. \n
    /add: Everytime you purchase food, simply log in the food, the amount (in servings) and its expiry date (in DD/MM/YYYY). I’ll help to keep track of it and remind you to consume it before it expires! 
    If you are unsure of servings portions, visit this link: https://www.healthhub.sg/live-healthy/2044/know-your-servings-photo-guide \n
    /addmany: If you have multiple food items to add to your foodstock, use this command to add it in all at once.\n
    /consume: Everytime you consume a certain type of food, tell me exactly what you consumed, the amount and I’ll remove it from the list. \n
    /consumemany: If you have consumed multiple food items, use this command to update me all at once.\n\n/list: This allows you to view a list of all the available food you have at any point in time. \n
    /edit: Use this command to edit the food name, servings or expiry date in your food stock.\n
    /edit_household_members: Use this command to edit any changes in the number of people in your household.\n
    /points: If you are curious about how many points you have accumulated, use this command to find out.\n
    /cancel: Use this command to get to the main menu if you want to exit /add, /addmany, /consume, /consumemany or /edit command. \n
    *IMPORTANT* \nPlease be consistent in entering the food names (eg. if previously /add was used to add an 'apple', when you /consume, 'apple' should be entered instead of 'apples'.""")
  

"""
reply user's message if the message is not a valid command and redirect user to /help 
"""
@bot.message_handler(func=lambda message: True)
def unknown(message):
    reply = message.text
    bot.reply_to(message, "Sorry, there is no such command. \nReply /help if you need guidance on how to use this bot.")
