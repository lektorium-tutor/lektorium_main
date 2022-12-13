from lektorium_main.profile.models import (Profile, TeacherProfile, StudentProfile)
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import logging

PROFILE_FIELDS = ['user', 'role', 'isActive', 'statusConfirmEmail', 'login', 'fullName', 'name', 'surname', 'middleName',
                  'email']


def create(backend, user, response, *args, **kwargs):
    if backend.name == 'educont':
        logging.warning("Educont profile create or pass")
        fields = dict(
            (name, kwargs.get(name, response.get(name))) for name in backend.setting('PROFILE_FIELDS', PROFILE_FIELDS))
        fields['login'] = fields['login'].split('@')[0] or ''
        fields['user'] = user
        if kwargs['is_new']:
            if fields['role'] == 'STUDENT':
                StudentProfile.objects.create(**fields)
            elif fields['role'] == 'TEACHER':
                TeacherProfile.objects.create(**fields)

def update(backend, user, response, *args, **kwargs):
    if backend.name == 'educont':
        logging.warning("Educont profile update")
        fields = dict(
            (name, kwargs.get(name, response.get(name))) for name in backend.setting('PROFILE_FIELDS', PROFILE_FIELDS))
        fields['login'] = fields['login'].split('@')[0] or ''
        fields['user'] = user
        if kwargs['is_new'] is False:
            if fields['role'] == 'STUDENT':
                profile = StudentProfile.objects.get(user=user)
                profile.update(**fields)
            elif fields['role'] == 'TEACHER':
                profile = TeacherProfile.objects.get(user=user)
                profile.update(**fields)
