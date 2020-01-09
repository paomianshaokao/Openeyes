from system.models import System
import time, os, psutil

from audits.utils import SystemAudits

class yusystemconfig(object):
    def editsystem(self, host):
        System.objects.filter(system='openeyes').update(hostname=host)

    def systemreload(self):
        time.sleep(2)
        os.system('shutdown -r now')

    def systemshutdown(self):
        time.sleep(2)
        os.system('shutdown -h now')

    def systemtheme(self, theme):
        System.objects.filter(system='openeyes').update(theme=theme)

    def system_infor(self):
        cpu = str(psutil.cpu_percent(0))
        mem = str(psutil.virtual_memory().percent)
        disk = str(psutil.virtual_memory().percent)
        systeminfoconfig = SystemAudits.systemInfoConfig()
        systeminfoconfig.canvas_insert_one(cpu, mem, disk)