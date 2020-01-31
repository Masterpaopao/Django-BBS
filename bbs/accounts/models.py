import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ConfirmString(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    code = models.CharField(max_length=256)
    pub_date = models.DateField(auto_now_add=True)


def upload_to(instance,filename):
    now = timezone.now()
    base,ext = os.path.splitext(filename)
    ext = ext.lower()
    return f'users/{now:%Y/%m/%Y%m%d%H%M%S}{ext}'


class UserUpdate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=2,choices=((1,'男'),(2,'女')),default=1)
    country = models.CharField(max_length=20,default='中国')
    picture = models.FileField(blank=True,null=True,upload_to=upload_to)


