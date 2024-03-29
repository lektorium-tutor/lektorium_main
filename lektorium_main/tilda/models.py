import datetime
import os

from django.conf import settings
from django.db import models
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.learning_sequences.api import get_course_outline
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from django.core.exceptions import ValidationError
import logging
from lektorium_main.tilda.utils import IrkruTildaArchive


class TildaArticle(models.Model):
    tilda_content = models.TextField(u'HTML-код', blank=True)
    styles = models.TextField(u'Стили', blank=True)
    scripts = models.TextField(u'Скрипты', blank=True)
    archive = models.FileField(u'Импорт из файла', blank=True, null=True, upload_to='tilda/zip/')
    course_id = models.CharField(u'Id курса', help_text="Вставляем без пробелов. Пример: course-v1:edX+DemoX+Demo_Course", blank=True, unique=True, max_length=300)

    class Meta:
        verbose_name = u'статья (Тильда)'
        verbose_name_plural = u'статьи (Тильда)'
    
    def clean(self):
        if not self.if_exists_course():
             raise ValidationError(u"Такой Course ID не найден")

    def _extract_path(self):
        return u'tilda/{year}/{course_id}/{folder}/'.format(
            year=datetime.date.today().year,
            course_id=self.course_id,
            folder=os.path.basename(os.path.splitext(self.archive.path)[0]),
        )

    @property
    def tilda_extract_root(self):
        """Путь к папке, в которую разархивированы файлы после импорта"""
        if self.archive:
            return settings.MEDIA_ROOT + self._extract_path()

    @property
    def tilda_extract_url(self):
        """URL папки с распакованными файлами"""
        if self.archive:
            return settings.MEDIA_URL + self._extract_path()
        
    @classmethod
    def get_latest_object(cls, course_id):
        try:
            return cls.objects.filter(course_id=course_id).latest('id')
        except cls.DoesNotExist:
            return None

    def import_archive(self):
        """Распаковать и импортировать загруженный в `archive` файл из Тильды"""
        if self.archive:
            archive = IrkruTildaArchive(self.archive, material=self)
            archive.process()
    
    def get_page(self):
        path = self.tilda_extract_root
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)) and 'page' in filename:
                full_path = (path + filename)
                HtmlFile = open(full_path, "r")
                return HtmlFile.read()
            
    def get_full_path(self):
        path = self.tilda_extract_root
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)) and 'page' in filename:
                full_path = (path + filename)
                return full_path.replace('/openedx/media/tilda/lektorium_main', '')
            
    def prepare_content(self):
        """Возвращает готовый к выводу хтмл"""
        result = self.tilda_content.replace('="images/', '="{}images/'.format(self.tilda_extract_url))
        result = result.replace("url('images/", "url('{}images/".format(self.tilda_extract_url))
        return result
    
    def if_exists_course(self):
        course_key = CourseKey.from_string(self.course_id)
        return CourseOverview.course_exists(course_key)