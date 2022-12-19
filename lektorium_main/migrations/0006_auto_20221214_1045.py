# Generated by Django 3.2.15 on 2022-12-14 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0005_auto_20221214_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentstatisticsitem',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Position (Page)'),
        ),
        migrations.AddField(
            model_name='studentstatisticsitem',
            name='score',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Score'),
        ),
    ]