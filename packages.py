#for database connection
import psycopg2
from urllib.parse import urlparse

#connect to our bot
import telebot

#packages needed
from telebot import types

import random
import threading

import datetime as dt
from datetime import date
from datetime import datetime
from time import sleep
import pytz
tz = pytz.timezone('Singapore') #change timezone

import math
