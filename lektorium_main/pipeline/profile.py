from lektorium_main.profile.models import (Profile, TeacherProfile, StudentProfile)
import logging

STUDENT_PROFILE_FIELDS = ['user', 'role', 'isActive', 'statusConfirmEmail', 'login', 'fullName', 'name', 'surname',
                  'middleName',
                  'email']

TEACHER_PROFILE_FIELDS = ['user', 'role', 'isActive', 'statusConfirmEmail', 'login', 'fullName', 'name', 'surname',
                  'middleName',
                  'email']


def create(backend, user, response, *args, **kwargs):
    if backend.name == 'educont':
        logging.warning("Educont profile create or update")
        role = response.get('role')

        if role is None:
            logging.warning("Educont profile role is None")
            return

        if role == 'STUDENT':
            fields = dict(
                (name, kwargs.get(name, response.get(name))) for name in
                backend.setting('STUDENT_PROFILE_FIELDS', STUDENT_PROFILE_FIELDS))
        elif role == 'TEACHER':
            fields = dict(
                (name, kwargs.get(name, response.get(name))) for name in
                backend.setting('TEACHER_PROFILE_FIELDS', TEACHER_PROFILE_FIELDS))
        fields['login'] = fields['login'].split('@')[0] or ''
        fields['user'] = user
        if kwargs['is_new']:
            if fields['role'] == 'STUDENT':
                StudentProfile.objects.create(**fields)
            elif fields['role'] == 'TEACHER':
                TeacherProfile.objects.create(**fields)
        else:
            if fields['role'] == 'STUDENT':
                profile = StudentProfile.objects.get(user=user)
                profile.update(**fields)
            elif fields['role'] == 'TEACHER':
                profile = TeacherProfile.objects.get(user=user)
                profile.update(**fields)
