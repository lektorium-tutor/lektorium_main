# Generated by Django 3.2.15 on 2022-12-14 07:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0004_auto_20221213_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]