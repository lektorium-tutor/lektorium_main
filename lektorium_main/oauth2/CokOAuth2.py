from social_core.backends.oauth import BaseOAuth2
import jwt
import os
import time
import hashlib
import json


class CokOAuth2(BaseOAuth2):
    name = 'educont'
    ID_KEY = 'lektorium'
    AUTHORIZATION_URL = 'https://dev.educont.ru/oauth/authorize'  # '{}/oauth2/authorize'.format(settings.SSO_ROO_URL)
    ACCESS_TOKEN_URL = 'https://dev.educont.ru/api/external/v1/oauth/token'  # '{}/oauth2/access_token'.format(settings.SSO_ROO_URL)
    DEFAULT_SCOPE = ["external_system.read"]
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    SCOPE_SEPARATOR = ' '

    def get_user_details(self, response):
        nickname = response.get('login') or ''
        fullname, name, surname, middleName = self.get_user_names(
            fullname=response.get('fullName'),
            name=response.get('name'),
            surname=response.get('surname'),
            middleName=response.get('middleName')
        )
        email = response.get('email')
        return {
            'username': nickname,
            'email': email,
            'fullname': fullname,
            'first_name': name,
            'last_name': surname
        }

    def user_data(self, access_token, *args, **kwargs):
        response = kwargs.pop('response')
        return self.get_json('https://dev.educont.ru/api/external/v1/profile', headers={
            'Authorization': '{0} {1}'.format(response.get('token_type'),
                                              access_token)
        })
