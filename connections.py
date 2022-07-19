#connect to database
result = urlparse("DATABASE URL")
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

conn = psycopg2.connect(
    database = database,
    user = username,
    password = password,
    host = hostname,
    port = port
)

#connect to telebot
bot = telebot.TeleBot("TOKEN", parse_mode=None)
