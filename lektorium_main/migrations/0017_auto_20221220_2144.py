# Generated by Django 3.2.15 on 2022-12-20 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0016_alter_studentstatisticsitem_profile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loggedin',
            name='profile_id',
            field=models.CharField(blank=True, max_length=36, null=True, verbose_name='id профиля пользователя в системе Educont'),
        ),
        migrations.AlterField(
            model_name='studentstatisticsitem',
            name='profile_id',
            field=models.CharField(blank=True, max_length=36, null=True, verbose_name='id профиля пользователя в системе Educont'),
        ),
    ]