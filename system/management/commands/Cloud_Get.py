from django.core.management.base import BaseCommand, CommandError
import threading
from cloud.models import Host, Cloud_Host
from cloud.utils import vSphereConfig

class Command(BaseCommand):
    def handle(self, *args, **options):
        cloud_get()
        # timer = threading.Timer(0, get)
        # timer.start()
        # step = 30
        # for x in range(int(60 / step) - 1):
        #     timer = threading.Timer(step, get)
        #     timer.start()

def get():
    timer = threading.Timer(30, cloud_get)
    timer.start()

# Cloud GET
def cloud_get():
    hosts = Host.objects.all()
    if hosts:
        for host in hosts:
            cloudconfig = vSphereConfig.vsphereget(host.ip, host.username, host.password, host.port)
            cloudconfig.vsphere_get_vm_info()