from lektorium_main.profile.models import (Profile, TeacherProfile, StudentProfile)


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'educont':
        role = response.get('role')
        data = {
            'isActive': response.get('isActive'),
            'role': response.get('role'),
            'statusConfirmEmail': response.get('statusConfirmEmail'),
            'nickname': response.get('login').split('@')[0] or '',
            'fullname': response.get('fullName'),
            'name': response.get('name'),
            'surname': response.get('surname'),
            'middleName': response.get('middleName'),
            'email': response.get('email')
        }
        try:
            profile = Profile.objects.get(user=user.id)
        except:
            profile = None
        if profile is None:
            if role == 'STUDENT':
                data['user'] = user.id
                profile = StudentProfile.objects.create(data)
            else:
                data['user'] = user.id
                profile = TeacherProfile.objects.create(data)
        profile.save()