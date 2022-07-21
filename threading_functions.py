def cus_send_message(id, text):
     try:
        bot.send_message(id, text)
     except Exception as e:
        print(e)

def cansend(db_reminders_result, hour):
    # determine if message should be sent, returns boolean
    index = (hour // 3) + 1
    return db_reminders_result[0][index] == 0

def canandshouldsend(db_reminders_result, hour, rem_freq):
    # determine if message should be sent based on user's personal reminder freq, returns boolean
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
       
