import logging

from django.db import models

# from completion.models import BlockCompletion

logger = logging.getLogger(__name__)


class EducontStatisticsItem(models.Model):
    '''
    "statisticType": "ENTER_TO_STUDY_SUBJECT",
    "externalId": "rus_1_11",
    "status": "true",
    "createdAt": "2022-01-25T08:08:55.125Z",
    "profileId": "9d0b9750-5ad9-4311-a0bc-06ab85eddc04"
    '''

    TYPES = (('s', 'ENTER_TO_STUDY_SUBJECT'), ('e', 'ENTER_TO_EDUCATION_PLATFORM'))
    statisticType = models.CharField("statisticType", max_length=2, choices=TYPES)
    externalId = models.CharField("externalId", max_length=255, default="")
    status = models.BooleanField("Status", blank=True, null=True)
    profileId = models.UUIDField("id профиля пользователя в системе Educont")
    createdAt = models.DateTimeField(auto_now_add=True)
