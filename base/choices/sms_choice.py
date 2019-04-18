# coding=UTF-8
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from base.util import field_choice


class _SMSChoice(field_choice.FieldChoice2):
    VALIDATION = field_choice.FieldChoiceSelection(0, _("验证短信 - B/C"))
    BOOKKEEPING_C = field_choice.FieldChoiceSelection(1, _("记账短信 - C"))


sms_choice = _SMSChoice()
