from social_core.backends.oauth import BaseOAuth2
import jwt
import os
import time
import hashlib
import json
import requests
import logging


class CokOAuth2(BaseOAuth2):
    name = 'educont'
    API_URL = 'https://educont.ru/api/external/v1'
    AUTHORIZATION_URL = 'https://educont.ru/oauth/authorize'  # '{}/oauth2/authorize'.format(settings.SSO_ROO_URL)
    ACCESS_TOKEN_URL = 'https://educont.ru/api/external/v1/oauth/token'  # '{}/oauth2/access_token'.format(settings.SSO_ROO_URL)
    DEFAULT_SCOPE = ["external_system.read"]
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    SCOPE_SEPARATOR = ','
    STATE_PARAMETER = True
    SEND_USER_AGENT = True
    TOKEN_TYPE = 'Bearer'

    def state_token(self):
        """Generate csrf token to include as state parameter."""
        return self.strategy.random_string(8)

    def api_url(self):
        return self.API_URL

    def get_user_details(self, response):
        logging.warning(response)
        logging.warning(dir(response))
        nickname = response.get('login').split('@')[0] or ''
        fullname = response.get('fullName')
        name = response.get('name')
        surname = response.get('surname')
        if response.get('email'):
            email = response.get('email')
        else:
            email = nickname + "@class.lektorium.tv"
        # email = response.get('email') or response.get('email', nickname + "@class.lektorium.tv")
        return {
            'username': nickname,
            'email': email,
            'fullname': fullname,
            'first_name': name,
            'last_name': surname,
        }

    def user_data(self, access_token, *args, **kwargs):
        logging.warning(dir(self))
        return self.get_json('{0}/profile'.format(self.API_URL), method="POST", headers={
            'Authorization': '{0} {1}'.format(self.TOKEN_TYPE, access_token)
        })
