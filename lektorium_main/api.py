import logging
from ninja import NinjaAPI, Schema, ModelSchema
from ninja.security import django_auth, HttpBearer
from django.contrib.auth.models import User
from lektorium_main.profile.models import Profile, TeacherProfile, StudentProfile
from ninja.orm import create_schema
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
# from common.djangoapps.third_party_auth.models import get_setting
import jwt
import os
import time
import hashlib
import json
import requests
from django.conf import settings

api = NinjaAPI(csrf=True)

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return token

log = logging.getLogger(__name__)


def gen_token(request, path):
    timestamp = int(time.time())

    if request.method == "POST" or request.method == "PUT":
        requestHash = hashlib.md5(request.body).hexdigest()
    else:
        requestHash = hashlib.md5(path.encode()).hexdigest()

    encoded_token = jwt.encode({
        "systemName": "Лекториум",
        "createdTimestamp": timestamp,
        "requestHash": requestHash,
        "systemCode": settings.SYSTEM_CODE_EDUCONT
    }, settings.PRIVATE_KEY_EDUCONT, algorithm="RS256")
    return encoded_token

def gen_tokenV2(method, path, body=None):
    timestamp = int(time.time())
    logging.warning(path)
    logging.warning(method)
    logging.warning(settings.SYSTEM_CODE_EDUCONT)
    logging.warning(settings.PRIVATE_KEY_EDUCONT)
    if method == "POST" or method == "PUT":
        requestHash = hashlib.md5(body).hexdigest()
    else:
        requestHash = hashlib.md5(path.encode()).hexdigest()

    encoded_token = jwt.encode({
        "systemName": "Лекториум",
        "createdTimestamp": timestamp,
        "requestHash": requestHash,
        "systemCode": settings.SYSTEM_CODE_EDUCONT
    }, settings.PRIVATE_KEY_EDUCONT, algorithm="RS256")
    return encoded_token


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['username', 'email', 'is_staff', 'is_active']


UserProfileSchema = create_schema(
    Profile,
    # fields=[
    #     'role',
    #     'isActive',
    #     'email'
    # ],
    custom_fields=[
        ('user', UserSchema, None),
        # ('has_profile_image', bool, False),
        # ('age', int, None),
        # ('level_of_education_display', str, None),
        # ('gender_display', str, None),
        # ('country', Any, None)
    ]
)
# class UserIn(Schema):
#     username: str
#     email: str
#     # is_staff: srt = None
#     # is_active: str = None
#
# class ProfileIn(Schema):
#     role: str
#     login: str
#     middlename: str
#     name: str
#     fullname: str
#     user: UserIn
#
# @api.post("/profiles", auth=django_auth)
# def create_profile(request, payload: ProfileIn):
#     profile = Profile.objects.create(**payload.dict())
#     return {
#         "id": profile.id,
#         "success": True
#     }

@api.get("/me", auth=django_auth, response=UserProfileSchema)
def me(request):
    try:
        user = get_object_or_404(User, username=request.auth)
        profile = Profile.get_polymorph_profile(user)
        return profile
    except:
        return {"success": False}

@api.delete("/profiles/{profile_id}", auth=django_auth)
def delete_profile(request, profile_id: str):
    try:
        if (User.objects.get(username=request.auth).is_superuser):
            profile = get_object_or_404(Profile, id=profile_id)
            profile.delete()
            return {"success": True}
        else:
            raise PermissionDenied()
    except:
        pass

# не работает просто тесты.
@api.get('/test', auth=django_auth)
def test(request):
    path ='https://api.dev.educont.ru/api/v1/public/educational-courses/educational-platforms/{0}?approved=true'.format(settings.SYSTEM_CODE_EDUCONT)
    path='https://api.dev.educont.ru/api/v1/public/sse/connect'
    token = gen_token(request=request, path=path)
    test = requests.get(url=path, headers={ "Content-Type": "text/event-stream", "Authorization": 'Bearer {0}'.format(token) })
    logging.warning(test)
    return test

@api.get('/token', auth=django_auth)
def genTokenGet(request):
    path = request.GET['path']
    method = request.GET['method']
    # logging.warning(path)
    # logging.warning(method)
    # body = json.loads(request.body.decode())
    # logging.warning(body)
    # path = body['path']
    # method = body['method']
    token = gen_tokenV2(method=method, path=path)
    logging.warning(token)
    return token

@api.post('/token', auth=django_auth)
def genToken(request):
    body = json.loads(request.body.decode())
    logging.warning(body)
    path = body['path']
    method = body['method']
    token = gen_tokenV2(method=method, path=path)
    logging.warning(token)
    return token

@api.post('/feedback')
def feedback(request):
    # try:
    body = json.loads(request.body.decode())
    path = 'https://api.dev.educont.ru/api/v1/public/educational-courses/feedback'
    path = body['path']
    method = body['method']
    token = gen_tokenV2(method=method, path=path)
    feedback = requests.post(url=path, data=request.body, headers={ "Content-Type": "application/json", "Authorization": 'Bearer {0}'.format(token) })
    logging.warning(feedback)
    return {"success": True}
    # except:
    #     raise HttpResponseServerError()
# api.put("/me", auth=django_auth)
# def update_me(request):
#     try:
#         user = get_object_or_404(User, username=request.auth)
#         profile = get_object_or_404(Profile, user=user)
#         Profile.objects.update()
#     except:
#         return HttpResponseServerError()
