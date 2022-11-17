import logging
from ninja import NinjaAPI, ModelSchema
from ninja.security import django_auth
from django.contrib.auth.models import User
from .profile.models import (Profile, TeacherProfile, StudentProfile)

api = NinjaAPI(csrf=True)
log = logging.getLogger(__name__)


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['username', 'email', 'is_staff', 'is_active']


UserProfileSchema = create_schema(
    Profile,
    custom_fields=[
        ('user', UserSchema, None),
        # ('has_profile_image', bool, False),
        # ('age', int, None),
        # ('level_of_education_display', str, None),
        # ('gender_display', str, None),
        # ('country', Any, None)
    ]
)


@api.get("/me", auth=django_auth, response=UserProfileSchema)
def me(request):
    user = User.objects.get(username=request.auth)
    profile = Profile.objects.get(user=user)
    return profile
