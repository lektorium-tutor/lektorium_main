# Generated by Django 3.2.15 on 2022-12-22 10:46

from django.db import migrations
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0025_auto_20221222_0609'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='block_key',
            field=opaque_keys.edx.django.models.UsageKeyField(blank=True, max_length=255, null=True),
        ),
    ]
