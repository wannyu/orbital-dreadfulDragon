"""
function to check if an input date is valid
""" 
def validDate(date):  
    try:
        day, month, year = date.split('/')
    except ValueError:
        isValidDate = False
    else:
        isValidDate = True
        try:
            dt.datetime(int(year), int(month), int(day))
        except ValueError:
            isValidDate = False

        if len(year) != 4:
            isValidDate = False
    return isValidDate


"""
since Heroku is hosted based on UTC timezone, in order for all messages to be processed at the correct timings,
timezone needs to be changed to singapore time
""" 
import pytz
tz = pytz.timezone('Singapore')

"""
function to get today's date
""" 
def get_today():
    sg = datetime.now(tz)
    return sg.date()
