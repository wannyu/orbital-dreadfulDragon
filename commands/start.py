import functions

"""
/start command in bot 
used only when user first starts using bot
"""
@bot.message_handler(commands=['start'])
def start(message):
    cur = conn.cursor()
    cur.execute("SELECT userID FROM users;")
    result = cur.fetchall()
    ids = []
    if result:
        for tupleid in result:
            ids = ids + [tupleid[0]]

    if message.from_user.id not in ids:
        # checking if user has /start before
        ids.append(message.from_user.id)

        today = get_today()

        cur = conn.cursor()
        values = (message.from_user.id, 1, 0, today, 0, 15, " ", 4)
        query = "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"
        cur.execute(query, values)
        conn.commit()
    else:
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET household = 1 WHERE userID = {message.from_user.id};")
        conn.commit()

    reply = bot.send_message(message.from_user.id, "Hello! I’m FoodSaver, I’m here to reduce food wastage. To get started, please input your username.")
    bot.register_next_step_handler(reply, input_username)
  
"""
helper function to take in user's username, then update to database
"""
def input_username(message):
    cur = conn.cursor()
    values = (message.text, message.from_user.id)
    query = "UPDATE users SET username = %s WHERE userID = %s;"
    cur.execute(query, values)
    conn.commit()
    reply = bot.send_message(message.from_user.id, f"Welcome {message.text}! Next, please state the number of people in your household (eg. 1, 2, 3 etc).")
    bot.register_next_step_handler(reply, nhousehold)
      
"""
helper function to take in user's household members, then update database
"""
def nhousehold(message):
    userID = message.from_user.id

    try: # checking if input is an integer
        int(message.text)
    except:
        reply = bot.send_message(message.from_user.id, "Please enter a valid number.")
        bot.register_next_step_handler(reply, nhousehold)
    else:
        household_size = int(message.text)

        if household_size <= 0 or household_size > 99:
            reply = bot.send_message(message.from_user.id, "Please enter a valid number. The accepted value should be within 1 to 99.")
            bot.register_next_step_handler(reply, nhousehold)

        else:
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET household = {household_size} WHERE userID = {message.from_user.id};")
            conn.commit()

            if household_size == 1:
                bot.send_message(message.from_user.id, f"There is {message.text} person in your household. You can start logging in your food. \nType /help to get guidance on how to use the bot.")
            elif household_size > 1:
                bot.send_message(message.from_user.id, f"There are {message.text} people in your household. You can start logging in your food. \nType /help to get guidance on how to use the bot.")

