from pymongo import DESCENDING
from audits.utils import Mongodb
from datetime import datetime
from utils import yutime

class operaLog(object):
    def __init__(self):
        self.db = Mongodb.mongodb()

    def opera(self):
        #   table = SystemLog
        #   {'project': project.id, 'group': group, 'username': username, 'level': level, 'action': action, 'ip': ip, 'log': log, 'ctime': ctime}
        #   level : normal、danger、warning
        #   action : login、get、config
        SystemLog = self.db["OperaLog"]
        return SystemLog

class operaLogConfig(object):
    def opera_remove(self):
        operainfo = operaLog()
        operainfo.opera().remove()

    def log_insert_one(self, project, group, username, level, action, ip, log):
        data = {'project': project, 'group': group, 'username': username, 'level': level,
                'action': action, 'ip': ip, 'log': log, 'ctime': datetime.now()}

        operainfo = operaLog()
        operainfo.opera().insert_one(data)

    def opera_check(self, month):
        tage = yutime.timeage()
        age = tage.monthage(month)

        operainfo = operaLog()
        operainfo.opera().remove({'ctime': {'$lt': age}})  #   清除超过一定时间的数据

    def opera_home_all(self):
        tage = yutime.timeone()
        age = tage.weekone()

        operalog = operaLog()
        login_number = operalog.opera().find({'action':'login', 'ctime': {'$gt': age}}).count()
        return login_number

    def opera_home_project(self, project):
        tage = yutime.timeone()
        age = tage.weekone()

        operalog = operaLog()
        login_number = operalog.opera().find({'project': project, 'action':'login', 'ctime': {'$gt': age}}).count()
        return login_number

    def opera_home_login_all(self):
        operalog = operaLog()
        login = operalog.opera().find({'action': 'login'}).sort('ctime', DESCENDING).limit(3)
        return list(login)

    def opera_home_login_project(self, project):
        operalog = operaLog()
        login = operalog.opera().find({'project': project, 'action':'login'}).sort('ctime', DESCENDING).limit(3)
        return list(login)

    def opera_all(self):
        operalog = operaLog()
        log = operalog.opera().find()
        return list(log)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list

    def opera_project(self, project):
        operalog = operaLog()
        log = operalog.opera().find({ "project": project })
        return list(log)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list