import json
import logging
from completion.models import BlockCompletion

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from lms.djangoapps.courseware.models import StudentModule
from model_utils.models import TimeStampedModel
from lektorium_main.courses.models import Course, Section, COK, Topic, TeachingMaterial

logger = logging.getLogger(__name__)


class LoggedIn(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), verbose_name="Пользователь", on_delete=models.SET_NULL,
                             null=True)  # TODO: remove after profile_id test
    profile_id = models.CharField("id профиля пользователя в системе Educont", max_length=36, blank=True,
                                  null=True)  # TODO: make required

    class Meta:
        verbose_name = "вход на платформу"
        verbose_name_plural = "записи входа на платформу"

    def __str__(self):
        return f"LoggedIn: {self.user} - {self.created}"


class StudentStatisticsItem(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), verbose_name="Пользователь", on_delete=models.SET_NULL,
                             null=True)  # TODO: remove after profile_id test
    profile_id = models.UUIDField("id профиля пользователя в системе Educont", blank=True,
                                  null=True)  # TODO: make required
    student_module = models.ForeignKey(StudentModule, blank=True, null=True, on_delete=models.SET_NULL)
    module_type = models.CharField("Module type", max_length=32)
    position = models.PositiveSmallIntegerField("Position (Page)", blank=True, null=True)
    score = models.CharField("Score", max_length=255, blank=True, null=True)
    block_id = models.CharField("block_id", max_length=255, blank=True, null=True)
    block_type = models.CharField("block_type", max_length=255, blank=True, null=True)
    course_key = models.CharField("course_key", max_length=255, blank=True, null=True)
    done = models.NullBooleanField("Done")

    def __str__(self):
        return f"StatisticsItem: {self.profile_id} {self.module_type}"

    class Meta:
        verbose_name = 'запись статистики'
        verbose_name_plural = 'записи статистики'

    example = {
        "data": [
            {
                "statisticType": "ENTER_TO_EDUCATION_PLATFORM",
                "externalId": "",
                "status": "",
                "createdAt": "2022-01-25T08:08:55.125Z",
                "profileId": "9d0b9750-5ad9-4311-a0bc-06ab85eddc04"
            },
            {
                "statisticType": "ENTER_TO_STUDY_SUBJECT",
                "externalId": "rus_1_11",
                "status": "true",
                "createdAt": "2022-01-25T08:08:55.125Z",
                "profileId": "9d0b9750-5ad9-4311-a0bc-06ab85eddc04"
            }
        ]
    }


@receiver(post_save, sender=StudentModule)
def save_student_statistics_item(sender, instance, **kwargs):
    user = get_user_model().objects.get(pk=instance.student_id)
    try:
        if user.verified_profile_educont:
            profile_id = user.verified_profile_educont.profile_id
    except:
        profile_id = None  # TODO: for local testing, remove

    state = json.loads(instance.state)
    logger.warning(f'STATE !!!!!!!!!!!!!! {state}')
    score_raw = state.get('score', None)
    done = state.get('done', None)
    position = state.get('position', None)

    # если существует position, понимаем, что юзер зашел на vertical
    if position:
        section = Section.objects.get(externalId=instance.module_state_key.block_id)
        vertical = section.topics.all[position]
        # BlockCompletion.objects.get(block_key=block.scope_ids.usage_id)
        logger.warning(f"!!! VERTICAL {vertical}")

    if score_raw:
        score = score_raw['raw_earned'] / score_raw['raw_possible']
    else:
        score = None

    StudentStatisticsItem.objects.create(
        user=user,
        profile_id=profile_id,
        student_module=instance,
        module_type=instance.module_type,
        block_id=instance.module_state_key.block_id,
        block_type=instance.module_state_key.block_type,
        course_key=instance.module_state_key.course_key,
        position=position,
        score=score,
        done=done,
    )
