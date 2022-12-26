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
def listen_educont_sse():
    request_path = f"{settings.EDUCONT_BASE_URL}/sse/connect"
    request_hash = hashlib.md5(request_path.encode()).hexdigest()
    encoded_token = jwt.encode({
        "systemName": "Лекториум",
        "createdTimestamp": int(timezone.now().timestamp()),
        "requestHash": request_hash,
        "systemCode": settings.SYSTEM_CODE_EDUCONT
    }, settings.PRIVATE_KEY_EDUCONT, algorithm="RS256")

    r = requests.get(request_path, stream=True)
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! {json.loads(decoded_line)}')

# @worker_ready.connect
# def at_start(sender, **k):
#     with sender.app.connection() as conn:
#          sender.app.send_task('listen_sse')
