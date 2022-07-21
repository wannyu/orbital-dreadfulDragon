from telebot import types

def rem_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    option1 = types.KeyboardButton('1')
    option2 = types.KeyboardButton('2')
    option3 = types.KeyboardButton('4')
    option4 = types.KeyboardButton('8')
    markup.add(option1, option2, option3, option4)
    return markup

@bot.message_handler(commands=['change_reminder'])
def change_reminder(message):
    data = [message.from_user.id]
    cur = conn.cursor()
    query = "SELECT reminderFreq FROM users WHERE userID = %s"
    cur.execute(query, data)
    result = cur.fetchall()
    result = result[0][0]

    reply = bot.send_message(message.from_user.id, f"Only the frequency of reminders for soon-to-be expired food can be changed. You are currently recieving reminders {result} time(s) per day. Please select your desired frequency.", reply_markup=rem_markup())
    bot.register_next_step_handler(reply, set_rem_freq)

def set_rem_freq(message):    
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /change_reminder command.")
    elif message.text == "1":
        cur = conn.cursor()
        values = (1, message.from_user.id)
        query = "UPDATE users SET reminderFreq = %s WHERE userID = %s;"
        cur.execute(query, values)
        conn.commit()
        bot.send_message(message.from_user.id, "You have opted to receive 1 reminder message daily. The message would be sent aproximately at 12am.")               
    elif message.text == "2":
        cur = conn.cursor()
        values = (2, message.from_user.id)
        query = "UPDATE users SET reminderFreq = %s WHERE userID = %s;"
        cur.execute(query, values)
        conn.commit()
        bot.send_message(message.from_user.id, "You have opted to receive 2 reminders message daily. The messages would be sent aproximately at 12am and 12pm.")               
    elif message.text == "4":
        cur = conn.cursor()
        values = (4, message.from_user.id)
        query = "UPDATE users SET reminderFreq = %s WHERE userID = %s;"
        cur.execute(query, values)
        conn.commit()
        bot.send_message(message.from_user.id, "You have opted to receive 4 reminders message daily. The messages would be sent aproximately at 12am, 6am, 12pm and 6pm.")               
    elif message.text == "8":
        cur = conn.cursor()
        values = (8, message.from_user.id)
        query = "UPDATE users SET reminderFreq = %s WHERE userID = %s;"
        cur.execute(query, values)
        conn.commit()
        bot.send_message(message.from_user.id, "You have opted to receive 8 reminders message daily. The messages would be sent aproximately at 12am, 3am, 6am, 9am, 12pm, 3pm, 6pm and 9pm.")               
    else:
        reply = bot.send_message(message.from_user.id, "Please select one of the buttons.")
        bot.register_next_step_handler(reply, set_rem_freq)     
        
