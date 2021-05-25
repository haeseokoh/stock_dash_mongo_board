import datetime
from dateutil.relativedelta import relativedelta

def year_weeks(date):
    n = date
    y = n.isocalendar()[0]
    w = n.isocalendar()[1]
    return y, w

def weeks_start_date(y, w):
    # 해당년도의 첫째날 + 첫째날의 요일을 구해 해당 주차의 첫날을 구함 + 주차를 더해줌 이때 1주차 부터 시작하므로 -1을 함
    return (datetime.datetime(y, 1, 1) + relativedelta(days=-datetime.datetime(y, 1, 1).isoweekday()) + relativedelta(weeks=w - 1)).date()


def weeks_from_today(howmuch):
    weeks_list = []
    for x in range(0, howmuch):
        n = datetime.datetime.now()
        # wday = n.weekday()
        n += relativedelta(weeks=-x)
        weeks_list.append(year_weeks(n))
    
    return weeks_list


def weeks_from_today_forDB(start_weeks, howmuch):
    weeks_list = []
    start_weeks_split = start_weeks.split(' ')
    y = int(start_weeks_split[0])
    w = int(start_weeks_split[1][1:])
    duration = int(howmuch[:-1])
    for x in range(duration+1, 1):
        n = weeks_start_date(y,w)
        # wday = n.weekday()
        n += relativedelta(weeks=x+1)
        weeks_list.append(year_weeks(n))
        
    return weeks_list


def period_from_weeks_forDB(start_weeks):
    weeks_list = []
    start_weeks_split = start_weeks.split(' ')
    y = int(start_weeks_split[0])
    w = int(start_weeks_split[1][1:])
    
    # add 'recored_date':{'$gte':startofperiod,'$lt':endofperiod}}
    # bson.errors.InvalidDocument: cannot encode object: datetime.date(2020, 9, 6), of type: <class 'datetime.date'>
    # need add time attr
    startofperiod = weeks_start_date(y, w) + relativedelta(hour=0)
    endofperiod = startofperiod + relativedelta(days = 6, hour=0)
    return startofperiod, endofperiod


def weeks_from_today_forDB2(start_weeks, howmuch):
    weeks_list = []
    start_weeks_split = start_weeks.split(' ')
    y = int(start_weeks_split[0])
    w = int(start_weeks_split[1][1:])
    duration = int(howmuch[:-1])
    # add 'recored_date':{'$gte':startofperiod,'$lt':endofperiod}}
    # bson.errors.InvalidDocument: cannot encode object: datetime.date(2020, 9, 6), of type: <class 'datetime.date'>
    # need add time attr
    
    # startofperiod = weeks_start_date(y, w) + relativedelta(weeks=duration + 1, hour=0)
    # endofperiod = weeks_start_date(y, w) + relativedelta(weeks=0 + 1, days = -1, hour=0)

    for x in range(duration + 1, 1):
        n = weeks_start_date(y, w)
        # wday = n.weekday()
        n += relativedelta(weeks=x + 1)
        y_w = year_weeks(n)
        startofperiod = weeks_start_date(y_w[0], y_w[1]) + relativedelta(hour=0)
        endofperiod = startofperiod + relativedelta(days = 6, hour=0)
        weeks_list.append((y_w, startofperiod, endofperiod))
    
    return weeks_list

if __name__ == "__main__":
    for x in weeks_from_today(4):
        print(x[0],x[1], weeks_start_date(x[0],x[1]))

    print('-----------------------')
    
    for x in weeks_from_today_forDB('2020 W36', '-52W'):
        print(x[0],x[1], weeks_start_date(x[0],x[1]))

    print('-----------------------')

    for x, y, z in weeks_from_today_forDB2('2020 W36', '-52W'):
        print(x, y, z)
        
    print(period_from_weeks_forDB('2020 W36'))


    