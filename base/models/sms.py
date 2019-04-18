from django.db import models
from base.choices.sms_choice import sms_choice


class AliSmsAPIMasterKey(models.Model):
    app_key = models.CharField(max_length=255)
    app_secret = models.CharField(max_length=255)
    template_code = models.CharField(max_length=255)
    sign_name = models.CharField(max_length=255)
    in_use = models.BooleanField(default=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    usage = models.IntegerField(choices=sms_choice.choice)

    def __unicode__(self):
        return sms_choice.get_verbose_name(self.usage)
