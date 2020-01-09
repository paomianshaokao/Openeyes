from django.db import models

# Create your models here.
class Alert(models.Model):
    alert = models.TextField(blank=True)
    user = models.ForeignKey("authen.UserInfo", on_delete=models.CASCADE)
