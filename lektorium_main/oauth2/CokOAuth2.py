# from social_core.backends.oauth import BaseOAuth2
# import jwt
# import os
# import time
# import hashlib
# import json
# import logging


# class CokOAuth2(BaseOAuth2):
#     name = 'educont'
#     ID_KEY = 'lektorium'
#     AUTHORIZATION_URL = 'https://dev.educont.ru/oauth/authorize'  # '{}/oauth2/authorize'.format(settings.SSO_ROO_URL)
#     ACCESS_TOKEN_URL = 'https://dev.educont.ru/api/external/v1/oauth/token'  # '{}/oauth2/access_token'.format(settings.SSO_ROO_URL)
#     DEFAULT_SCOPE = ["external_system.read"]
#     ACCESS_TOKEN_METHOD = 'POST'
#     REDIRECT_STATE = False
#     SCOPE_SEPARATOR = ' '

#     def get_user_details(self, response):
#         logging.warning(response)
#         nickname = response.get('login') or ''
#         fullname, name, surname, middleName = self.get_user_names(
#             fullname=response.get('fullName'),
#             name=response.get('name'),
#             surname=response.get('surname'),
#             middleName=response.get('middleName')
#         )
#         email = response.get('email')
#         return {
#             'username': nickname,
#             'email': email,
#             'fullname': fullname,
#             'first_name': name,
#             'last_name': surname
#         }

#     def user_data(self, access_token, *args, **kwargs):
#         logging.warning(kwargs.pop('response'))
#         response = kwargs.pop('response')
#         return self.get_json('https://dev.educont.ru/api/external/v1/profile',method="POST", headers={
#             'Authorization': '{0} {1}'.format(response.get('token_type'),
#                                               access_token)
#         })


from social_core.backends.oauth import BaseOAuth2
import jwt
import os
import time
import hashlib
import json
import logging
from urllib.parse import urljoin

class CokOAuth2(BaseOAuth2):
    name = 'educont'
    API_URL='https://dev.educont.ru/api/external/v1/'
    AUTHORIZATION_URL = 'https://dev.educont.ru/oauth/authorize'  # '{}/oauth2/authorize'.format(settings.SSO_ROO_URL)
    ACCESS_TOKEN_URL = 'https://dev.educont.ru/api/external/v1/oauth/token'  # '{}/oauth2/access_token'.format(settings.SSO_ROO_URL)
    DEFAULT_SCOPE = ["external_system.read"]
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    SCOPE_SEPARATOR = ','
    STATE_PARAMETER = True
    SEND_USER_AGENT = True

    def state_token(self):
        """Generate csrf token to include as state parameter."""
        return self.strategy.random_string(8)

    def api_url(self):
        return self.API_URL

    def get_user_details(self, response):
        logging.warning(response)
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
        """Loads user data from service"""
        data = self._user_data(access_token)
        # if not data.get('email'):
        #     try:
        #         emails = self._user_data(access_token, '/emails')
        #     except (HTTPError, ValueError, TypeError):
        #         emails = []

        #     if emails:
        #         email = emails[0]
        #         primary_emails = [
        #             e for e in emails
        #             if not isinstance(e, dict) or e.get('primary')
        #         ]
        #         if primary_emails:
        #             email = primary_emails[0]
        #         if isinstance(email, dict):
        #             email = email.get('email', '')
        #         data['email'] = email
        return data

    def _user_data(self, access_token, path=None):
        url = urljoin(self.api_url(), 'profile')
        logging.warning(self.get_json(url, method="POST", headers={'Authorization': f'token {access_token}'}))
        return self.get_json(url, method="POST", headers={'Authorization': f'token {access_token}'})

    # def user_data(self, access_token, *args, **kwargs):
    #     return self.get_json('https://dev.educont.ru/api/external/v1/profile',method="POST" , headers={
    #         'Authorization': '{0} {1}'.format(response.get('token_type'),
    #                                           access_token)
    #     })
