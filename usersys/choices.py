# coding=UTF-8
from __future__ import unicode_literals
from base.util import field_choice


class _UserRoleChoice(field_choice.FieldChoice2):
    CLIENT = field_choice.FieldChoiceSelection(0, "C端客户", alias='client')
    RECYCLING_STAFF = field_choice.FieldChoiceSelection(1, "B端业务员", alias='recycling_staff')
    RECOMMENDER = field_choice.FieldChoiceSelection(2, "市场推广", alias='recommender')
    QC_ASSISTANT = field_choice.FieldChoiceSelection(3, "质检员", alias='qc_assistant')


user_role_choice = _UserRoleChoice()
