from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from lektorium_main.core.models import BaseModel
from lektorium_main.courses.models import *


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     logging.warning("!!!!!!!!!!!!!!!!!!!!!!!!!!!!! @@@@@@@@@@@@@@@@@@")
#     # logging.warning(dir(instance))
#     # social = instance.social_auth
#     # logging.warning(social)
#     # profile = instance.profile
#     # logging.warning(profile)
#     # if created:
#     #     Profile.objects.create(user=instance, isActive=instance.profile.isActive)
#
#
# post_save.connect(create_user_profile, sender=User)
#
#
# # @receiver(post_save, sender=User)
# # def save_user_profile(sender, instance, **kwargs):
# #     instance.profile.save()
#
#
# # post_save.connect(save_user_profile, sender=User)


class Profile(PolymorphicModel, BaseModel):
    class StatusConfirmEmail(models.TextChoices):
        CONFIRM = 'CONFIRM',
        NOT_CONFIRM = 'NOT_CONFIRM',
        NEW_PROFILE = 'NEW_PROFILE',
        OLD_PROFILE = 'OLD_PROFILE',

    class Role(models.TextChoices):
        TEACHER = 'TEACHER',
        STUDENT = 'STUDENT',

    # Relationships
    educationalInstitutions = models.ForeignKey("lektorium_main.EducationalInstitutions",
                                                verbose_name='Данные об образовательных учреждениях пользователя',
                                                on_delete=models.SET_NULL,
                                                null=True, blank=True)

    # Fields
    role = models.CharField('Роль пользователя в Системе', max_length=15, choices=Role.choices)

    isActive = models.BooleanField('Флаг функционирующего аккаунта')
    login = models.CharField('Логин', max_length=50)
    middleName = models.CharField('Отчество', max_length=50)
    name = models.CharField('Имя', max_length=50)
    fullName = models.CharField(max_length=200)
    email = models.EmailField('Почта', null=True, blank=True)

    surname = models.CharField('Фамилия', max_length=50, null=True, blank=True)
    statusConfirmEmail = models.CharField('Статус подтверждения почты пользователя в Системе', max_length=15,
                                          choices=StatusConfirmEmail.choices, null=True, blank=True)
    birthdate = models.CharField(max_length=50, null=True, blank=True)
    birthyear = models.CharField(max_length=50, null=True, blank=True)

    user = models.OneToOneField(get_user_model(), unique=True, db_index=True, related_name='verified_profile',
                                verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("lektorium_main_Profile_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_Profile_update", args=(self.pk,))

    def update(self,*args, **kwargs):
            for name,values in kwargs.items():
                try:
                    setattr(self,name,values)
                except KeyError:
                    pass
            self.save()


class EducationalInstitution(BaseModel):
    """
    Данные об образовательном учреждении
    """

    class TypeEducationalInstitution(models.TextChoices):
        SCHOOL = 'SCHOOL',
        COLLEGE = 'COLLEGE'

    # Fields
    shortName = models.CharField('Краткое наименование образовательной организации', max_length=100)
    fullName = models.TextField('Полное наименование образовательной организации')
    inn = models.CharField('ИНН образовательной организации', max_length=12,
                           validators=[RegexValidator('^[0-9]{10}$', 'Invalid INN')], )
    kpp = models.CharField('КПП образовательной организации', max_length=9,
                           validators=[RegexValidator('^[0-9]{9}$', 'Invalid KPP')], )
    postIndex = models.CharField('Индекс образовательной организации', max_length=6,
                                 validators=[RegexValidator('^[0-9]{6}$', 'Invalid postal code')],
                                 )
    street = models.CharField('Улица образовательной организации', max_length=30)
    address = models.TextField('Полный адрес образовательной организации')
    locality = models.CharField('Город образовательной организации', max_length=100)
    region = models.CharField('Регион образовательной организации', max_length=100)
    municipalArea = models.CharField('Муниципальный район образовательной организации', max_length=50)
    isTest = models.BooleanField('Флаг "Тестовое учрждение"',
                                 help_text='Если значение "true", то для пользователя, который привязан к этому \
                                 учреждению не будет учитываться статистика',
                                 default=False)
    typeEducationalInstitution = models.CharField('Тип образовательного учреждения', max_length=8,
                                                  choices=TypeEducationalInstitution.choices)

    @property
    def schoolName(self):
        """
        Краткое наименование+полный адрес образовательной организации
        """
        return f"{self.address} {self.shortName}"

    class Meta:
        verbose_name = 'данные об образовательном учреждении'
        verbose_name_plural = 'данные об образовательных учреждениях'

    def __str__(self):
        return f'{self.get_typeEducationalInstitution_display()} {self.schoolName}'

    def get_absolute_url(self):
        return reverse("lektorium_main_EducationalInstitution_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_EducationalInstitution_update", args=(self.pk,))

    @classmethod
    def update(cls, user):
        profile = cls(user=user)
        return profile

class EducationalInstitutions(BaseModel):
    # Relationships
    educationalInstitution = models.ForeignKey("lektorium_main.EducationalInstitution", on_delete=models.CASCADE, blank=True, null=True)

    # Fields
    approvedStatus = models.CharField(max_length=50)
    isActual = models.BooleanField(null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("lektorium_main_EducationalInstitutions_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_EducationalInstitutions_update", args=(self.pk,))


class StudentProfile(Profile):
    studentGradeEducationalInstitutions = models.ForeignKey("lektorium_main.StudentTagEducationalInstitutions",
                                                            on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("lektorium_main_StudentProfile_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_StudentProfile_update", args=(self.pk,))


class TeacherProfile(Profile):
    teacherTagEducationalInstitutions = models.ForeignKey("lektorium_main.TeacherTagEducationalInstitutions",
                                                          on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("lektorium_main_TeacherProfile_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_TeacherProfile_update", args=(self.pk,))


class TeacherTagEducationalInstitutions(BaseModel):
    tagId = models.CharField(max_length=100, blank=True, null=True)
    gradeEducationalInstitutions = models.ForeignKey("lektorium_main.GradeEducationalInstitutions",
                                                     on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class StudentTagEducationalInstitutions(BaseModel):
    tagId = models.CharField(max_length=100, blank=True, null=True)
    gradeEducationalInstitutions = models.ForeignKey("lektorium_main.GradeEducationalInstitutions",
                                                     on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class GradeEducationalInstitutions(BaseModel):
    educationalInstitutionId = models.UUIDField(editable=False, unique=True)
    letter = models.CharField(max_length=10, blank=True, null=True)
    grade = models.ForeignKey("lektorium_main.Grade", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class Grade(BaseModel):
    class TypeEducationalInstitution(models.TextChoices):
        SCHOOL = 'SCHOOL',
        COLLEGE = 'COLLEGE'

    value = models.PositiveSmallIntegerField(blank=True, null=True)
    typeEducationalInstitution = models.CharField(max_length=15, choices=TypeEducationalInstitution.choices)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)
