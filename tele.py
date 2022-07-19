#not in use anymore


!pip install python-telegram-bot
import logging
import random
#import mysql.connector as mysql
#import mysql.connector

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

#Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

token = "TOKEN"

updater = Updater(token, use_context=True)

import sqlite3
conn = sqlite3.connect('foodSaver.db', check_same_thread=False)

conn.execute('''
CREATE TABLE User (
    userID,
    points
);''')

conn.commit()

conn.execute('''
CREATE TABLE Food (
    foodID,
    foodName,
    servings,
    expiryDate DATE,
    userID
);''')

conn.commit()

def start(update: Update, context: CallbackContext):
    #create the user and update database

    #insert user into sql user table
    userID = random.randint(1000, 9999)
    #id_tup = conn.execute('SELECT userID FROM User')
    while userID in conn.execute('SELECT userID FROM User'):
        userID =  random.randint(1000, 9999)
    query = f'INSERT INTO User VALUES({userID}, 0)'
    conn.execute(query)
    update.message.reply_text(f"Hello! I’m FoodSaver, I’m here to reduce food wastage. Here are some commands to use the features I provide. \n /add: Everytime you purchase food, simply log in the food, the amount (in servings) and its expiry date. I’ll help to keep track of it and remind you to consume it before it expires! \n /consume: Everytime you consume a certain type of food, tell me exactly what you consumed, the amount and I’ll remove it from the list. \n /list: This allows you to view a list of all the available food you have at any point in time to prevent buying duplicates. \n Your user ID is {userID}")
  
def add(update: Update, _: CallbackContext) -> None:
    #take in 4 inputs, userID, foodname, servings and expiry date
    text = update.message.text
    logger.info(text)
    terms = text.split(" ")
    userID = terms[1]
    food_name = terms[2]
    servings = terms[3]
    expiry_date = terms[4]

    foodID = random.randint(1000, 9999)
    while foodID in conn.execute('SELECT foodID FROM Food'):
        foodID =  random.randint(1000, 9999)

    # INSERT SQL code to add this into our database
    values = (foodID, food_name, servings, expiry_date, userID)
    #add_query = f"INSERT INTO Food VALUES({foodID}, {food_name}, {servings}, {expiry_date}, {userID});"
    add_query = "INSERT INTO Food VALUES(?, ?, ?, ?, ?);"
    conn.execute(add_query, values)
    reply = f"This is added to your food stock: \n"
    if servings == "1":
        reply += f"{food_name} ({servings} serving) expires {expiry_date} \n" 
    else:
        reply += f"{food_name} ({servings} servings) expires {expiry_date} \n" 
    update.message.reply_text(reply)

def list(update: Update, _: CallbackContext) -> None:
    #take in 1 input userID
    text = update.message.text
    logger.info(text)
    terms = text.split(" ")
    userID = terms[1]
    values = [userID]
    query = "SELECT foodID, foodName, servings, expiryDate FROM Food WHERE userID = ?"
    cursor = conn.execute(query, values)
    reply = "This is the current food stock you have: \n"
    for row in cursor:
      food_name = row[1]
      servings = row[2]
      expiry_date = row[3]
      if servings == "1":
        reply += f"{food_name} ({servings} serving) expires {expiry_date} \n" 
      else:
        reply += f"{food_name} ({servings} servings) expires {expiry_date} \n" 
    update.message.reply_text(reply)


def consume(update: Update, _: CallbackContext) -> None:
    #take in 3 inputs, userID, foodname and servings consumed
    text = update.message.text
    logger.info(text)
    terms = text.split(" ")
    userID = terms[1]
    food_name = terms[2]
    servings_consumed = terms[3]

    #update SQL 
    values = [food_name, userID] 
    query = "SELECT foodID, expiryDate FROM Food WHERE foodName = ? AND userID = ?"
    food = tuple(conn.execute(query, values))
    if len(food) == 1:
      #update the servings of the only row
      earliest_foodID = food[0][0]
    else:
      #choose the one with earlier expiry date
      data = [food_name, userID] 
      earliest_expiry_query = "SELECT foodID, MIN(expiryDate) FROM Food WHERE foodName = ? AND userID = ?"
      earliest_expiry = tuple(conn.execute(earliest_expiry_query, data))
      earliest_foodID = earliest_expiry[0][0]
      conn.commit()
    
    servings = tuple(conn.execute(f"SELECT servings FROM Food WHERE foodID = {earliest_foodID}"))[0][0]

    servings_left = int(servings) - int(servings_consumed)
    if servings_left == 0:
      #delete
      conn.execute(f"DELETE FROM Food WHERE foodID = {earliest_foodID}")
      conn.commit()
    else:
      #update
      conn.execute(f"UPDATE Food SET servings = {servings_left} WHERE foodID = {earliest_foodID}")
      conn.commit()

    reply = f"This is removed from your food list: \n {food_name} ({servings_consumed} serving(s))\n"
    update.message.reply_text(reply)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("list", list))
    dispatcher.add_handler(CommandHandler("consume", consume))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    ## SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()  
  
