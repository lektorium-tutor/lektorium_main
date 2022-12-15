from lektorium_main.profile.models import (Profile, TeacherProfile, StudentProfile, EducationalInstitution, EducationalInstitutions)
from django.contrib.auth.models import User
import logging

STUDENT_PROFILE_FIELDS = ['id', 'user', 'role', 'isActive', 'statusConfirmEmail', 'login', 'fullName', 'name', 'surname',
                  'middleName',
                  'email']

TEACHER_PROFILE_FIELDS = ['id', 'user', 'role', 'isActive', 'statusConfirmEmail', 'login', 'fullName', 'name', 'surname',
                  'middleName',
                  'email']


def create(backend, user, response, *args, **kwargs):
    if backend.name == 'educont':
        logging.warning("Educont profile create or update")
        role = response.get('role')
        profile_id = response.get('id')
        educationalInstitutions = response.get('educationalInstitutions')

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
        user.is_active = False
        user.save()
        fields['user'] = user
        fields['profile_id'] = profile_id
        fields['login'] = fields['login'].split('@')[0] or ''
        if educationalInstitutions:
            edu_org, created_org = EducationalInstitution.objects.update_or_create(defaults={**educationalInstitutions[0]['educationalInstitution']}, id=educationalInstitutions[0]['educationalInstitution']['id'])
            edu_orgs, created_orgs = EducationalInstitutions.objects.update_or_create(educationalInstitution=edu_org, approvedStatus=educationalInstitutions[0]['approvedStatus'], isActual=educationalInstitutions[0]['isActual']) 
            fields['educationalInstitutions'] = edu_orgs

        if fields['role'] == 'STUDENT':
            StudentProfile.objects.update_or_create(defaults={**fields}, user=user )
        elif fields['role'] == 'TEACHER':
            TeacherProfile.objects.update_or_create(defaults={**fields}, user=user )
        
