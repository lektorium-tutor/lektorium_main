import logging
from ninja import NinjaAPI, Schema, ModelSchema
from ninja.security import django_auth
from django.contrib.auth.models import User
from lektorium_main.profile.models import Profile, TeacherProfile, StudentProfile
from ninja.orm import create_schema
from django.shortcuts import get_object_or_404

api = NinjaAPI(csrf=True)
log = logging.getLogger(__name__)


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
    user = User.objects.get(username=request.auth)
    profile = Profile.objects.get(user=user)
    return profile

@api.delete("/profiles/{profile_id}", auth=django_auth)
def delete_profile(request, profile_id: str):
    profile = get_object_or_404(Profile, id=profile_id)
    profile.delete()
    return {"success": True}
