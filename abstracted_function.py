# checking for a valid input date
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
