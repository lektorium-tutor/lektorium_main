import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from lms.djangoapps.courseware.models import StudentModule
from model_utils.models import TimeStampedModel

from lektorium_main.profile.models import Profile

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


# @receiver(user_logged_in)
# def collect_logged_in(sender, request, user, **kwargs):
#     if settings.FEATURES.get('ENABLE_LEKTORIUM_MAIN', False):
#         try:
            # if user.verified_profile_educont.role == Profile.Role.STUDENT:
            #     profile_id = user.verified_profile_educont.profile_id  # You may need to define the profile role
            # else:
            #     profile_id = None
            # LoggedIn.objects.create(
            #     user=user,
            #     profile_id=profile_id
            # )
#         except Exception as err:
#             logger.error(f"Unexpected {err=}, {type(err)=}, , profile_id: {profile_id}")


@receiver(post_save, sender=StudentModule)
def save_student_statistics_item(sender, instance, **kwargs):
    user = get_user_model().objects.get(pk=instance.student_id)
    if user.verified_profile_educont:
        profile_id = user.verified_profile_educont.profile_id
    else:
        profile_id = None  # TODO: for local testing, remove
    state = json.loads(instance.state)
    logger.warning(f'STATE !!!!!!!!!!!!!! {state}')
    score_raw = state.get('score', None)
    done = state.get('done', None)

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
        position=state.get('position', None),
        score=score,
        done=done,
    )
