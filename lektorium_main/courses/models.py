from django.conf import settings
import base64
import hashlib
import time

import jwt
import requests
from django.conf import settings
from django.db import models
from django_mysql.models import SetCharField
from polymorphic.models import PolymorphicModel
import logging

from lektorium_main.api import SYSTEM_CODE, PRIVATE_KEY
from lektorium_main.core.models import BaseModel
log = logging.getLogger(__name__)

class TagCategory(BaseModel):
    name = models.CharField("Наименование категории", max_length=255)


class Tag(BaseModel):
    """
    id: string (uuid) "id тега"
    name: string "Наименование тега"
    parentId: string (uuid) "id родительского тэга" null=True
    """
    name = models.CharField("Наименование тега", max_length=255)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TagCategory, blank=True, null=True, on_delete=models.CASCADE)


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
    externalId = models.CharField(unique=True)
    courseName = models.CharField("Название учебного материала", max_length=255, blank=False, null=False)
    courseTypeId = models.PositiveSmallIntegerField("id типа учебного материала", choices=COURSE_TYPES)


class COK(Course):
    @property
    def courseTypeId(self):
        return 0

    course_id = models.CharField("ИД курса на едх", max_length=255)

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

    def educont_upload(self):
        """
        {
            "data": [
        {
                "externalId": "math11",
                "courseTypeId":"4",
                "courseImage": "data:image/png;base64,iVBORw0KGgoAAAANSU...hEUgAAABgAAAAYCA",
                "externalLink": "https://.....ru",
                "grades": "["11" ]",
                "courseName": "Степени и логарифмы (10-11 класс)",
              "courseDescription": "Логарифмы - сложная тема в школьном курсе математики. И причина состоит в том, что даже для их определения используются неудачные формулировки...",
                "tags":"[ { "id": "bbd7befb-10d3-4bd5-8f65-17b3073e20ec" },   { "id": "78d7befb-22d3-4bd5-8f65-17b3073e20ec" }]"
        }
            ]
        }
        """

        timestamp = int(time.time())
        with open(self.courseImageFile.path, "rb") as img_file:
            course_image_base64 = base64.b64encode(img_file.read())
        body = [
            {"externalId": self.externalId,
             "courseTypeId": self.courseTypeId,
             "courseImage": course_image_base64,
             "externalLink": self.externalLink,
             "grades": self.grades,
             "courseName": self.courseName,
             "courseDescription": self.courseDescription,
             "tags": self.tags.all(),
             }
        ]
        request_hash = hashlib.md5(body).hexdigest()

        encoded_token = jwt.encode({
            "systemName": "Лекториум",
            "createdTimestamp": timestamp,
            "requestHash": request_hash,
            "systemCode": SYSTEM_CODE
        }, PRIVATE_KEY, algorithm="RS256")

        r = requests.post(f"{settings.EDUCONT_BASE_URL}/api/v1/public/educational-courses",
                      data=body,
                      headers={"Authorization": f"Bearer {encoded_token}"}
                      )
        log.warning(f"POST COURSE: {r.json()}")


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
