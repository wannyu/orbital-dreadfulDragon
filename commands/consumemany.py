import functions

"""
/consumemany command in bot 
"""
@bot.message_handler(commands=['consumemany'])
def consumemany(message):
    data = [message.from_user.id]
    cur = conn.cursor()
    query = "SELECT * FROM food WHERE userID = %s"
    cur.execute(query, data)
    result = cur.fetchall()
    
    # user doesnt have anything in their list, dont let them consume
    if len(result) == 0:
        reply = bot.send_message(message.from_user.id, 'Sorry, you do not have any food in your list. Use /add to add some food before comsuming them!')
    else:
        reply = bot.send_message(message.from_user.id, 'Please state the food name and servings consumed. Insert a line break after each food.\nEg:\nbell pepper 1\nbanana 2\napple 5')
        bot.register_next_step_handler(reply, consumemany_sql)     
        
"""
helper function for /consumemany command 
takes in message sent from user, check if the message is valid to consume food item
valid food items (with valid name, valid servings) will be removed from database
invalid food items will not be removed, will prompt user to reenter (with appropriate error messages)
"""
def consumemany_sql(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /consumemany command.")
    else:
        list = message.text.splitlines()
        confirmation_msg = "This is removed from your food list:\n"
        valid_counter = False 
        
        invalid_input_msg = "Invalid input(s)! These are not removed from your food stock:\n\n"
        invalid_counter = False

        today = get_today()
        
        total_servings_consumed = 0
        points_given = 0
        for k in list: #k is each food input
            terms = k.split(" ")

            isString = 0
            for j in range(len(terms) - 1):
                if terms[j].isalpha():
                    isString += 1

            if len(terms) >= 2 and isString == len(terms) - 1 and terms[-1].isdigit():
                food_name = ""
                for i in range(len(terms) - 1):
                    food_name += (terms[i]).lower() #convert all to lower case
                    if i != len(terms) - 2:
                        food_name += " "
                servings_consumed = int(terms[-1])

                ###update Food SQL
                values = [food_name, message.from_user.id]
                cur = conn.cursor()
                query = "SELECT foodID, servings, expiryDate FROM food WHERE foodName = %s AND userID = %s ORDER BY expiryDate"
                cur.execute(query, values)
                food = cur.fetchall()

                if len(food) == 0: # the input food by user isnt in the foodstock
                    invalid_input_msg += "(" + str(k) + ")" + ': Invalid input! You do not have this in your food stock.\n'
                    invalid_counter = True

                elif servings_consumed <= 0:
                    invalid_input_msg += "(" + str(k) + ")" + ': Invalid serving value! Value should at least be 1.\n'
                    invalid_counter = True

                else:
                    servings_sum = 0
                    for foodrow in food:
                        servings_sum += foodrow[1]

                    if servings_consumed > servings_sum:
                        invalid_input_msg += "(" + str(k) + ")" + ': Your serving input is more than what you have in your food stock!\n'
                        invalid_counter = True

                    else: # this whole else segment involves consuming food (and update database)
                        if len(food) == 1:
                            # theres only 1 food with that name, juz update the servings of the only row
                            earliest_foodID = food[0][0]
                            servings_available = food[0][1]
                            expiry_date = food[0][2]
                            days_left = ((expiry_date - today).days)
                            if days_left == 0:
                                days_left = 1
                            points_given += days_left * servings_consumed


                            if servings_consumed == servings_available:
                                # delete from database
                                cur = conn.cursor()
                                cur.execute(f"DELETE FROM food WHERE foodID = {earliest_foodID} AND userID = {message.from_user.id}")
                                conn.commit()

                            else:
                                # update database
                                servings_left = servings_available - servings_consumed
                                cur = conn.cursor()
                                cur.execute(f"UPDATE food SET servings = {servings_left} WHERE foodID = {earliest_foodID} AND userID = {message.from_user.id}")
                                conn.commit()     

                        else: # len(food) > 1
                            # sum all servings with diff expiry dates, then start deducting servings from earliest expiry
                            servings_sum = 0
                            for foodrow in food:
                                servings_sum += foodrow[1]

                            if servings_consumed == servings_sum:
                                # all the food across diff expiry dates are consumed 
                                for foodrow in food:
                                    foodid_to_delete = foodrow[0]
                                    cur = conn.cursor()
                                    cur.execute(f"DELETE FROM food WHERE foodID = {foodid_to_delete} AND userID = {message.from_user.id}")
                                    conn.commit()
                                    
                                    expiry_date = foodrow[2]
                                    days_left = ((expiry_date - today).days)
                                    if days_left == 0:
                                        days_left = 1
                                    points_given += days_left * foodrow[1]

                            else:
                                # check which rows need to deleted/updated based on how many servings are consumed (according to order of expiry)
                                servings_consumed_counter = servings_consumed #use counter as servings_consumed is required later on
                                for foodrow in food:
                                    if servings_consumed_counter - foodrow[1] >= 0:
                                        # delete this row 
                                        foodid_to_delete = foodrow[0]
                                        cur = conn.cursor()
                                        cur.execute(f"DELETE FROM food WHERE foodID = {foodid_to_delete} AND userID = {message.from_user.id}")
                                        conn.commit()
                                        expiry_date = foodrow[2]
                                        days_left = ((expiry_date - today).days)
                                        if days_left == 0:
                                            days_left = 1
                                        points_given += days_left * foodrow[1]

                                    elif servings_consumed_counter > 0:
                                        # update this row
                                        foodid_to_update = foodrow[0]
                                        cur = conn.cursor()
                                        update_serving_value = foodrow[1] - servings_consumed_counter
                                        cur.execute(f"UPDATE food SET servings = {update_serving_value} WHERE foodID = {foodid_to_update} AND userID = {message.from_user.id}")
                                        conn.commit()
                                        expiry_date = foodrow[2]
                                        days_left = ((expiry_date - today).days)
                                        if days_left == 0:
                                            days_left = 1
                                        points_given += days_left * servings_consumed_counter

                                    servings_consumed_counter = servings_consumed_counter - foodrow[1]

                        valid_counter = True 
                        confirmation_msg += f"{food_name} ({servings_consumed} serving(s))\n"
     
                        total_servings_consumed += servings_consumed

            else:
                invalid_input_msg += "(" + str(k) + ")" +  ': Invalid input! Please follow the specified format. Eg: "Apple 2"\n'
                invalid_counter = True
    
        if valid_counter:
            confirmation_msg += "You are awarded " + str(points_given) + " point(s) for consuming them before their expiry. Good job!"
            bot.send_message(message.from_user.id, confirmation_msg)
            
            ### update User SQL (servings consumed for the week)
            cur = conn.cursor()
            cur.execute(f"SELECT weeklyServings FROM users WHERE userID = {message.from_user.id}")
            result = cur.fetchall()
            updated_servings = int(result[0][0]) + int(total_servings_consumed)

            cur = conn.cursor()
            cur.execute(f"UPDATE users SET weeklyServings = {updated_servings} WHERE userID = {message.from_user.id};")
            conn.commit()

            ### award points 
            cur = conn.cursor()
            cur.execute(f"SELECT points FROM users WHERE userID = {message.from_user.id}")
            result = cur.fetchall()
            updated_points = int(result[0][0]) + points_given

            cur = conn.cursor()
            cur.execute(f"UPDATE users SET points = {updated_points} WHERE userID = {message.from_user.id};")
            conn.commit()
            
        if invalid_counter:
            reply = bot.send_message(message.from_user.id, invalid_input_msg + "\nPlease try again!")
            bot.register_next_step_handler(reply, consumemany_sql)    
    
