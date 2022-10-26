"""
Database models for lektorium_main.
"""
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel

from .core.models import BaseModel


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
    educationalInstitutions = models.ForeignKey("lektorium_main.EducationalInstitutions", on_delete=models.SET_NULL,
                                                null=True, blank=True)

    # Fields
    role = models.CharField(max_length=15, choices=Role.choices)

    isActive = models.BooleanField()
    login = models.CharField(max_length=50)
    middleName = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    fullName = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)

    surname = models.CharField(max_length=50, null=True, blank=True)
    statusConfirmEmail = models.CharField(max_length=15, choices=StatusConfirmEmail.choices)
    birthdate = models.CharField(max_length=50, null=True, blank=True)
    birthyear = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("lektorium_main_Profile_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_Profile_update", args=(self.pk,))


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
                           validators=[RegexValidator('^[0-9]{10}$', 'Invalid INN')],)
    kpp = models.CharField('КПП образовательной организации', max_length=9,
                           validators=[RegexValidator('^[0-9]{9}$', 'Invalid KPP')],)
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


class EducationalInstitutions(BaseModel):
    # Relationships
    educationalInstitution = models.ForeignKey("lektorium_main.EducationalInstitution", on_delete=models.CASCADE)

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
                                                            on_delete=models.CASCADE)

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
                                                          on_delete=models.CASCADE)

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
                                                     on_delete=models.CASCADE)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class StudentTagEducationalInstitutions(BaseModel):
    tagId = models.CharField(max_length=100, blank=True, null=True)
    gradeEducationalInstitutions = models.ForeignKey("lektorium_main.GradeEducationalInstitutions",
                                                     on_delete=models.CASCADE)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class GradeEducationalInstitutions(BaseModel):
    educationalInstitutionId = models.UUIDField(editable=False, unique=True)
    letter = models.CharField(max_length=10, blank=True, null=True)
    grade = models.ForeignKey("lektorium_main.Grade", on_delete=models.CASCADE)

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
