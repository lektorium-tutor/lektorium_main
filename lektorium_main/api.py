import hashlib
import json
import logging

# from common.djangoapps.third_party_auth.models import get_setting
import jwt
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, ModelSchema
from ninja.orm import create_schema
from ninja.security import django_auth, HttpBearer
import datetime
from django.utils import timezone
import time

from lektorium_main.profile.models import Profile

api = NinjaAPI(csrf=True)


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return token


log = logging.getLogger(__name__)


def gen_token(request, path):
    timestamp = int(timezone.now().timestamp())
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
    timestamp = int(timezone.now().timestamp())
    timestamp = int(time.time())
    logging.warning(path)
    logging.warning(method)
    if method == "POST" or method == "PUT":
        requestHash = hashlib.md5(json.dumps(body).encode("utf-8")).hexdigest()
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


# class EducationalInstitutionSchema(Schema):
#     class Config:
#         model = EducationalInstitution

UserProfileSchema = create_schema(
    Profile,
    depth=2
    # fields=[
    #     'role',
    #     'isActive',
    #     'email'
    # ],
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

@api.get("/me", auth=django_auth, response={200: UserProfileSchema, 404: str})
def me(request):
    user = get_object_or_404(User, username=request.auth)
    profile = Profile.get_polymorph_profile(user)
    if profile:
        return 200, profile
    else:
        return 404, ""


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
    # path = 'https://api.dev.educont.ru/api/v1/public/educational-courses/educational-platforms/{0}?approved=true'.format(
    #     settings.SYSTEM_CODE_EDUCONT)
    path = 'https://api.dev.educont.ru/api/v1/public/sse/connect'
    token = gen_token(request=request, path=path)
    # test = requests.get(url=path, headers={"Content-Type": "text/event-stream", "Authorization": 'Bearer {0}'.format(token)})
    logging.warning(test)
    return token


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

def utcformat(dt, timespec='milliseconds'):
    """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SS.mmmZ)"""
    iso_str = dt.astimezone(datetime.timezone.utc).isoformat('T', timespec)
    return iso_str.replace('+00:00', 'Z')

@api.post('/feedback', auth=django_auth)
def feedback(request):
    # try:
    now = utcformat(datetime.datetime.now(tz=datetime.timezone.utc))
    logging.warning(datetime.datetime.now())
    body = json.loads(request.body.decode())
    path = 'https://api.dev.educont.ru/api/v1/public/educational-courses/feedback'
    method = "POST"
    user = get_object_or_404(User, username=request.auth)
    profile = Profile.get_polymorph_profile(user)
    if profile:
        body['profileId'] = str(profile.id)
        body['externalUserId'] = user.id
        body['createdAt'] = str(now)
        logging.warning(body)
        token = gen_tokenV2(method=method, path=path, body=body)
        response = requests.post(url=path, data=request.body, headers={ "Content-Type": "application/json", "Authorization": 'Bearer {0}'.format(token) })
        logging.warning(response.status_code)
        logging.warning(response.content)
        return {"status": response.status_code}
    else:
        return {"status": 404, "message": "Отсуствует связанный аккаунт Educont"}
