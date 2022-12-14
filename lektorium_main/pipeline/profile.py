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
        logging.warning(response)
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
        fields['profile_id'] = profile_id
        fields['login'] = fields['login'].split('@')[0] or ''
        
        user.is_active = fields['isActive']
        logging.warning(dir(user))
        if not StudentProfile.objects.filter(user=user).exists() and not TeacherProfile.objects.filter(user=user).exists():
            if not educationalInstitutions:
                user.is_active = False  
            elif educationalInstitutions[0]['approvedStatus'] != 'APPROVED' or educationalInstitutions[0]['isActual'] == False:
                user.is_active = False
            else:
                edu_org = EducationalInstitution.objects.update_or_create(**educationalInstitutions[0]['educationalInstitution'])
                edu_orgs = EducationalInstitutions.objects.update_or_create(educationalInstitution=edu_org, approvedStatus=educationalInstitutions[0]['approvedStatus'], isActual=educationalInstitutions[0]['isActual']) 
                educationalInstitutions = edu_orgs

            user.save()
            fields['user'] = user
            if fields['role'] == 'STUDENT':
                StudentProfile.objects.create(**fields)
            elif fields['role'] == 'TEACHER':
                TeacherProfile.objects.create(**fields)
        else:
            if not educationalInstitutions:
                user.is_active = False  
            elif educationalInstitutions[0]['approvedStatus'] != 'APPROVED' or educationalInstitutions[0]['isActual'] == False:
                user.is_active = False
            else:
                edu_org = EducationalInstitution.objects.update_or_create(educationalInstitutions[0]['educationalInstitution'])
                edu_orgs = EducationalInstitutions.objects.update_or_create(educationalInstitution=edu_org, approvedStatus=educationalInstitutions[0]['approvedStatus'], isActual=educationalInstitutions[0]['isActual']) 
                educationalInstitutions = edu_orgs

            # user.save()
                # edu_orgs = profile.educationalInstitutions_set
                # edu_org = edu_orgs.educationalInstitution_set
                # logging.warning(edu_org)
            if fields['role'] == 'STUDENT':
                fields['user'] = user
                profile = StudentProfile.objects.get(user=user)
                profile.update(**fields)
            elif fields['role'] == 'TEACHER':
                fields['user'] = user
                profile = TeacherProfile.objects.get(user=user)
                profile.update(**fields)
        # logging.warning(user.is_active)
        # user.save()
