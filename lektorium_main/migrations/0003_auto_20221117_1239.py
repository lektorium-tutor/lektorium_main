# Generated by Django 3.2.15 on 2022-11-17 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lektorium_main', '0002_cok_course_educationalcourse_section_tag_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verified_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='educationalInstitutions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lektorium_main.educationalinstitutions', verbose_name='Данные об образовательных учреждениях пользователя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='isActive',
            field=models.BooleanField(verbose_name='Флаг функционирующего аккаунта'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='login',
            field=models.CharField(max_length=50, verbose_name='Логин'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='middleName',
            field=models.CharField(max_length=50, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('TEACHER', 'Teacher'), ('STUDENT', 'Student')], max_length=15, verbose_name='Роль пользователя в Системе'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='statusConfirmEmail',
            field=models.CharField(blank=True, choices=[('CONFIRM', 'Confirm'), ('NOT_CONFIRM', 'Not Confirm'), ('NEW_PROFILE', 'New Profile'), ('OLD_PROFILE', 'Old Profile')], max_length=15, null=True, verbose_name='Статус подтверждения почты пользователя в Системе'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='surname',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Фамилия'),
        ),
    ]
