"""
lektorium_main Django application initialization.
"""

from django.apps import AppConfig
# from django.contrib.admin.apps import AdminConfig
# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from lektorium_main.profile.signals import create_user_profile, save_user_profile


class LektoriumMainConfig(AppConfig):
    """
    Configuration for the lektorium_main Django application.
    """

    name = 'lektorium_main'
    verbose_name = 'Lektorium main app'

    # def ready(self):
    #     post_save.connect(create_user_profile, sender=User)
    #     post_save.connect(save_user_profile, sender=User)

# class LEKTAdminConfig(AdminConfig):
#     # default_site = 'umnoc.admin.UMNOCAdminSite'
#     name = 'lektorium_main.courses.admin.LEKTAdminSite'
#     label = 'lekt_admin'
