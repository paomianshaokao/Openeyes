from django.db import models

# Create your models here.
class System(models.Model):
    system = models.CharField(max_length=32)
    hostname = models.CharField(max_length=32)
    theme = models.CharField(max_length=32,default='skin-0')
    # alert = models.TextField(blank=True)
    # face_distance = models.CharField(max_length=16,default=0.4)

    # sn = models.CharField(max_length=32, db_index=True)
    # networkstate = models.CharField(max_length=16, default='未授权')
    # serverstate = models.CharField(max_length=16, default='未授权')
    # pcstate = models.CharField(max_length=16, default='未授权')
    # cloudstate = models.CharField(max_length=16, default='未授权')
    # dumbstate = models.CharField(max_length=16, default='未授权')
    # networknumber = models.CharField(max_length=32, default=0)
    # servernumber = models.CharField(max_length=32, default=0)
    # pcnumber = models.CharField(max_length=32, default=0)
    # cloudnumber = models.CharField(max_length=32, default=0)
    # dumbnumber = models.CharField(max_length=32, default=0)

class SystemEmail(models.Model):
    server = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    system = models.ForeignKey("System", on_delete=models.CASCADE)
