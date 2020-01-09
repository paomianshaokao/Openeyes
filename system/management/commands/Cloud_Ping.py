from django.core.management.base import BaseCommand, CommandError
from cloud.models import Host
from tcping import Ping
import threading, re
from audits.utils import HostAlarm

class Command(BaseCommand):
    def handle(self, *args, **options):
        timer = threading.Timer(0, ping)
        timer.start()
        step = 15
        for x in range(int(60/step)-1):
            timer = threading.Timer(step, ping)
            timer.start()

def ping():
    hosts = Host.objects.all()
    for host in hosts:
        timer = threading.Timer(0, cloud_ping, args=[host])
        timer.start()

def cloud_ping(host):
    tcping = Ping(host.ip, host.port, 1)
    tcping.ping(2)
    successed = re.findall(r'(\d+) successed', tcping.result.raw)
    if not '0' in successed:
        Host.objects.filter(id=host.id).update(state='online')
    else:
        alarm = HostAlarm.Alarm()
        alarm.cloud_offalarm(host)
        Host.objects.filter(id=host.id).update(state='offline')
