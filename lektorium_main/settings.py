import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn='https://39b89a1b7ec546f4978f0d4c0f828ee4@sentry.urfu.online/9',
    integrations=[DjangoIntegration(),
                  LoggingIntegration(
                      level=logging.INFO,  # Capture info and above as breadcrumbs
                      event_level=logging.ERROR  # Send errors as events
                  )],
    traces_sample_rate=1.0,
    _experiments={
        'profiles_sample_rate': 1.0,
    },
    send_default_pii=True
)
