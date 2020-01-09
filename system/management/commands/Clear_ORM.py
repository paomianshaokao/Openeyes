from django.core.management.base import BaseCommand, CommandError
import threading
from authen.models import Project
from audits.utils import SystemAudits, SystemLog, OperaLog, CloudAudits
import psutil

class Command(BaseCommand):
    def handle(self, *args, **options):
        timer = threading.Timer(0, clear,args=[1])
        timer.start()
        timer = threading.Timer(0, clearall)
        timer.start()

def clear(time):
    systeminfo = SystemAudits.systemInfoConfig()
    systemlog = SystemLog.systemLogConfig()
    operalog = OperaLog.operaLogConfig()
    cloudinfo = CloudAudits.cloudInfoConfig()

    systeminfo.canvas_check(time)  #   清除超过1个月的SystemCanvas数据
    systemlog.log_check(time)  #   清除超过1个月的SystemLog数据
    operalog.opera_check(time)  #   清除超过1个月的OperaLog数据
    cloudinfo.canvas_check(time)  #   清除超过1个月的CloudCanvas数据

def clearall():
    disk = psutil.virtual_memory().percent
    if disk > 90:
        clear(1)
        project = Project.objects.filter(project='admin').first()
        log = '硬盘使用率超过90%，已自动清除一个月前的日志报表数据'
        systemlogconfig = SystemLog.systemLogConfig()
        systemlogconfig.log_insert_one(project.id, 'localcluster', 'localhost', 'warning', '127.0.0.1', log)
