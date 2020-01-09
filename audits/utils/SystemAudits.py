from audits.utils import Mongodb
from datetime import datetime
from utils import yutime

class systemInfo(object):
    def __init__(self):
        self.db = Mongodb.mongodb()

    def canvas(self):
        #   table = SystemCanvas
        #   {'cpu': cpu, 'memory': mem, 'disk': disk, 'ctime': ctime}
        SystemCanvas = self.db.SystemCanvas
        return SystemCanvas

class systemInfoConfig(object):
    def canvas_remove(self):
        systeminfo = systemInfo()
        systeminfo.canvas().remove()

    def canvas_insert_one(self, cpu, mem, disk):
        data = {'cpu': cpu, 'memory': mem, 'disk': disk, 'ctime': datetime.now()}

        systeminfo = systemInfo()
        systeminfo.canvas().insert_one(data)

    def canvas_check(self, month):
        tage = yutime.timeage()
        age = tage.monthage(month)

        systeminfo = systemInfo()
        systeminfo.canvas().remove({'ctime': {'$lt': age}})  #   清除超过一定时间的数据

    def canvas_home(self):
        tage = yutime.timeage()
        age = tage.minuteage(10)

        systeminfo = systemInfo()
        systemcanvas = systeminfo.canvas().find({'ctime': {'$gt': age}})
        return list(systemcanvas)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list

