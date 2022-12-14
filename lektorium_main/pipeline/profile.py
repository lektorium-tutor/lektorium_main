from lektorium_main.profile.models import (Profile, TeacherProfile, StudentProfile, EducationalInstitution, EducationalInstitutions)
from django.contrib.auth.models import User
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
        fields['profile_id'] = profile_id
        fields['EducationalInstitutions'] = educationalInstitutions
        fields['login'] = fields['login'].split('@')[0] or ''
        
        user.is_active = fields['isActive']
        fields['user'] = user
    
        if kwargs['is_new']:
            if not fields['EducationalInstitutions']:
                user.is_active = False  
            elif fields['EducationalInstitutions'][0]['approvedStatus'] != 'APPROVED' or fields['EducationalInstitutions'][0]['isActual'] == False:
                user.is_active = False
            else:
                edu_org = EducationalInstitution.objects.create(fields['EducationalInstitutions'][0]['educationalInstitution'])
                eud_orgs = EducationalInstitutions.objects.create(educationalInstitution=edu_org, approvedStatus=fields['EducationalInstitutions'][0]['approvedStatus'], isActual=fields['EducationalInstitutions'][0]['isActual']) 
            fields['EducationalInstitutions'] = eud_orgs
            user.save()
            if fields['role'] == 'STUDENT':
                fields['user'] = user
                StudentProfile.objects.create(**fields)
            elif fields['role'] == 'TEACHER':
                fields['user'] = user
                TeacherProfile.objects.create(**fields)
        else:
            if not fields['EducationalInstitutions']:
                user.is_active = False  
            elif fields['EducationalInstitutions'][0]['approvedStatus'] != 'APPROVED' or fields['EducationalInstitutions'][0]['isActual'] == False:
                user.is_active = False

            if fields['role'] == 'STUDENT':
                fields['user'] = user
                profile = StudentProfile.objects.get(user=user)
                edu_orgs = profile.educationalInstitutions_set
                edu_org = edu_orgs.educationalInstitution_set
                logging.warning(edu_org)
                profile.update(**fields)
            elif fields['role'] == 'TEACHER':
                fields['user'] = user
                profile = TeacherProfile.objects.get(user=user)
                profile.update(**fields)
