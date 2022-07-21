@bot.message_handler(commands=['edit_household_members'])
def edit_household_members(message):
    id = [message.from_user.id]
    cur = conn.cursor()
    query = "SELECT household FROM users WHERE userID = %s"
    cur.execute(query, id)
    result = cur.fetchall()
    result = result[0][0]
    if result == 1:
        reply = bot.send_message(message.from_user.id, f'You currently have {result} person in your household. Please state the updated number of people in your household (eg. 1, 2, 3 etc).')
    else:
        reply = bot.send_message(message.from_user.id, f'You currently have {result} people in your household. Please state the updated number of people in your household (eg. 1, 2, 3 etc).')
    bot.register_next_step_handler(reply, update_nhousehold)

def update_nhousehold(message):
    userID = message.from_user.id

    try:
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
            bot.send_message(message.from_user.id, f"You have successfully updated the number of people in your household to {message.text}.")
