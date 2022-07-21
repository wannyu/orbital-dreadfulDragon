import functions

"""
/addmany command in bot 
"""
@bot.message_handler(commands=['addmany'])
def addmany(message):
    reply = bot.send_message(message.from_user.id, 'Please state the food name, servings and expiry date. Insert a line break after each food. \nEg: \nbell pepper 2 19/11/2022\nbanana 5 18/7/2022\napple 2 20/8/2022')
    bot.register_next_step_handler(reply, addmany_sql)

    
"""
helper function to /addmany command
takes in message sent from user, check if the message is valid to add food items
valid food items (with valid name, valid servings, valid expiry date) will be added to database
invalid food items will not be added, will prompt user to reenter (with appropriate error messages)
"""
def addmany_sql(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /addmany command.")
    else:
        list = message.text.splitlines()
        confirmation_msg = "These are added to your food stock: \n"
        valid_counter = False 
        
        invalid_input_msg = "Invalid input(s)! These are not added to your food stock: \n\n"
        invalid_counter = False
        
        for k in list: #k is each food input

            cur = conn.cursor()
            terms = k.split(" ")

            isString = 0
            for j in range(len(terms) - 2):
                if terms[j].isalpha():
                    isString += 1            

            if len(terms) >= 3 and isString == len(terms) - 2 and terms[-2].isdigit() and validDate(terms[-1]):
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
                    invalid_input_msg += "(" + str(k) + ")" + ': Invalid date! Date cannot be earlier than today.\n'
                    invalid_counter = True
                   
                elif servings <= 0 or servings > 999:
                    invalid_input_msg += "(" + str(k) + ")" + ': Invalid serving value! Value should be within 1-999.\n'
                    invalid_counter = True

                else:
                    #check if the same food (with same expiry date already exists in database)
                    cur = conn.cursor()
                    checking_query = "SELECT foodID, foodName, servings, expiryDate FROM food WHERE food.foodName = %s AND food.expiryDate = %s AND userID = %s"
                    checking_values = (food_name, expiry_date, message.from_user.id)
                    cur.execute(checking_query, checking_values)
                    data = cur.fetchall()
                    valid_counter = True

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

                    if servings == 1:
                        expiry_date = expiry_date.strftime('%d/%m/%Y')
                        confirmation_msg += f"{food_name} ({servings} serving) expires {expiry_date} \n"
                    else:
                        expiry_date = expiry_date.strftime('%d/%m/%Y')
                        confirmation_msg += f"{food_name} ({servings} servings) expires {expiry_date} \n"

            else:
                invalid_input_msg += "(" + str(k) + ")" + ': Invalid input! Please follow the specified format. Eg: "Apple 2 15/10/2022"\n'
                invalid_counter = True

        if valid_counter:
            bot.send_message(message.from_user.id, confirmation_msg)
        if invalid_counter:
            reply = bot.send_message(message.from_user.id, invalid_input_msg + "\nPlease try again!")
            bot.register_next_step_handler(reply, addmany_sql)              
