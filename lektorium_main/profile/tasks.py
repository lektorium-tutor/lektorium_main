import hashlib
import json
import logging

import jwt
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from aiohttp_sse_client import client as sse_client
import asyncio
from openedx.core.lib.celery import APP
import celery_pool_asyncio
# from celery.signals import worker_ready


logger = logging.getLogger('lektorium_main.profile.tasks')

app=APP


@app.task
async def listen_educont_sse(*args, **kwargs):
    logger.warning(f'!!!!!!!!!!!!!! {args}; {kwargs}')
    request_path = f"{settings.EDUCONT_BASE_URL}/api/v1/public/sse/connect"
    request_hash = hashlib.md5(request_path.encode()).hexdigest()
    encoded_token = jwt.encode({
        "systemName": "Лекториум",
        "createdTimestamp": int(timezone.now().timestamp()),
        "requestHash": request_hash,
        "systemCode": settings.SYSTEM_CODE_EDUCONT
    }, settings.PRIVATE_KEY_EDUCONT, algorithm="RS256")

    # r = requests.get(request_path, headers={"Authorization": f"Bearer {encoded_token}"}, stream=True)
    async with sse_client.EventSource(
        request_path,
        headers={"Authorization": f"Bearer {encoded_token}"}
    ) as event_source:
        # try:
        async for event in event_source:
            logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! {event}')
        # except ConnectionError:
        #     pass


    # logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! {r}')
    # for line in r.iter_lines():
    #     logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! {r.url} -- {line}')
    #     if line:
    #         decoded_line = line.decode('utf-8')
    #         logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! {json.loads(decoded_line)}')

# @worker_ready.connect
# def at_start(sender, **k):
#     with sender.app.connection() as conn:
#          sender.app.send_task('listen_sse')
