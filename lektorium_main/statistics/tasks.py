import hashlib
import json
import logging

import jwt
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

# from celery.signals import worker_ready


logger = logging.getLogger('lektorium_main.profile.tasks')


@shared_task(
    name='listen_sse',
    bind=True,
    acks_late=False,
)
def send_stats_educont(*args, **kwargs):
    logger.warning(f'!!!!!!!!!!!!!! {args}; {kwargs}')
    request_path = f"{settings.EDUCONT_BASE_URL}/statistics"
    request_hash = hashlib.md5(request_path.encode()).hexdigest()
    encoded_token = jwt.encode({
        "systemName": "Лекториум",
        "createdTimestamp": int(timezone.now().timestamp()),
        "requestHash": request_hash,
        "systemCode": settings.SYSTEM_CODE_EDUCONT
    }, settings.PRIVATE_KEY_EDUCONT, algorithm="RS256")

    r = requests.post(request_path, headers={"Authorization": f"Bearer {encoded_token}"}, stream=True)

