# Generated by Django 3.2.15 on 2022-12-15 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0009_statusmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusmessage',
            name='status_type',
            field=models.CharField(choices=[('ACTIVE_STATUS', 'Active Status'), ('EMPTY_EDU_INST', 'Empty Edu Inst'), ('APPROVED_STATUS', 'Approved Status'), ('ACTUAL_STATUS', 'Actual Status'), ('NOT_APPROVED_STATUS', 'Not Approved Status'), ('NONE_APPROVED_STATUS', 'None Approved Status'), ('GRADUATE_APPROVED_STATUS', 'Graduate Approved Status')], help_text='ВНИМАНИЕ! Типы сообщений униакальные для каждой записи', max_length=50, unique=True, verbose_name='Тип сообщения'),
        ),
    ]