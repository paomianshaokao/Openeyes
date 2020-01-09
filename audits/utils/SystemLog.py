from audits.utils import Mongodb
from datetime import datetime
from utils import yutime

class systemLog(object):
    def __init__(self):
        self.db = Mongodb.mongodb()

    def log(self):
        #   table = SystemLog
        #   {'project': project.id, 'cluster': cluster, 'host': host, 'level': level, 'ip': ip, 'log': log, 'ctime': ctime}
        #   level : normal、danger、warning
        SystemLog = self.db.SystemLog
        return SystemLog

class systemLogConfig(object):
    def log_remove(self):
        systeminfo = systemLog()
        systeminfo.log().remove()

    def log_insert_one(self, project, cluster, host, level, ip, log):
        data = {'project': project, 'cluster': cluster, 'host': host, 'level': level,
                'ip': ip, 'log': log, 'ctime': datetime.now()}

        systeminfo = systemLog()
        systeminfo.log().insert_one(data)

    def log_check(self, month):
        tage = yutime.timeage()
        age = tage.monthage(month)

        systemlog = systemLog()
        systemlog.log().remove({'ctime': {'$lt': age}})  #   清除超过一定时间的数据

    def log_home_all(self):
        tage = yutime.timeone()
        age = tage.weekone()

        systemlog = systemLog()
        normal_number = systemlog.log().find({'level':'normal', 'ctime': {'$gt': age}}).count()
        warning_number = systemlog.log().find({'level':'warning', 'ctime': {'$gt': age}}).count()
        danger_number = systemlog.log().find({'level':'danger', 'ctime': {'$gt': age}}).count()
        log = {'normal_number': normal_number, 'warning_number': warning_number, 'danger_number': danger_number}
        return log

    def log_home_project(self, project):
        tage = yutime.timeone()
        age = tage.weekone()

        systemlog = systemLog()
        normal_number = systemlog.log().find({'project': project, 'level':'normal', 'ctime': {'$gt': age}}).count()
        warning_number = systemlog.log().find({'project': project, 'level':'warning', 'ctime': {'$gt': age}}).count()
        danger_number = systemlog.log().find({'project': project, 'level':'danger', 'ctime': {'$gt': age}}).count()
        log = {'normal_number': normal_number, 'warning_number': warning_number, 'danger_number': danger_number}
        return log

    def log_all(self):
        systemlog = systemLog()
        log = systemlog.log().find()
        return list(log)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list

    def log_project(self, project):
        systemlog = systemLog()
        log = systemlog.log().find({ "project": project })
        return list(log)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list