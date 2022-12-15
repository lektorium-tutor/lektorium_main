# Generated by Django 3.2.15 on 2022-12-15 08:11

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0008_educationalinstitution_schoolname'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusMessage',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status_type', models.CharField(choices=[('ACTIVE_STATUS', 'Active Status'), ('EMPTY_EDU_INST', 'Empty Edu Inst'), ('APPROVED_STATUS', 'Approved Status'), ('ACTUAL_STATUS', 'Actual Status'), ('NOT_APPROVED_STATUS', 'Not Approved Status'), ('NONE_APPROVED_STATUS', 'None Approved Status'), ('GRADUATE_APPROVED_STATUS', 'Graduate Approved Status')], max_length=50, unique=True, verbose_name='Тип сообщения')),
                ('message', models.CharField(blank=True, max_length=400, null=True, verbose_name='Сообщение')),
            ],
            options={
                'verbose_name': 'Сообщение для пользователя',
                'verbose_name_plural': 'Сообщения для пользователей',
            },
        ),
    ]
