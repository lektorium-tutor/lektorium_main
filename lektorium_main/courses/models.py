import base64
import hashlib
import logging
import time
import uuid

import jwt
import requests
from django.conf import settings
from django.db import models
from django_mysql.models import SetCharField
from polymorphic.models import PolymorphicModel

from lektorium_main.core.models import BaseModel

log = logging.getLogger(__name__)


class TagCategory(BaseModel):
    name = models.CharField("Наименование категории", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория тегов'
        verbose_name_plural = 'категории тегов'


class Tag(BaseModel):
    """
    id: string (uuid) "id тега"
    name: string "Наименование тега"
    parentId: string (uuid) "id родительского тэга" null=True
    """
    tag_id = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    name = models.CharField("Наименование тега", max_length=255)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TagCategory, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Course(PolymorphicModel):
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

    # COURSE_TYPES = (
    #     (0, "ЦОК"),
    #     (1, "Раздел"),
    #     (2, "Тема"),
    #     (3, "Учебный материал")
    # )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    externalId = models.CharField(unique=True, max_length=255)
    courseName = models.CharField("Название учебного материала", max_length=255, blank=False, null=False)

    # courseTypeId = models.PositiveSmallIntegerField("id типа учебного материала", choices=COURSE_TYPES)

    def __str__(self):
        return self.courseName


class COK(Course):
    @property
    def courseTypeId(self):
        return 0

    course_id = models.CharField("ИД курса на едх", max_length=255, blank=True, null=True)

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
        max_length=(9 + 7 * 2),  # 1..16,
        blank=True
    )
    tags = models.ManyToManyField(Tag)

    class Meta:
        verbose_name = "курс ЦОК"
        verbose_name_plural = "курсы ЦОК"

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
        body = {"externalId": self.externalId,
                "courseTypeId": self.courseTypeId,
                "courseImage": course_image_base64,
                "externalLink": self.externalLink,
                "grades": self.grades,
                "courseName": self.courseName,
                "courseDescription": self.courseDescription,
                "tags": [tag.tag_id for tag in self.tags.all()],
                }
        request_hash = hashlib.md5(body).hexdigest()

        encoded_token = jwt.encode({
            "systemName": "Лекториум",
            "createdTimestamp": timestamp,
            "requestHash": request_hash,
            "systemCode": settings.SYSTEM_CODE
        }, settings.PRIVATE_KEY, algorithm="RS256")

        r = requests.post(f"{settings.EDUCONT_BASE_URL}/api/v1/public/educational-courses",
                          data=body,
                          headers={"Authorization": f"Bearer {encoded_token}"}
                          )
        log.warning(f"POST COURSE: {r.json()}")


class Section(Course):
    @property
    def courseTypeId(self):
        return 1

    externalParent = models.ForeignKey(COK, related_name="sections", blank=False, null=False,
                                       on_delete=models.CASCADE)

    class Meta:
        verbose_name = "раздел курса"
        verbose_name_plural = "разделы курса"


class Topic(Course):
    @property
    def courseTypeId(self):
        return 2

    externalParent = models.ForeignKey(Course, related_name="topics", blank=False, null=False,
                                       on_delete=models.CASCADE)

    class Meta:
        verbose_name = "тема"
        verbose_name_plural = "темы"


class TeachingMaterial(Course):
    @property
    def courseTypeId(self):
        return 3

    externalLink = models.URLField("Ссылка в системе-источнике", blank=False, null=False)
    externalParent = models.ForeignKey(Course, related_name="teaching_materials", blank=False, null=False,
                                       on_delete=models.CASCADE)

    tags = models.ManyToManyField(Tag)

    class Meta:
        verbose_name = "материал"
        verbose_name_plural = "материалы"
