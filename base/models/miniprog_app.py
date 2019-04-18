from django.db import models


class MiniprogramAppSecret(models.Model):
    appsecret = models.CharField(max_length=256)
    appid = models.CharField(max_length=256)
