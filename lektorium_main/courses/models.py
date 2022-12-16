import uuid

from django.db import models
from django_mysql.models import SetCharField
from polymorphic.models import PolymorphicModel

from lektorium_main.core.models import BaseModel


class Tag(BaseModel):
    """
    id: string (uuid) "id тега"
    name: string "Наименование тега"
    parentId: string (uuid) "id родительского тэга" null=True
    """
    name = models.CharField("Наименование тега", max_length=255)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)


class Course(PolymorphicModel, BaseModel):
    """
    Учебный материал (в том числе ЦОК), который предоставляет образовательная платформа
    для изучения пользователям.
    Иерархия ЦОКа выглядит следующим образом:
    ЦОК – Раздел – Тема – Учебный материал.
    ЦОК и учебный материал обязательны, раздел и тема могут быть опущены, если они не предусмотрены в ЦОК.

    Для ЦОК обязательны поля:
        - id учебного материала (externalId);
        - тип учебного материала (courseTypeId);
        - изображение (courseImage);
        - ссылка в системе-источнике (externalLink);
        - перечень классов, которым доступен материал (grades);
        - название (courseName);
        - описание (courseDescription);
        - перечень тегов, соответствующих этому ЦОК (tags).

    Для учебного материала обязательны поля:
        - id учебного материала (externalId);
        - тип учебного материала (courseTypeId);
        - id родительского элемента в иерархии (externalParentId);
        - название (courseName);
        - перечень тегов, соответствующих этому учебному материалу (в т.ч. тег «Вид учебного материала»

        (на 1 учебный материал нужно добавить столько тегов, чтобы можно было точно определить,
        что он из себя представляет.
        Например, если у Вас лекция в видеоформате, то следует прикрепить 2 тега: «Лекция» и «Видеоролик»)) (tags).

    """

    COURSE_TYPES = (
        (0, "ЦОК"),
        (1, "Раздел"),
        (2, "Тема"),
        (3, "Учебный материал")
    )
    externalId = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    courseName = models.CharField("Название учебного материала", max_length=255, blank=False, null=False)
    courseTypeId = models.PositiveSmallIntegerField("id типа учебного материала", choices=COURSE_TYPES)


class COK(Course):
    @property
    def courseTypeId(self):
        return 0

    courseImageFile = models.ImageField("Файл изображения",
                                        help_text="Изображение не должно содержать никаких надписей. "
                                                  "Разрешение - 600x600 пикселей (допускается 500х500). "
                                                  "Формат – jpg, jpeg, png. Размер – не более 5Мб.",
                                        blank=False, null=False)
    externalLink = models.URLField("Ссылка в системе-источнике", blank=False, null=False)
    courseDescription = models.TextField("Описание учебного материала", blank=False, null=False)
    grades = SetCharField(
        verbose_name="Массив классов, которым доступен учебный материал",
        base_field=models.PositiveSmallIntegerField(),
        size=16,
        max_length=(9 + 7 * 2),  # 1..16
    )
    tags = models.ManyToManyField(Tag)


class Section(Course):
    @property
    def courseTypeId(self):
        return 1

    externalParent = models.ForeignKey(Course, related_name="sections", blank=False, null=False,
                                       on_delete=models.CASCADE)


class Topic(Course):
    @property
    def courseTypeId(self):
        return 2

    externalParent = models.ForeignKey(Course, related_name="topics", blank=False, null=False,
                                       on_delete=models.CASCADE)


class EducationalCourse(Course):
    @property
    def courseTypeId(self):
        return 3

    externalLink = models.URLField("Ссылка в системе-источнике", blank=False, null=False)
    courseDescription = models.TextField("Описание учебного материала", blank=False, null=False)
    externalParent = models.ForeignKey(Course, related_name="educational_courses", blank=False, null=False,
                                       on_delete=models.CASCADE)
    grades = SetCharField(
        verbose_name="Массив классов, которым доступен учебный материал",
        base_field=models.PositiveSmallIntegerField(),
        size=16,
        max_length=(9 + 7 * 2),  # 1..16
    )
    tags = models.ManyToManyField(Tag)
