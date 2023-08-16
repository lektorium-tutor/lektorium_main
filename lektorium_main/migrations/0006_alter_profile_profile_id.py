# Generated by Django 3.2.15 on 2022-12-14 08:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0005_profile_profile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
