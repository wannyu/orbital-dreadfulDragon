"""
send message to all existing users, except those who stop bot
"""
def cus_send_message(id, text):
     try:
        bot.send_message(id, text)
     except Exception as e:
        print(e)

"""
helper function
takes in the query result from reminders table and the current hour in 24h clock
checks if the same message have been sent in the same hour
return a boolean result to indicate if the message can be sent (if it hasnt sent in the same hour)
"""
def cansend(db_reminders_result, hour):
    index = (hour // 3) + 1
    return db_reminders_result[0][index] == 0

"""
helper function
takes in the query result from reminders table, the current hour in 24h clock and user's reminder frequency (int)
checks if the same message have been sent in the same hour and should be sent based on the reminder frequency
return a boolean result to indicate if the message can and should be sent (if it hasnt sent in the same hour and user should recieve it in this hour)
"""
def canandshouldsend(db_reminders_result, hour, rem_freq):
    timings_list = []
    if rem_freq == 1:
        timings_list = [0]
    elif rem_freq == 2:
        timings_list = [0, 12]
    elif rem_freq == 4:
        timings_list = [0, 6, 12, 18]
    elif rem_freq == 8:
        timings_list = [0, 3, 6, 9, 12, 15, 18, 21]
    return cansend(db_reminders_result, hour) and (hour in timings_list)
       
