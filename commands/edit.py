from telebot import types
import functions

"""
creating custom keyboard that has buttons for users to select edit category
"""
def gen_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    food_name = types.KeyboardButton('Food Name')
    servings = types.KeyboardButton('Servings')
    expiry = types.KeyboardButton('Expiry Date')
    markup.add(food_name, servings, expiry)
    return markup

id_and_food_dict = {} # dictionary to keep track of current user's food to edit

"""
/edit command in bot 
for user to edit existing food in foodstock
"""
@bot.message_handler(commands=['edit'])
def edit(message):
    data = [message.from_user.id]
    cur = conn.cursor()
    query = "SELECT * FROM food WHERE userID = %s"
    cur.execute(query, data)
    result = cur.fetchall()
    
    # user doesnt have anything in their list, dont allow edit to happen
    if len(result) == 0:
        reply = bot.send_message(message.from_user.id, 'Sorry, you do not have any food in your list. Use /add to add some food before editing them!')
    else:
        reply = bot.send_message(message.from_user.id, "Please input the food that you want to edit.")
        bot.register_next_step_handler(reply, choose_food)
        
"""
helper function for /edit
take in input from user's message, check if the food item is in his foodstock
then determine how many entries there are and move on to the corresponding follow up functions
    only 1 entry: move straight to edit_sql function
    more than 1 entry: go to choose_option function first
"""
def choose_food(message):
    foodname = message.text.lower()
    userID = message.from_user.id
    
    values = [foodname, userID]
    cur = conn.cursor()
    query = "SELECT foodName, servings, expiryDate FROM food WHERE foodName = %s AND userID = %s ORDER BY expiryDate"
    cur.execute(query, values)
    foodlist = cur.fetchall() # list can have 1 or more items (if theres 2 apple with diff expiry dates then there will be 2 entries)
    
    global id_and_food_dict

    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
        
    elif len(foodlist) == 0: # no such food inside
        reply = bot.send_message(message.from_user.id, "Invalid input! You do not have this in your food stock. Please try again!")
        bot.register_next_step_handler(reply, choose_food)
        
    elif len(foodlist) == 1: # theres exactly 1 food with this name
        name = foodlist[0][0]
        serving = foodlist[0][1]
        expiry = foodlist[0][2]
        expiry = expiry.strftime('%d/%m/%Y')
        
        id_and_food_dict[userID] = foodlist
        
        reply = bot.send_message(message.from_user.id, f"Here is what you currently have:\n{name} ({serving} serving(s)) expiring on {expiry}\nSelect the category you want to edit:", reply_markup=gen_markup())
        bot.register_next_step_handler(reply, edit_sql)
    
    else:
        text = ""
        for i in range(len(foodlist)):
            name = foodlist[i][0]
            serving = foodlist[i][1]
            expiry = foodlist[i][2]
            expiry = expiry.strftime('%d/%m/%Y')
            text += str(i + 1) + " -- " + name + " (" + str(serving) + " serving(s)) expiring on " + expiry + "\n"

        id_and_food_dict[userID] = foodlist
        
        reply = bot.send_message(message.from_user.id, f"Here is what you currently have:\n{text}\nSelect the option you want to edit.")
        bot.register_next_step_handler(reply, choose_option)
        
"""
helper function for /edit, after choose_food function
take in input from user's message, check if the input is a valid option (one of the options offered)
if valid, move on to next function (edit_sql)
if invalid, prompt user to reenter one of the given options
"""
def choose_option(message):
    foodoption = message.text
    userID = message.from_user.id
    
    global id_and_food_dict
    original_foodlist = id_and_food_dict[userID]
    
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
    else:    
        try:
            int(foodoption)
        except:
            reply = bot.send_message(message.from_user.id, "Invalid option! Please select one of the options offered above.")
            bot.register_next_step_handler(reply, choose_option)
        else:
            if int(foodoption) > len(original_foodlist) or int(foodoption) <= 0: # invalid option input (more or less than what was offered)
                reply = bot.send_message(message.from_user.id, f"Invalid option! Please select one of the options offered above.")
                bot.register_next_step_handler(reply, choose_option)

            else:
                new_foodlist = original_foodlist[int(foodoption) - 1]
                id_and_food_dict[userID] = [new_foodlist]

                reply = bot.send_message(message.from_user.id, f"Select the category you want to edit:", reply_markup=gen_markup())
                bot.register_next_step_handler(reply, edit_sql)

