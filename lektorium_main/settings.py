import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from django.conf import settings

def apply_settings(django_settings):
    django_settings.SOCIAL_AUTH_PIPELINE += ['lektorium_main.pipeline.profile.create', ]

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

# SOCIAL_AUTH_PIPELINE = ['lektorium_main.oauth2.pipeline.profile.save_profile', ]

# insert_enterprise_pipeline_elements(SOCIAL_AUTH_PIPELINE)
