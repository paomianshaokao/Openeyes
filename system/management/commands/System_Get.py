from django.core.management.base import BaseCommand, CommandError
import threading
from system.utils import yusystemconfig

class Command(BaseCommand):
    def handle(self, *args, **options):
        timer = threading.Timer(0, get)
        timer.start()
        # step = 30
        # for x in range(int(60 / step) - 1):
        #     timer = threading.Timer(step, get)
        #     timer.start()

def get():
    timer = threading.Timer(30, system_get)
    timer.start()

# System GET
def system_get():
    sysconfig = yusystemconfig.yusystemconfig()
    sysconfig.system_infor()