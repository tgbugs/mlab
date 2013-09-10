from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

###---------------------------------------------------------------
###  Datetime and timedelta functions to be reused for consistency
###---------------------------------------------------------------

def frmtDT(dateTime,formatString='%Y/%m/%d %H:%M:%S',localtime=False):
    if localtime:
        return 'the dt run through some function that converts UTC to whatever the current local timezone is polled from the system' #FIXME
    return datetime.strftime(dateTime,formatString)

def timeDeltaIO(tdORfloat):
    try:
        return tdORfloat.total_seconds()
    except:
        try:
            return timedelta(seconds=tdORfloat)
        except TypeError:
            raise TypeError('That wasn\'t a float OR a timedelta, what the hell are you feeding the poor thing!?')


