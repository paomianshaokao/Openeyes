from cloud.models import *

class ormconfig(object):
    def deletorm(self):
        Cluster.objects.all().delete()
        Host.objects.all().delete()
        Host_VM.objects.all().delete()
        Cloud_Host.objects.all().delete()
        Cloud_VM.objects.all().delete()