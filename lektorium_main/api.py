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

api = NinjaAPI(csrf=True)

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return token

log = logging.getLogger(__name__)
SYSTEM_CODE = "66a79e1f-0d24-46bf-9d77-a3af72e61384"
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
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
        "systemCode": SYSTEM_CODE
    }, PRIVATE_KEY, algorithm="RS256")
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
        profile = get_object_or_404(Profile, user=user)
        return profile
    except:
        return HttpResponseServerError()

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
    path ='https://api.dev.educont.ru/api/v1/public/educational-courses/educational-platforms/{0}?approved=true'.format(SYSTEM_CODE)
    path='https://api.dev.educont.ru/api/v1/public/sse/connect'
    token = gen_token(request=request, path=path)
    test = requests.get(url=path, headers={ "Content-Type": "text/event-stream", "Authorization": 'Bearer {0}'.format(token) })
    logging.warning(test)
    return test

@api.post('/feedback')
def feedback(request):
    # try:
    path = 'https://api.dev.educont.ru/api/v1/public/educational-courses/feedback'
    token = gen_token(request=request, path=path)
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