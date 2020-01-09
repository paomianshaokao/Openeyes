import datetime

#   一段时间前，如一小时前
class timeage(object):
    def __init__(self):
        self.now = datetime.datetime.now()

    def minuteage(self,m):
        minute = self.now - datetime.timedelta(minutes = 1 * m)
        return minute

    def hourage(self,h):
        hour = self.now - datetime.timedelta(hours = 1 * h)
        return hour

    def dayage(self,d):
        day = self.now - datetime.timedelta(days = 1 * d)
        return day

    def weekage(self,w):
        week = self.now - datetime.timedelta(days = 7 * w)
        return week

    def monthage(self,m):
        month = self.now - datetime.timedelta(days = 31 * m)
        return month

#   这个时段的开始，如今天0点
class timeone(object):
    def __init__(self):
        self.now = datetime.datetime.now()

    def today(self):
        today = datetime.date.today().day
        return today

    def daytime(self, day):
        day = datetime.datetime(self.now.year, self.now.month, day, 0, 0, 0)
        return day

    def hourtime(self, day, hour):
        hour = datetime.datetime(self.now.year, self.now.month, day, hour, 0, 0)
        return hour

    def minutetime(self, day, hour, minute):
        minute = datetime.datetime(self.now.year, self.now.month, day, hour, minute, 0)
        return minute

    def hourone(self):
        firstminute = datetime.datetime(self.now.year, self.now.month, self.now.day, self.now.hour, 0, 0)
        return firstminute

    def dayone(self):
        firsthour = datetime.datetime(self.now.year, self.now.month, self.now.day, 0, 0, 0)
        return firsthour

    def weekone(self):
        week_day = self.now - datetime.timedelta(days=self.now.weekday())
        firstday = datetime.datetime(week_day.year, week_day.month, week_day.day, 0, 0, 0)
        return firstday

    def monthone(self):
        firstday = datetime.datetime(self.now.year, self.now.month, 1, 0, 0, 0)
        return firstday

