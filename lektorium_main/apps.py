"""
lektorium_main Django application initialization.
"""

from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class LektoriumMainConfig(AppConfig):
    """
    Configuration for the lektorium_main Django application.
    """

    name = 'lektorium_main'
    verbose_name = 'Lektorium main app'


class LEKTAdminConfig(AdminConfig):
    # default_site = 'umnoc.admin.UMNOCAdminSite'
    name = 'lektorium_main.admin.LEKTAdminSite'
    label = 'lekt_admin'
