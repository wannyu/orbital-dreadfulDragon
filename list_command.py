@bot.message_handler(commands=['list'])
def list(message):
    values = [message.from_user.id]
    cur = conn.cursor()
    #query = "SELECT foodID, foodName, servings, expiryDate FROM food WHERE userID = %s"
    query = "SELECT foodID, foodName, servings, expiryDate FROM food WHERE userID = %s ORDER BY expiryDate, foodName"
    cur.execute(query, values)
    cursor = cur.fetchall()
    reply = "This is the current food stock you have: \n"
    for row in cursor:
      food_name = row[1]
      servings = row[2]
      expiry_date = row[3]
      expiry_date = expiry_date.strftime('%d/%m/%Y')
      if servings == "1":
        reply += f"{food_name} ({servings} serving) expires {expiry_date} \n"
      else:
        reply += f"{food_name} ({servings} servings) expires {expiry_date} \n"
    bot.send_message(message.from_user.id, reply)
