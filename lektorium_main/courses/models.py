from django.db import models
from polymorphic.models import PolymorphicModel

from lektorium_main.models import BaseModel


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
    courseName = models.CharField("Название учебного материала", blank=False, null=False)
    courseTypeId = models.PositiveSmallIntegerField("id типа учебного материала", choices=COURSE_TYPES)


class COK(Course):
    courseTypeId = 0
    courseImageFile = models.ImageField("Файл изображения",
                                        help_text="Изображение не должно содержать никаких надписей." \
                                                  "Разрешение - 600x600 пикселей (допускается 500х500). Формат – jpg, jpeg, png." \
                                                  " Размер – не более 5Мб.",
                                        blank=False, null=False)
    externalLink = models.URLField("Ссылка в системе-источнике", blank=False, null=False)
    courseDescription = models.TextField("Описание учебного материала", blank=False, null=False)


class EducationalCourse(Course):
    courseTypeId = 3
    externalLink = models.URLField("Ссылка в системе-источнике", blank=False, null=False)
    courseDescription = models.TextField("Описание учебного материала", blank=False, null=False)
