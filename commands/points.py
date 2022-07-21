"""
/points command in bot
query how many points a user has
"""
@bot.message_handler(commands=['points'])
def points(message):
    cur = conn.cursor()
    cur.execute(f"SELECT points FROM users WHERE userID = {message.from_user.id}")
    result = cur.fetchall()               
    bot.send_message(message.from_user.id, f"You have accumulated {result[0][0]} points.")    