"""
helper function for /edit
take in input from user's message, check if the message is one of the given button
if valid, move on to the category to be edited
if invalid, prompt user to click one of the buttons provided
"""             
def edit_sql(message: types.Message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
    elif message.text == "Food Name":
        reply = bot.send_message(message.from_user.id, "Please input the new food name.")
        bot.register_next_step_handler(reply, edit_food_name_sql)               
    elif message.text == "Servings":
        reply = bot.send_message(message.from_user.id, "Please input the new number of servings.")
        bot.register_next_step_handler(reply, edit_servings_sql)      
    elif message.text == "Expiry Date":
        reply = bot.send_message(message.from_user.id, "Please input the new expiry date (in the form of DD/MM/YYYY).")
        bot.register_next_step_handler(reply, edit_expiry_sql)
    else:
        reply = bot.send_message(message.from_user.id, "Please select one of the buttons.")
        bot.register_next_step_handler(reply, edit_sql)     
    
    
"""
helper function for /edit (to edit food name)
take in new name, check if new name is valid
if valid, update database
if invalid, prompt user to input new name
"""         
def edit_food_name_sql(message): 
    userID = message.from_user.id
    terms = message.text.split(" ")
    
    isString = 0
    for i in range(len(terms)):
        if terms[i].isalpha():
            isString += 1
    
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
    elif isString != len(terms): # input name isnt all alphabets
        reply = bot.send_message(message.from_user.id, 'Invalid input! Please make sure that the new name contains alphabets only.')
        bot.register_next_step_handler(reply, edit_food_name_sql)
    else:
        new_name = ""
        for i in range(len(terms)):
            new_name += (terms[i]).lower() # convert all to lower case
            if i != len(terms) - 1:
                new_name += " "
                
        global id_and_food_dict
        foodlist = id_and_food_dict[userID]
        foodlist = foodlist[0] # getting tuple out of list
        old_name = foodlist[0]
        servings = int(foodlist[1])
        expiry = foodlist[2]
        
        if old_name == new_name:
            reply = bot.send_message(message.from_user.id, 'Invalid name! Please enter a name different from the original name.')
            bot.register_next_step_handler(reply, edit_food_name_sql) 
            
        else:
            # check if there is an entry of the new name and the same expiry date. if there is then add the 2 servings up and update it and delete row with old name
            cur = conn.cursor()
            values = (new_name, expiry.strftime('%Y-%m-%d'), message.from_user.id)
            cur.execute("SELECT foodID, servings FROM food WHERE foodName = %s AND expiryDate = %s AND userID = %s", values)
            cursor = cur.fetchall()
            if len(cursor) > 0: # theres an existing entry
                newname_foodID = cursor[0][0]
                newname_old_servings = cursor[0][1]
                newname_new_servings = newname_old_servings + servings

                # update the added up servings
                cur = conn.cursor()
                updated_values = (newname_new_servings, newname_foodID, message.from_user.id)
                cur.execute(f"UPDATE food SET servings = %s WHERE foodID = %s AND userID = %s", updated_values) 
                conn.commit() 

                # get id of old name then delete that row
                cur = conn.cursor()
                values = (old_name, servings, expiry.strftime('%Y-%m-%d'), message.from_user.id)
                cur.execute("SELECT foodID FROM food WHERE foodName = %s AND servings = %s AND expiryDate = %s AND userID = %s", values)
                cursor = cur.fetchall()
                oldname_foodID = cursor[0][0]

                cur = conn.cursor()
                values = (oldname_foodID, message.from_user.id)
                cur.execute(f"DELETE FROM food WHERE foodID = %s AND userID = %s", values)
                conn.commit() 

            else: # new name doesnt exist yet, simply update food name
                cur = conn.cursor()
                values = (old_name, servings, expiry.strftime('%Y-%m-%d'), message.from_user.id)
                cur.execute("SELECT foodID FROM food WHERE foodName = %s AND servings = %s AND expiryDate = %s AND userID = %s", values)
                cursor = cur.fetchall()
                foodID = cursor[0][0]

                # update food name
                cur = conn.cursor()
                updated_values = (new_name, foodID, message.from_user.id)
                cur.execute(f"UPDATE food SET foodName = %s WHERE foodID = %s AND userID = %s", updated_values)
                conn.commit() 

            # delete from dict
            del id_and_food_dict[message.from_user.id]

            bot.send_message(message.from_user.id, f"Food name successfully updated from {old_name} to {new_name}.")

   
"""
helper function for /edit (to edit food servings)
take in new servings, check if value is valid
if valid, update database
if invalid, prompt user to input new value
"""         
def edit_servings_sql(message):
    userID = message.from_user.id
    
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
    else:
        try:
            int(message.text)
        except:
            reply = bot.send_message(message.from_user.id, "Please enter a valid number.")
            bot.register_next_step_handler(reply, edit_servings_sql)
        else:
            new_servings = int(message.text)

            if new_servings < 0 or new_servings > 999:
                reply = bot.send_message(message.from_user.id, "Please enter a valid number. The accepted value should be within 0 to 999.")
                bot.register_next_step_handler(reply, edit_servings_sql)

            else:
                global id_and_food_dict
                foodlist = id_and_food_dict[userID]
                foodlist = foodlist[0] # getting tuple out of list
                name = foodlist[0]
                old_servings = int(foodlist[1])
                expiry = foodlist[2]
                
                if old_servings == new_servings:
                    reply = bot.send_message(message.from_user.id, 'Invalid servings! Please enter a value different from the original servings.')
                    bot.register_next_step_handler(reply, edit_servings_sql) 
            
                else:
                    cur = conn.cursor()
                    values = (name, old_servings, expiry.strftime('%Y-%m-%d'), message.from_user.id)
                    cur.execute("SELECT foodID FROM food WHERE foodName = %s AND servings = %s AND expiryDate = %s AND userID = %s", values)
                    cursor = cur.fetchall()
                    foodID = cursor[0][0]

                    # delete from dict
                    del id_and_food_dict[message.from_user.id]

                    # update
                    if int(new_servings) != 0:
                        cur = conn.cursor()
                        updated_values = (new_servings, foodID, message.from_user.id)
                        cur.execute(f"UPDATE food SET servings = %s WHERE foodID = %s AND userID = %s", updated_values)
                        conn.commit()
                        bot.send_message(message.from_user.id, f"Number of servings of {name} successfully updated from {old_servings} to {new_servings}.")
                    else:
                        cur = conn.cursor()
                        data = (foodID, message.from_user.id)
                        cur.execute(f"DELETE FROM food WHERE foodID = %s AND userID = %s", data)
                        conn.commit()
                        if old_servings == 1:
                            bot.send_message(message.from_user.id, f"{old_servings} serving of {name} is removed from your list.")  
                        else:
                            bot.send_message(message.from_user.id, f"{old_servings} servings of {name} is removed from your list.") 

    
"""
helper function for /edit (to edit food expiry)
take in new expiry, check if date is valid
if valid, update database
if invalid, prompt user to input new date
"""     
def edit_expiry_sql(message):
    userID = message.from_user.id
    expiry_date = message.text
    
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, "You exited /edit command.")
    else:
        try: # checking if it can be converted to dateform
            dt.datetime.strptime(expiry_date, "%d/%m/%Y").date()
        except:
            # input isnt a date form (can be str, int etc)
            reply = bot.send_message(message.from_user.id, "Please enter a valid expiry date.")
            bot.register_next_step_handler(reply, edit_expiry_sql)
        else:
            today = get_today()
            if not validDate(expiry_date):
                # date isnt a valid date
                reply = bot.send_message(message.from_user.id, "Please enter a valid expiry date.")
                bot.register_next_step_handler(reply, edit_expiry_sql)
            elif (dt.datetime.strptime(expiry_date, "%d/%m/%Y").date() - today).days < 0: 
                # expiry date earlier than today
                reply = bot.send_message(message.from_user.id, 'Invalid date! Date cannot be earlier than today. Please try again!')
                bot.register_next_step_handler(reply, edit_expiry_sql)
            else:
                global id_and_food_dict
                foodlist = id_and_food_dict[userID]
                foodlist = foodlist[0] # getting tuple out of list
                name = foodlist[0]
                servings = int(foodlist[1])
                old_expiry = foodlist[2]
                new_expiry = dt.datetime.strptime(expiry_date, "%d/%m/%Y").date()
                
                if old_expiry == new_expiry:
                    reply = bot.send_message(message.from_user.id, 'Invalid date! Please enter a date different from the original expiry.')
                    bot.register_next_step_handler(reply, edit_expiry_sql) 
            
                else:
                    # delete from dict
                    del id_and_food_dict[message.from_user.id]

                    ## chekcing for name with same new expiry
                    # check if there is an entry of the same name and the new expiry date. if there is then add the 2 servings up and update it and delete row with old expiry
                    cur = conn.cursor()
                    values = (name, new_expiry.strftime('%Y-%m-%d'), message.from_user.id)
                    cur.execute("SELECT foodID, servings FROM food WHERE foodName = %s AND expiryDate = %s AND userID = %s", values)
                    cursor = cur.fetchall()
                    if len(cursor) > 0: #theres an existing entry
                        newexpiry_foodID = cursor[0][0]
                        newexpiry_old_servings = cursor[0][1]
                        newexpiry_new_servings = newexpiry_old_servings + servings

                        # update the added up servings
                        cur = conn.cursor()
                        updated_values = (newexpiry_new_servings, newexpiry_foodID, message.from_user.id)
                        cur.execute(f"UPDATE food SET servings = %s WHERE foodID = %s AND userID = %s", updated_values) 
                        conn.commit() 

                        # get id of old expiry then delete that row
                        cur = conn.cursor()
                        values = (name, servings, old_expiry.strftime('%Y-%m-%d'), message.from_user.id)
                        cur.execute("SELECT foodID FROM food WHERE foodName = %s AND servings = %s AND expiryDate = %s AND userID = %s", values)
                        cursor = cur.fetchall()
                        oldexpiry_foodID = cursor[0][0]

                        cur = conn.cursor()
                        values = (oldexpiry_foodID, message.from_user.id)
                        cur.execute(f"DELETE FROM food WHERE foodID = %s AND userID = %s", values)
                        conn.commit() 

                    else: # new expiry doesnt exist yet, simply update expiry
                        cur = conn.cursor()
                        values = (name, servings, old_expiry.strftime('%Y-%m-%d'), message.from_user.id)
                        cur.execute("SELECT foodID FROM food WHERE foodName = %s AND servings = %s AND expiryDate = %s AND userID = %s", values)
                        cursor = cur.fetchall()
                        foodID = cursor[0][0]
                        
                        # update
                        cur = conn.cursor()
                        updated_values = (new_expiry.strftime('%Y-%m-%d'), foodID, message.from_user.id)
                        cur.execute(f"UPDATE food SET expiryDate= %s WHERE foodID = %s AND userID = %s", updated_values)
                        conn.commit() 
                    bot.send_message(message.from_user.id, f"Expiry date of {name} successfully updated from {old_expiry.strftime('%d/%m/%Y')} to {new_expiry.strftime('%d/%m/%Y')}")
