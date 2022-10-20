"""
Database models for lektorium_main.
"""
from model_utils.models import TimeStampedModel
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel


class Profile(PolymorphicModel, TimeStampedModel):
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
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    isActive = models.BooleanField()
    login = models.CharField(max_length=50)
    middleName = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    fullName = models.CharField(max_length=200)
    id = models.UUIDField()
    email = models.EmailField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
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


class EducationalInstitution(TimeStampedModel):
    class TypeEducationalInstitution(models.TextChoices):
        SCHOOL = 'SCHOOL',
        COLLEGE = 'COLLEGE'

    # Fields
    fullName = models.TextField(max_length=100)
    shortName = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    kpp = models.CharField(max_length=50)
    id = models.UUIDField()
    inn = models.CharField(max_length=50)
    street = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    isTest = models.BooleanField(default=False)
    address = models.TextField(max_length=200)
    postIndex = models.CharField(max_length=30)
    municipalArea = models.CharField(max_length=50)
    typeEducationalInstitution = models.CharField(max_length=5, choices=TypeEducationalInstitution.choices)
    schoolName = models.TextField(max_length=200)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("lektorium_main_EducationalInstitution_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_EducationalInstitution_update", args=(self.pk,))


class EducationalInstitutions(TimeStampedModel):
    # Relationships
    educationalInstitution = models.ForeignKey("lektorium_main.EducationalInstitution", on_delete=models.SET_NULL)

    # Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    approvedStatus = models.CharField(max_length=50)
    isActual = models.NullBooleanField()

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
                                                            on_delete=models.SET_NULL)

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
                                                          on_delete=models.SET_NULL)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("lektorium_main_TeacherProfile_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("lektorium_main_TeacherProfile_update", args=(self.pk,))


class TeacherTagEducationalInstitutions(TimeStampedModel):
    tagId = models.CharField(max_length=100, blank=True, null=True)
    gradeEducationalInstitutions = models.ForeignKey("lektorium_main.GradeEducationalInstitutions",
                                                     on_delete=models.SET_NULL)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class StudentTagEducationalInstitutions(TimeStampedModel):
    tagId = models.CharField(max_length=100, blank=True, null=True)
    gradeEducationalInstitutions = models.ForeignKey("lektorium_main.GradeEducationalInstitutions",
                                                     on_delete=models.SET_NULL)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class GradeEducationalInstitutions(TimeStampedModel):
    educationalInstitutionId = models.UUIDField(editable=False, unique=True)
    letter = models.CharField(max_length=10, blank=True, null=True)
    grade = models.ForeignKey("lektorium_main.Grade", on_delete=models.SET_NULL)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)


class Grade(TimeStampedModel):
    class TypeEducationalInstitution(models.TextChoices):
        SCHOOL = 'SCHOOL',
        COLLEGE = 'COLLEGE'

    id = models.UUIDField(editable=False, unique=True)
    value = models.PositiveSmallIntegerField(blank=True, null=True)
    typeEducationalInstitution = models.CharField(max_length=15, choices=TypeEducationalInstitution.choices)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)
