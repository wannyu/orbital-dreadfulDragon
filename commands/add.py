import functions

"""
/add command in bot 
"""
@bot.message_handler(commands=['add'])
def add(message):
    reply = bot.send_message(message.from_user.id, 'Please state the food name, servings and expiry date. \nEg: bell pepper 2 19/11/2022')
    bot.register_next_step_handler(reply, add_sql)

def add_sql(message):
    cur = conn.cursor()
    terms = message.text.split(" ")

    isString = 0
    for j in range(len(terms) - 2):
        if terms[j].isalpha():
            isString += 1
            
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /add command.")
    elif len(terms) >= 3 and isString == len(terms) - 2 and terms[-2].isdigit() and validDate(terms[-1]):
        userID = message.from_user.id
        food_name = ""
        for i in range(len(terms) - 2):
            food_name += (terms[i]).lower() #convert all to lower case
            if i != len(terms) - 3:
                food_name += " "
        servings = int(terms[-2])
        expiry_date = terms[-1]
        expiry_date = dt.datetime.strptime(expiry_date, "%d/%m/%Y").date()

        today = get_today()
        if (expiry_date - today).days < 0: #expiry date earlier than today
            reply = bot.send_message(message.from_user.id, 'Invalid date! Date cannot be earlier than today. Please try again!')
            bot.register_next_step_handler(reply, add_sql)

        elif servings <= 0 or servings > 999:
            reply = bot.send_message(message.from_user.id, 'Invalid serving value! Value should be within 1-999. Please try again!')
            bot.register_next_step_handler(reply, add_sql)
        
        else:
            #check if the same food (with same expiry date already exists in database)
            cur = conn.cursor()
            checking_query = "SELECT foodID, foodName, servings, expiryDate FROM food WHERE food.foodName = %s AND food.expiryDate = %s AND userID = %s"
            checking_values = (food_name, expiry_date, message.from_user.id)
            cur.execute(checking_query, checking_values)
            data = cur.fetchall()

            if len(data) == 0:
                foodID = random.randint(1000, 9999)
                cur = conn.cursor()
                cur.execute('SELECT foodID FROM food')
                result = cur.fetchall()
                while foodID in result:
                    foodID =  random.randint(1000, 9999)
                # INSERT SQL code to add this into our database
                values = (foodID, food_name, servings, expiry_date, userID)
                cur = conn.cursor()
                add_query = "INSERT INTO food VALUES(%s, %s, %s, %s, %s);"
                cur.execute(add_query, values)
                conn.commit()

            else:
                existing_foodID = data[0][0]
                #existing record of food with same expiry date, just add
                total_servings = int(data[0][2]) + int(servings)
                cur = conn.cursor()
                add = f"UPDATE food SET servings = {total_servings} WHERE foodID = {existing_foodID}"
                cur.execute(add)
                conn.commit()

            reply = "This is added to your food stock: \n"
            if servings == 1:
                expiry_date = expiry_date.strftime('%d/%m/%Y')
                reply += f"{food_name} ({servings} serving) expires {expiry_date} \n"
            else:
                expiry_date = expiry_date.strftime('%d/%m/%Y')
                reply += f"{food_name} ({servings} servings) expires {expiry_date} \n"
            bot.send_message(message.from_user.id, reply)
            conn.commit()
    else:
        reply = bot.send_message(message.from_user.id, 'Invalid input! Please follow the specified format. Eg: "Apple 2 15/10/2022"')
        bot.register_next_step_handler(reply, add_sql)
