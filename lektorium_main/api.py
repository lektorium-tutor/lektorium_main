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
from ninja import NinjaAPI, ModelSchema, Schema
from ninja.orm import create_schema
from ninja.security import django_auth, HttpBearer
import datetime
from django.utils import timezone
from typing import Optional
from lektorium_main.profile.models import Profile
log = logging.getLogger(__name__)

api = NinjaAPI(csrf=True)


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return token


log = logging.getLogger(__name__)


def gen_token(request, path):
    timestamp = int(timezone.now().timestamp())
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

UserProfileSchema = create_schema(
    Profile,
    depth=2
)
# class educationalInstitutionIn(Schema):
#     address: str= None
#     fullName: str= None
#     shortName: str= None
#     schoolName: str= None
#     locality: str= None
#     municipalArea: str= None

# class educationalInstitutionsIn(Schema):
#     isActual: bool = None
#     approvedStatus: str = None
#     educationalInstitution: educationalInstitutionIn = None

# class ProfileSchema(Schema):
#     fullName: str = None
#     isActive: bool = None
#     email: str = None
#     statusConfirmEmail: str = None
#     role: str = None
#     educationalInstitutions: Optional[educationalInstitutionsIn]

@api.get("/me", auth=django_auth, response=Optional[UserProfileSchema])
def me(request):
    user = get_object_or_404(User, username=request.auth)
    profile = Profile.get_polymorph_profile(user)
    if profile:
        return profile


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
    path = f'{settings.EDUCONT_BASE_URL}/api/v1/public/sse/connect'
    token = gen_token(request=request, path=path)
    # test = requests.get(url=path, headers={"Content-Type": "text/event-stream", "Authorization": 'Bearer {0}'.format(token)})
    return token


@api.get('/token')  # , auth=django_auth # TODO: construct some auth or limit this by local connections
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
    path = body['path']
    method = body['method']
    token = gen_tokenV2(method=method, path=path)
    return token

def utcformat(dt, tz, timespec='milliseconds'):
    """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SS.mmmZ)"""
    iso_str = dt.astimezone(tz).isoformat('T', timespec)
    return iso_str.replace('+03:00', 'Z')

@api.post('/feedback', auth=django_auth)
def feedback(request):
    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name="Europe/Moscow")
    now = utcformat(datetime.datetime.now(tz=tz), tz)
    body = json.loads(request.body.decode())
    path = f'{settings.EDUCONT_BASE_URL}/api/v1/public/educational-courses/feedback'
    method = "POST"
    user = get_object_or_404(User, username=request.auth)
    profile = Profile.get_polymorph_profile(user)
    if profile:
        body['profileId'] = str(profile.id)
        body['externalUserId'] = str(user.id)
        body['createdAt'] = str(now)
        token = gen_tokenV2(method=method, path=path, body=body)
        response = requests.post(url=path, json=body, headers={ "Content-Type": "application/json", "Authorization": 'Bearer {0}'.format(token) })
        log.warning(f"Response: {response.status_code}, {response.content}")
        return {"status": response.status_code}
    else:
        return {"status": 404, "message": "Отсуствует связанный аккаунт Educont"}

class SSEStatus(Schema):
    profile_id: str
    status: str

@api.post('/sse')  # TODO: create auth (mb remote user?)
def sse(request, sse_status: SSEStatus):
    profile = Profile.objects.get(id=sse_status.profile_id)
    status = sse_status.status
    if status == 'APPROVED':
        profile.approve()
    elif status == 'NOT_APPROVED':
        profile.disapprove()




