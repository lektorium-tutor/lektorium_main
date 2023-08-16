"""
lektorium_main Django application initialization.
"""

from django.apps import AppConfig
from django.conf import settings

from edx_django_utils.plugins import PluginURLs

from .constants import ProjectType, SettingsType
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
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'lektorium_main',
                PluginURLs.RELATIVE_PATH: 'urls',
            }
        },
       'settings_config': {
            ProjectType.LMS: {
                SettingsType.PRODUCTION : { 'relative_path': 'settings' },
                SettingsType.COMMON: { 'relative_path': 'settings' },
                SettingsType.DEVSTACK: { 'relative_path': 'settings' },
            }
        }
    }

    def ready(self):
        if settings.FEATURES.get('ENABLE_LEKTORIUM_MAIN', False):
            self._enable_lek_main()

        # from .profile.tasks import listen_educont_sse
        # listen_educont_sse.delay()


    def _enable_lek_main(self):
        from lektorium_main import settings as auth_settings
        auth_settings.apply_settings(settings)

# class LEKTAdminConfig(apps.AdminConfig):
#     # default_site = 'umnoc.admin.UMNOCAdminSite'
#     name = 'lektorium_main.admin.LEKTAdminSite'
#     label = 'lekt_admin'
