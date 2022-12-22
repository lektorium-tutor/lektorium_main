import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from django.conf import settings

def apply_settings(django_settings):
    django_settings.SOCIAL_AUTH_PIPELINE += ['lektorium_main.pipeline.profile.create', ]

    django_settings.EDUCONT_BASE_URL = 'https://api.dev.educont.ru'
    django_settings.LEARNING_BASE_URL = 'https://apps.class.lektorium.tv/learning/course'
    django_settings.SYSTEM_CODE_EDUCONT = "66a79e1f-0d24-46bf-9d77-a3af72e61384"
    django_settings.PRIVATE_KEY_EDUCONT = """-----BEGIN PRIVATE KEY-----
    MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/DrL3/ujNZkEM
    w6QNevX9yYofjMPfFqlETrKyzJV/slQxSoKthbrmkt4z3m+Vn+qfNBFLzU9LrmUW
    liJpP5lVJZptOweCtFJwIb+Eu/8vbLj7wQHb9XNNUk/JR15Ekrb/D6nyF673aeHm
    gss8PqboOGIuDuOoeYSAaAWYvfsZ32wHGJNawjJYMh0NiMOthUyXBD1GOC/CGKsV
    xvAi2QzNGgW5x6D/HGiU5gxoxvYNLj3OB8VBy1b3xL+URfNlQGfBFxe8gb4hyp4h
    Pi0KMdKaihD20ucaV5vd2Qaw9MWHrjSBSu06R99SLD6Q7ObvaSJjYZLqmdmz/O5v
    080gQmHhAgMBAAECggEAEz7uENTFC0HQbjJ8AV6gToUhjI2PwpaEDQ03a5L3wVIL
    sJ5unP+yZN0pFIUE7QfbqNdkIaRoJznFVZnglAUT01OzI2s1lblH76M6qWqNqW+U
    j8mwwAFQ8NpIjsBJcvNrizR+/FPd7G7mUmPdCK/P/OcHHtghnzxEeHHiFHGYzJF8
    GgRZ62SiCh3iiygzvPfJQGQPdrdLplJjZgijBkUrOaw19pBdLY2earw/BHAxXJ6K
    9KPJn7M7r4BdtL8UmrcTwdbKnf/BMaQvyOIZyWOBvk8nTplWrxORCIFomoq7hFMJ
    j8ZWOJF2/2fkj3K4/ExGMLWE0dZ8wvkrxx0cGR9HlQKBgQDLzXLWR6SFN4q/eSck
    KjTIkk0WK5OW142b4ovYFqTm1lsOYgBqbNRdYoRJkNRgMI1/OiUHlcxM2yrE7ryh
    dPTC9iFjCj3MbCJtNAFuSODrAsE3H+Y5s0FocP4/nUNHI+fot+aYvpeaQJVzYjo3
    AMWVJECI1ofG7xLcLLq8zzjffQKBgQDv/Zolgz1DZAhj/Gl/v1xVmEME/QusYz8n
    Q7+sGqkGLpuJnucqjbaq7WjbeEjpfjVJ7/Go+YwbbTBjq+AIVkYFpKLNEQX/yja4
    lmFB4cpjxo3qB3L0BR13qUqvgIdtbB6O6wGfLqPUTvfxTBmOnJq/63zEQ9A0qY8y
    LLpDgPEhNQKBgQCrBdkcYDp7YESasTxbaN+qgLsXo7HSn0hCTDY2O6pd2/vFchAP
    Pwxm4UlJwrO1lIjo/w4b82TiCfk2EXFRvCe5g3o49lsttICfS0j4F0hHbqRdcfNs
    8DQvRMLW902B4Wu3Krvj6eymkRPZI9DeX1Nu+GD/c6e1FOKqyQ5bazm6sQKBgQCj
    Fyu/HG3wszVEhY9IYkokXQIGjNR3BUcwrsi986wz6E6I+rTL5Vxi0k30/8xE6SDb
    qzUGCPhe1xgQVAg+giq5wQVl6JC0IL6JOKDFfeTlY1Sj2wYSsLsyy5hWpjjicpxd
    sXT7sV1idXvnvjiMAv7jN+wlEJSYhTYr+dtm7mRvlQKBgALw0/MYyYYClQrb0AUU
    wck2gRsIn/XNp7JdHjHNYO4zkT+8OHfbNFWEfgoNbCxhKBjzUHE5q6qCpUtqP15R
    4xKQKg7RWM0DV00Z5NMIcIMJ4PfemRUSWk9yIGReHgwPlYtSGjei6be6zn9qk5m9
    Q66RhL6+PGReF5QUCtUGAqIf
    -----END PRIVATE KEY-----"""



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
