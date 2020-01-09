from django.db import models

# Create your models here.
class Cluster(models.Model):
    cluster = models.CharField(max_length=32)
    host_number = models.CharField(max_length=16, default='0')
    ctime = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey("authen.Project",on_delete=models.CASCADE)

class Host(models.Model):
    host = models.CharField(max_length=32,db_index=True)
    ip = models.CharField(max_length=16,db_index=True)
    port = models.CharField(max_length=16)
    username = models.CharField(max_length=32, blank=True)
    password = models.CharField(max_length=32, blank=True)
    system = models.CharField(max_length=32)
    state = models.CharField(max_length=16, blank=True)
    ctime = models.DateTimeField(auto_now_add=True)
    cluster = models.ForeignKey("Cluster",on_delete=models.CASCADE)

class Host_VM(models.Model):
    uuid = models.CharField(max_length=64,db_index=True)
    ctime = models.DateTimeField(auto_now_add=True)
    host = models.ForeignKey("Host",on_delete=models.CASCADE)

class Cloud_Host(models.Model):
    host = models.CharField(max_length=32,db_index=True)
    username = models.CharField(max_length=32, blank=True)
    password = models.CharField(max_length=32, blank=True)
    ctime = models.DateTimeField(auto_now_add=True)
    cloud_host = models.ForeignKey("Host",on_delete=models.CASCADE)
    cluster = models.ForeignKey("Cluster",on_delete=models.CASCADE)

class Cloud_VM(models.Model):
    uuid = models.CharField(max_length=64,db_index=True)
    ctime = models.DateTimeField(auto_now_add=True)
    cloud_host = models.ForeignKey("Cloud_Host",on_delete=models.CASCADE)

# class Cloud_Alarm(models.Model):
#     offalarm = models.CharField(max_length=16, default='active')
#     emailoffalarm = models.CharField(max_length=16, default='inactive')
#     alarm_host = models.ForeignKey("Host", on_delete=models.CASCADE)