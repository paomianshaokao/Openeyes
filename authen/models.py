from django.db import models

# Create your models here.
class Project(models.Model):
    project = models.CharField(max_length=32)
    ctime = models.DateTimeField(auto_now_add=True)

class UserGroup(models.Model):
    caption = models.CharField(max_length=32)
    ctime = models.DateTimeField(auto_now_add=True)

class UserInfo(models.Model):
    username = models.CharField(max_length=32,db_index=True)
    password = models.CharField(max_length=32)
    email = models.CharField(max_length=32,db_index=True)
    # alarm = models.CharField(max_length=16,default='已关闭')
    # face = models.CharField(max_length=16,default='未录入')
    state = models.CharField(max_length=16,default='Active')
    ctime = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey("UserGroup",on_delete=models.CASCADE)
    project = models.ForeignKey("Project",on_delete=models.CASCADE)
