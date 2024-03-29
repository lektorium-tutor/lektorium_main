# Generated by Django 3.2.15 on 2022-12-29 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lektorium_main', '0035_auto_20221227_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.CharField(default=uuid.uuid4, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('status', models.CharField(blank=True, choices=[(None, 'CREATED'), ('IN_WAITING', 'IN_WAITING'), ('IN_PROCESSING', 'IN_PROCESSING'), ('COMPLETED', 'COMPLETED'), ('WITH_ERRORS', 'WITH_ERRORS'), ('FAILED', 'FAILED')], max_length=16)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verified_profile_educont', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='TransactionErrorMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('fixed', models.BooleanField(default=False)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='error_messages', to='lektorium_main.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalTransaction',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.CharField(db_index=True, default=uuid.uuid4, max_length=36)),
                ('status', models.CharField(blank=True, choices=[(None, 'CREATED'), ('IN_WAITING', 'IN_WAITING'), ('IN_PROCESSING', 'IN_PROCESSING'), ('COMPLETED', 'COMPLETED'), ('WITH_ERRORS', 'WITH_ERRORS'), ('FAILED', 'FAILED')], max_length=16)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical transaction',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='educontstatisticsitem',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='lektorium_main.transaction'),
        ),
    ]
