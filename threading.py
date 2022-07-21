import functions
import threading_functions

def threading_func():
    while True:
        cur = conn.cursor()
        cur.execute("SELECT userID FROM users;")
        result = cur.fetchall()
        ids = []
        if result:
            for tupleid in result:
                ids = ids + [tupleid[0]]
                    
        today = get_today()

        cur = conn.cursor()
        values = (today,)
        check_query = "SELECT * FROM reminders WHERE reminders.date = %s;"
        cur.execute(check_query, values)
        db_reminders_result = cur.fetchall()

        if len(db_reminders_result) == 0:
            cur = conn.cursor()
            values = (today, 0, 0, 0, 0, 0, 0, 0, 0)
            insert_query = "INSERT INTO reminders VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cur.execute(insert_query, values)
            conn.commit()

            cur = conn.cursor()
            values = (today,)
            check_query = "SELECT * FROM reminders WHERE reminders.date = %s;"
            cur.execute(check_query, values)
            db_reminders_result = cur.fetchall()
         

    
        for id in ids:
            
            ##### weekly leaderboards #####
            #sends on sun, mon and thur 12am
            daytoday = today.strftime('%A')
            if (daytoday == "Sunday" or daytoday == "Monday" or daytoday == "Thursday") and sg.hour == 0 and cansend(db_reminders_result, 0):
                points_query = "SELECT userID, points, username FROM users ORDER BY points DESC"
                cur = conn.cursor()
                cur.execute(points_query)
                result = cur.fetchall()
                #we display top 3 users?
                reply = "The leaderboard for this week:\n"

                try:
                    reply += "FIRST PLACE 🥇: " + result[0][2] + " -- " + str(result[0][1]) + " points" + "\n"
                    reply += "SECOND PLACE 🥈: " + result[1][2] + " -- " + str(result[1][1]) + " points" + "\n"
                    reply += "THIRD PLACE 🥉: " + result[2][2] + " -- " + str(result[2][1]) + " points" + "\n"
                except Exception as e:
                    print(e)
                    
                if id == result[0][0]: #first
                    reply += "\nCONGRATULATIONS 🎉 🥳 👏  You are the best food saver this week! 😎"
                elif id == result[1][0]: #second
                    reply += "\nCONGRATULATIONS 🎉 🥳 👏 You place second this week! Keep up the good work!"
                elif id == result[2][0]: #third
                    reply += "\nCONGRATULATIONS 🎉 🥳 👏 You place third this week! Keep striving to be the best food saver!"
                else:
                    reply += "\nYou missed the leaderboard by just a little! Try to get it next week!"
                cus_send_message(id, reply)
            
            
            
            ##### send reminder for soon to be expired food #####
            cur = conn.cursor()
            values = (id,)
            query = "SELECT reminderFreq FROM users WHERE userID = %s;"
            cur.execute(query, values)
            rem_freq = cur.fetchall()[0][0]

            if (sg.hour == 0 or sg.hour == 3 or sg.hour == 6 or sg.hour == 9 or sg.hour == 12 or sg.hour == 15 or sg.hour == 18 or sg.hour == 21) and canandshouldsend(db_reminders_result, sg.hour, rem_freq):
                data = [id]
                cur = conn.cursor()
                expiry_query = "SELECT * FROM food WHERE userID = %s ORDER BY foodName"
                cur.execute(expiry_query, data)
                result = cur.fetchall()
                conn.commit()

                expiring_today = 0
                expiring_oneday = 0
                expiring_threedays = 0
                expiring_today_food = ""
                expiring_oneday_food = ""
                expiring_threedays_food = ""

                for i in result:
                    expiry_date = i[3] 
                    food_name = i[1]
                    days_diff = (expiry_date - today).days
                    if days_diff == 0:
                        if expiring_today > 0:
                            expiring_today_food += ", "
                        expiring_today_food += food_name
                        expiring_today += 1
                    elif days_diff == 1:
                        if expiring_oneday > 0:
                            expiring_oneday_food += ", "
                        expiring_oneday_food += food_name
                        expiring_oneday += 1
                    elif days_diff == 3:
                        if expiring_threedays > 0:
                            expiring_threedays_food += ", "
                        expiring_threedays_food += food_name
                        expiring_threedays += 1

                reply = "You have food expiring soon!\n"
                if expiring_today != 0:
                    reply += "Expiring today: " + expiring_today_food + "\n"
                if expiring_oneday != 0:
                    reply += "Expiring in 1 day: " + expiring_oneday_food + "\n"
                if expiring_threedays != 0:
                    reply += "Expiring in 3 days: " + expiring_threedays_food + "\n"
                reply += "Consume them soon, don’t let them go to waste!"

                if expiring_today + expiring_oneday + expiring_threedays != 0:
                    cus_send_message(id, reply)



            ##### send purchase limit message #####
            #trying 6h intervals (roughly 12am, 6am, 12pm, 6pm)
            if (sg.hour == 0 and cansend(db_reminders_result, 0)) or (sg.hour == 6 and cansend(db_reminders_result, 6)) or (sg.hour == 12 and cansend(db_reminders_result, 12)) or (sg.hour == 18 and cansend(db_reminders_result, 18)):
                servings_div_by_days_left = 0
                data = [id]
                cur = conn.cursor()
                food_query = "SELECT * fROM Food WHERE userID = %s"
                cur.execute(food_query, data)
                result = cur.fetchall()

                for i in result:
                    expiry_date = dt.datetime.strptime(str(i[3]), "%Y-%m-%d").date()
                    days_left = (expiry_date - today).days
                    num_servings = int(i[2])

                    #if the food expires today, then change it to 1 (1 day left to eat)
                    if days_left == 0:
                        days_left = 1
                    servings_div_by_days_left += num_servings / days_left

                cur = conn.cursor()
                hh_member_query = "SELECT household FROM users WHERE userID = %s"
                cur.execute(hh_member_query, data)
                num_hh_members_result = cur.fetchall()

                cur = conn.cursor()
                user_serving_lim_query = "SELECT servingLimit FROM users WHERE userID = %s"
                cur.execute(user_serving_lim_query, data)
                user_serving_lim_result = cur.fetchall()

                if servings_div_by_days_left / int(num_hh_members_result[0][0]) > int(user_serving_lim_result[0][0]):
                    cus_send_message(id, "Oops! It seems that you might have bought too much food to be consumed by your household before they expire! Do think twice before buying more food!")



            ##### update weekly consumption #####
            data = [id]

            #getting today's date
            sg = datetime.now(tz)
            today = sg.date()

            cur = conn.cursor()
            reset_date_query = "SELECT startDate FROM users WHERE userID = %s"
            cur.execute(reset_date_query, data)
            result = cur.fetchall()
            stored_date = result[0][0]
            
            if (today - stored_date).days % 7 == 0 and (today - stored_date).days != 0: #7 days interval since it is a weekly update and not == start date
                cur = conn.cursor()
                weekly_servings_consumed_query = "SELECT weeklyServings FROM users WHERE userID = %s"
                cur.execute(weekly_servings_consumed_query, data)
                weekly_servings_consumed_result = cur.fetchall()
                weekly_servings_consumed = int(weekly_servings_consumed_result[0][0])

                cur = conn.cursor()
                hh_member_query = "SELECT household FROM users WHERE userID = %s"
                cur.execute(hh_member_query, data)
                num_hh_members_result = cur.fetchall()
                num_hh_members = int(num_hh_members_result[0][0])

                user_limit = weekly_servings_consumed / num_hh_members / 7
                rounded_value = math.ceil(user_limit)
                
                #update new limit for this user
                if rounded_value > 0:
                    cur = conn.cursor()
                    cur.execute(f"UPDATE users SET servingLimit = {rounded_value} WHERE userID = {id};")
                    conn.commit()

                #make serving count to be back to 0
                cur = conn.cursor()
                cur.execute(f"UPDATE users SET weeklyServings = 0 WHERE userID = {id};")
                conn.commit()
       
       
       
            ##### checking for expired food #####
            #daily at 12am
            if sg.hour == 0 and cansend(db_reminders_result, 0):
                curr_id = [id]

                cur = conn.cursor()
                query = "SELECT foodID, foodName, servings, expiryDate FROM food WHERE userID = %s"
                cur.execute(query, curr_id)
                cursor = cur.fetchall()

                for row in cursor:
                    food_id = row[0]
                    food_name = row[1]
                    servings = row[2]
                    expiry_date = row[3]
                    if (expiry_date - today).days < 0: #food expired
                        expiry_date = expiry_date.strftime('%d/%m/%Y')
                        points_to_deduct = servings

                        #deduct points
                        cur = conn.cursor()
                        cur.execute(f"SELECT points FROM users WHERE userID = {id}")
                        result = cur.fetchall()
                        updated_points = int(result[0][0]) - points_to_deduct

                        if updated_points < 0: #if points go negative
                            points_to_deduct = int(result[0][0])
                            updated_points = 0

                        cur = conn.cursor()
                        cur.execute(f"UPDATE users SET points = {updated_points} WHERE userID = {id};")
                        conn.commit()

                        if points_to_deduct == 1:
                            cus_send_message(id, f"Oh no! It seems like you forgot to consume {servings} serving(s) of {food_name} which expired on {expiry_date}. It has been removed from your food stock and {points_to_deduct} point was deducted.")
                        else:
                            cus_send_message(id, f"Oh no! It seems like you forgot to consume {servings} serving(s) of {food_name} which expired on {expiry_date}. It has been removed from your food stock and {points_to_deduct} points were deducted.")
                        cur.execute(f"DELETE FROM food WHERE foodID = {food_id}")
                        conn.commit()
                        
                        
        ##UPDATE REMINDERS TABLE TO SET CURRENT HOUR VALUE TO 1
        if sg.hour == 0:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET zero = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 3:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET three = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 6:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET six = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 9:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET nine = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 12:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET twelve = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 15:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET fifteen = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 18:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET eighteen = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
        elif sg.hour == 21:
            cur = conn.cursor()
            values = (1, today)
            query = "UPDATE reminders SET twentyone = %s WHERE date = %s;"
            cur.execute(query, values)
            conn.commit()
            
        sleep(600)#every 10 min

worker = threading.Thread(target=threading_func, args=())
