# Generated by Django 3.2.15 on 2022-12-14 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0006_alter_profile_profile_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentprofile',
            options={'verbose_name': 'Профиль студента', 'verbose_name_plural': 'Профили студентов'},
        ),
        migrations.AlterModelOptions(
            name='teacherprofile',
            options={'verbose_name': 'Профиль преподавателя', 'verbose_name_plural': 'Профили преподавателей'},
        ),
    ]