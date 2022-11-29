# Generated by Django 3.2.15 on 2022-10-26 21:15

import uuid

import django.utils.timezone
import django_mysql.models
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('lektorium_main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False,
                                                                verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False,
                                                                      verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('externalId', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('courseName', models.CharField(max_length=255, verbose_name='Название учебного материала')),
                ('courseTypeId', models.PositiveSmallIntegerField(
                    choices=[(0, 'ЦОК'), (1, 'Раздел'), (2, 'Тема'), (3, 'Учебный материал')],
                    verbose_name='id типа учебного материала')),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_lektorium_main.course_set+',
                                   to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False,
                                                                verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False,
                                                                      verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Наименование тега')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='children', to='lektorium_main.tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('course_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lektorium_main.course')),
                ('externalParent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics',
                                                     to='lektorium_main.course')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lektorium_main.course',),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('course_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lektorium_main.course')),
                ('externalParent',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections',
                                   to='lektorium_main.course')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lektorium_main.course',),
        ),
        migrations.CreateModel(
            name='EducationalCourse',
            fields=[
                ('course_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lektorium_main.course')),
                ('externalLink', models.URLField(verbose_name='Ссылка в системе-источнике')),
                ('courseDescription', models.TextField(verbose_name='Описание учебного материала')),
                ('grades', django_mysql.models.SetCharField(models.PositiveSmallIntegerField(), max_length=23, size=16,
                                                            verbose_name='Массив классов, которым доступен учебный материал')),
                ('externalParent',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educational_courses',
                                   to='lektorium_main.course')),
                ('tags', models.ManyToManyField(to='lektorium_main.Tag')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lektorium_main.course',),
        ),
        migrations.CreateModel(
            name='COK',
            fields=[
                ('course_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lektorium_main.course')),
                ('courseImageFile', models.ImageField(
                    help_text='Изображение не должно содержать никаких надписей. Разрешение - 600x600 пикселей (допускается 500х500). Формат – jpg, jpeg, png. Размер – не более 5Мб.',
                    upload_to='', verbose_name='Файл изображения')),
                ('externalLink', models.URLField(verbose_name='Ссылка в системе-источнике')),
                ('courseDescription', models.TextField(verbose_name='Описание учебного материала')),
                ('grades', django_mysql.models.SetCharField(models.PositiveSmallIntegerField(), max_length=23, size=16,
                                                            verbose_name='Массив классов, которым доступен учебный материал')),
                ('tags', models.ManyToManyField(to='lektorium_main.Tag')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('lektorium_main.course',),
        ),
    ]