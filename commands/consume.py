@bot.message_handler(commands=['consume'])
def consume(message):
    data = [message.from_user.id]
    cur = conn.cursor()
    query = "SELECT * FROM food WHERE userID = %s"
    cur.execute(query, data)
    result = cur.fetchall()
    
    #user doesnt have anything in their list
    if len(result) == 0:
        reply = bot.send_message(message.from_user.id, 'Sorry, you do not have any food in your list. Use /add to add some food before comsuming them!')
    else:
        reply = bot.send_message(message.from_user.id, 'Please state the food name and servings consumed. \nEg: bell pepper 1')
        bot.register_next_step_handler(reply, consume_sql)



def consume_sql(message):
    terms = message.text.split(" ")
    userID = message.from_user.id
    
    #getting today's date
    sg = datetime.now(tz)
    today = sg.date()

    isString = 0
    for j in range(len(terms) - 1):
        if terms[j].isalpha():
            isString += 1
            
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /consume command.")
    elif len(terms) >= 2 and isString == len(terms) - 1 and terms[-1].isdigit():
        food_name = ""
        for i in range(len(terms) - 1):
            food_name += (terms[i]).lower() #convert all to lower case
            if i != len(terms) - 2:
                food_name += " "
        servings_consumed = int(terms[-1])

        ###update Food SQL
        values = [food_name, userID]
        cur = conn.cursor()
        query = "SELECT foodID, servings, expiryDate FROM food WHERE foodName = %s AND userID = %s ORDER BY expiryDate"
        cur.execute(query, values)
        food = cur.fetchall()

        if len(food) == 0: # the input food by user isnt in the foodstock
            reply = bot.send_message(message.from_user.id, 'Invalid input! You do not have this in your food stock. Please try again!')
            bot.register_next_step_handler(reply, consume_sql)
   
        elif servings_consumed <= 0:
            reply = bot.send_message(message.from_user.id, 'Invalid serving value! Value should at least be 1. Please try again!')
            bot.register_next_step_handler(reply, consume_sql)
            
        else:
            servings_sum = 0
            for foodrow in food:
                servings_sum += foodrow[1]
                
            if servings_consumed > servings_sum:
                reply = bot.send_message(message.from_user.id, 'Your serving input is more than what you have in your food stock! Please try again with the correct number of servings.')
                bot.register_next_step_handler(reply, consume_sql)
                
            else: #this whole else segment involves consuming food (and update database)
                points_given = 0
                if len(food) == 1:
                    #theres only 1 food with that name, juz update the servings of the only row
                    earliest_foodID = food[0][0]
                    servings_available = food[0][1]
                    expiry_date = food[0][2]
                    days_left = ((expiry_date - today).days)
                    if days_left == 0:
                        days_left = 1
                    points_given = days_left * servings_consumed

                    if servings_consumed == servings_available:
                        #delete from database
                        cur = conn.cursor()
                        cur.execute(f"DELETE FROM food WHERE foodID = {earliest_foodID} AND userID = {message.from_user.id}")
                        conn.commit()

                    else:
                        #update database
                        servings_left = servings_available - servings_consumed
                        cur = conn.cursor()
                        cur.execute(f"UPDATE food SET servings = {servings_left} WHERE foodID = {earliest_foodID} AND userID = {message.from_user.id}")
                        conn.commit()     
                    
                else: #len(food) > 1
                    #sum all servings with diff expiry dates, then start deducting servings from earliest expiry
                    servings_sum = 0
                    for foodrow in food:
                        servings_sum += foodrow[1]

                    if servings_consumed == servings_sum:
                        #all the food across diff expiry dates are consumed 
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
                        #check which rows need to deleted/updated based on how many servings are consumed (according to order of expiry)
                        servings_consumed_counter = servings_consumed #use counter as servings_consumed is required later on
                        for foodrow in food:
                            if servings_consumed_counter - foodrow[1] >= 0:
                                #delete this row 
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
                                #update this row
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

                ###update User SQL (servings consumed for the week)
                cur = conn.cursor()
                cur.execute(f"SELECT weeklyServings FROM users WHERE userID = {message.from_user.id}")
                result = cur.fetchall()
                updated_servings = int(result[0][0]) + int(servings_consumed)

                cur = conn.cursor()
                cur.execute(f"UPDATE users SET weeklyServings = {updated_servings} WHERE userID = {message.from_user.id};")
                conn.commit()
                
                ###award points 
                cur = conn.cursor()
                cur.execute(f"SELECT points FROM users WHERE userID = {message.from_user.id}")
                result = cur.fetchall()
                updated_points = int(result[0][0]) + points_given

                cur = conn.cursor()
                cur.execute(f"UPDATE users SET points = {updated_points} WHERE userID = {message.from_user.id};")
                conn.commit()
                
                ###bot send confirmation message + points awarded
                reply = f"This is removed from your food list: \n{food_name} ({servings_consumed} serving(s))\nYou are awarded {points_given} point(s) for consuming it before its expiry. Good job!"
                bot.send_message(message.from_user.id, reply)   
     
    else:
        reply = bot.send_message(message.from_user.id, 'Invalid input! Please follow the specified format. Eg: "Apple 2"')
        bot.register_next_step_handler(reply, consume_sql)
        
