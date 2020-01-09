from audits.utils import Mongodb
from datetime import datetime
from utils import yutime

class cloudInfo(object):
    def __init__(self):
        self.db = Mongodb.mongodb()

    def canvas(self):
        #   table = CloudCanvas
        #   {'uuid': uuid, 'cpu': cpu, 'memory': mem, 'disk_read': disk_read, 'disk_write': disk_write, 'net_out': net_out, 'net_in': net_in, 'ctime': ctime}
        CloudCanvas = self.db.CloudCanvas
        return CloudCanvas

class cloudInfoConfig(object):
    def canvas_remove(self):
        cloudinfo = cloudInfo()
        cloudinfo.canvas().remove()

    def canvas_insert_one(self, data):
        now = datetime.now()
        data['ctime'] = now    #   添加创建时间

        cloudinfo = cloudInfo()
        cloudinfo.canvas().insert_one(data)

    def canvas_del_uuid(self, uuid):
        cloudinfo = cloudInfo()
        cloudinfo.canvas().remove({'uuid': uuid})  # 清除制定uuid的虚拟机

    def canvas_check(self, month):
        tage = yutime.timeage()
        age = tage.monthage(month)

        cloudinfo = cloudInfo()
        cloudinfo.canvas().remove({'ctime': {'$lt': age}})  #   清除超过一定时间的数据

    def canvas_table(self, vm_id):
        tage = yutime.timeage()
        age = tage.minuteage(10)

        cloudinfo = cloudInfo()
        cloudcanvas = cloudinfo.canvas().find({'vm': vm_id, 'ctime': {'$gt': age}})
        return list(cloudcanvas)   #   默认<class 'pymongo.cursor.Cursor'> 只能迭代一次，真坑，转成list

    def canvas_vm(self, uuid, time='10min'):
        tage = yutime.timeage()
        if time == '3hour':
            age = tage.hourage(3)
        elif time == 'day':
            age = tage.dayage(1)
        else:
            age = tage.minuteage(10)
        cloudinfo = cloudInfo()
        cloudcanvas = cloudinfo.canvas().find({'uuid': uuid, 'ctime': {'$gt': age}})

        cpucanvas = []
        memorycanvas = []
        diskcanvas_read = []
        diskcanvas_write = []
        netcanvas_out = []
        netcanvas_in = []
        for canvas in cloudcanvas:
            cpucanvas.append({'y': canvas['cpu'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
            memorycanvas.append({'y': canvas['memory'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
            if 'disk_read' in canvas:
                diskcanvas_read.append({'y': canvas['disk_read'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
                diskcanvas_write.append({'y': canvas['disk_write'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
            if 'net_out' in canvas:
                netcanvas_out.append({'y': canvas['net_out'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
                netcanvas_in.append({'y': canvas['net_in'], 'x': canvas['ctime'].strftime( '%Y-%m-%d %H:%M' ) })
        cloudcanvas = {'cpucanvas': cpucanvas, 'memorycanvas': memorycanvas,
                       'diskcanvas_read': diskcanvas_read, 'diskcanvas_write': diskcanvas_write,
                       'netcanvas_out': diskcanvas_read, 'netcanvas_in': diskcanvas_write}
        return cloudcanvas