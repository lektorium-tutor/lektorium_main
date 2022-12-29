import logging
import datetime
import logging

import requests
from celery import shared_task
from django.conf import settings
from lms import CELERY_APP
from lektorium_main.api import utcformat, gen_tokenV2
from .models import Transaction, EducontStatisticsItem, TransactionStatus, TransactionErrorMessage

# from celery.signals import worker_ready


logger = logging.getLogger('lektorium_main.profile.tasks')

from celery.schedules import crontab

CELERY_APP.conf.beat_schedule = {
    'nightly_send': {
        'task': 'send_stats',
        'schedule': crontab(hour=4, minute=28),
        'args': (),
    },
'nightly_ask': {
        'task': 'ask_about_transactions',
        'schedule': crontab(minute=23),
        'args': (),
    },
}

CELERY_APP.conf.timezone = 'Europe/Moscow'

@CELERY_APP.task(
    name='send_stats',
    bind=True,
    acks_late=False,
)
def send_stats_educont(*args, **kwargs):
    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name='Europe/Moscow')
    now = utcformat(datetime.datetime.now(tz=tz), tz)

    old_time = now.today() - datetime.timedelta(days=60)  # не самый правильный, но фильтр старых записей
    items = EducontStatisticsItem.objects.filter(createdAt__gte=old_time, transaction__isnull=True)
    body = {'data': [item.to_dict() for item in items]}
    path = f'{settings.EDUCONT_BASE_URL}/api/v1/public/statistics'

    token = gen_tokenV2(method='POST', path=path, body=body)
    response = requests.post(url=path, json=body, headers={'Content-Type': 'application/json',
                                                           'Authorization': f'Bearer {token}'})
    logger.warning(f'Response: {response.status_code}, {response.text}')

    transaction = Transaction.objects.create(id=response.text, status=TransactionStatus.__empty__)


@CELERY_APP.task(
    name='ask_about_transactions',
    bind=True,
    acks_late=False,
)
def ask_about_transactions(*args, **kwargs):
    for transaction in Transaction.objects.filter(status__in=
    [
        TransactionStatus.__empty__,
        TransactionStatus.IN_WAITING,
        TransactionStatus.IN_PROCESSING
    ]):
        path = f'{settings.EDUCONT_BASE_URL}/api/v1/public/transaction/{transaction.id}'

        token = gen_tokenV2(method='GET', path=path)
        response = requests.get(url=path,
                                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
        if response.status_code != 200:
            logger.error(f'Get transaction info returned {response.status_code} with text {response.text}. Transaction: {transaction.id}')
            continue

        new_status = response.text
        if new_status in TransactionStatus.names:
            transaction.update({'status':new_status})

        if new_status == TransactionStatus.WITH_ERRORS:
            logger.info(f'TransactionStatus.WITH_ERRORS: {response.text}')
            logger.info(f'TransactionStatus.WITH_ERRORS: {response.json()}')
            for error_msg in response.json():
                TransactionErrorMessage.objects.create(
                    message=error_msg,
                    transaction=transaction
                )



