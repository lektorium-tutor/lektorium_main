# Generated by Django 3.2.15 on 2022-12-20 16:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lektorium_main', '0013_auto_20221220_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag_id',
            field=models.CharField(default=uuid.UUID('c4bb44f3-d698-4947-919c-869a4fdb47f4'), max_length=255, unique=True),
        ),
    ]
