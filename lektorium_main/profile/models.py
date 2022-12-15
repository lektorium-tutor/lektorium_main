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
from django.contrib.auth.signals import user_logged_in


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
    profile_id = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        pass

    @property
    def is_empty_edu_inst(self):
        if self.educationalInstitutions.educationalInstitution:
            return True
        else: 
            return False

    @property
    def is_actual(self):
        return self.educationalInstitutions.isActual
    
    @property
    def is_approved(self):
        if self.educationalInstitutions.approvedStatus == 'APPROVED':
            return True
        else: 
            return False
    
    @property
    def is_not_approved(self):
        if self.educationalInstitutions.approvedStatus == 'NOT_APPROVED':
            return True
        else: 
            return False

    @property
    def is_graduate_approved(self):
        if self.educationalInstitutions.approvedStatus == 'GRADUATE':
            return True
        else: 
            return False

    @property
    def is_none_approved(self):
        if self.educationalInstitutions.approvedStatus == None or self.educationalInstitutions.approvedStatus == '':
            return True
        else: 
            return False

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

    @classmethod
    def get_polymorph_profile(cls, user):
        if cls.objects.filter(models.Q(StudentProfile___user = user) | models.Q(TeacherProfile___user = user)  ).exists():
            return cls.objects.filter(models.Q(StudentProfile___user = user) | models.Q(TeacherProfile___user = user)  ).first()
    
    @classmethod
    def is_profile_exists(cls, user):
        email = user.email
        if cls.objects.filter(models.Q(StudentProfile___user = user) | models.Q(TeacherProfile___user = user)  ).exists():
            return True
        elif cls.objects.filter(models.Q(StudentProfile___email = email) | models.Q(TeacherProfile___email = email)  ).exists():
            return True
        else:
            return False

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
    schoolName = models.TextField('Наименование школы', blank=True, null=True)
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
    def schoolNameCustom(self):
        """
        Краткое наименование+полный адрес образовательной организации
        """
        return f"{self.address} {self.shortName}"

    class Meta:
        verbose_name = 'данные об образовательном учреждении'
        verbose_name_plural = 'данные об образовательных учреждениях'
    
    def __str__(self):
        return str(self.pk)

    # def __str__(self):
    #     return f'{self.get_typeEducationalInstitution_display()} {self.schoolNameCustom}'

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
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'

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
        verbose_name = 'Профиль преподавателя'
        verbose_name_plural = 'Профили преподавателей'

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

class StatusMessage(BaseModel):
    empty_message = 'Ошибка: пустое сообщение, обратитесь к Администратору образовательной платформы.'

    class StatusType(models.TextChoices):
        ACTIVE_STATUS = 'ACTIVE_STATUS',
        EMPTY_EDU_INST = 'EMPTY_EDU_INST',
        APPROVED_STATUS = 'APPROVED_STATUS',
        ACTUAL_STATUS = 'ACTUAL_STATUS',
        NOT_APPROVED_STATUS = 'NOT_APPROVED_STATUS',
        NONE_APPROVED_STATUS = 'NONE_APPROVED_STATUS'
        GRADUATE_APPROVED_STATUS = 'GRADUATE_APPROVED_STATUS'
    
    status_type = models.CharField('Тип сообщения',help_text='ВНИМАНИЕ! Типы сообщений униакальные для каждой записи', max_length=50, choices=StatusType.choices, unique=True)
    message = models.CharField('Сообщение', max_length=400, blank=True, null=True)

    class Meta:
        verbose_name = 'Сообщение для пользователя'
        verbose_name_plural = 'Сообщения для пользователей'

    def __str__(self):
        return str(self.pk)

    @classmethod
    def get_message(cls, status_type):
        try:
            return cls.objects.get(status_type=status_type).message
        except:
            return cls.empty_message

def is_verefication_educont_profile(user):
    if user.is_superuser or user.is_staff:
        return True
    
    profile = Profile.get_polymorph_profile(user)
    if profile.isActive or profile.is_approved or profile.is_actual or profile.is_empty_edu_inst:
        return True
    else:
        return False

def get_message_status_educont_profile(user):
    profile = Profile.get_polymorph_profile(user)
    if not profile.isActive:
        return StatusMessage.get_message(StatusMessage.StatusType.ACTIVE_STATUS)
    elif not profile.is_actual:
        return StatusMessage.get_message(StatusMessage.StatusType.ACTUAL_STATUS)
    elif not profile.is_empty_edu_inst:
        return StatusMessage.get_message(StatusMessage.StatusType.EMPTY_EDU_INST)
    elif not profile.is_none_approved:
        return StatusMessage.get_message(StatusMessage.StatusType.NONE_APPROVED_STATUS)
    elif not profile.is_not_approved: 
        return StatusMessage.get_message(StatusMessage.StatusType.NOT_APPROVED_STATUS)
    elif not profile.is_graduate_approved: 
        return StatusMessage.get_message(StatusMessage.StatusType.GRADUATE_APPROVED_STATUS)
    elif not profile.is_approved:
        return StatusMessage.get_message(StatusMessage.StatusType.APPROVED_STATUS)
    else:
        return StatusMessage.empty_message
