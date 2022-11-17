"""
URLs for lektorium_main.
"""
from django.urls import re_path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import
from django.conf.urls import url, include

from .api import api
from .admin import lekt_admin_site

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    url('^admin/', lekt_admin_site.urls),
    url('^api/', api.urls),
    # re_path(r'', TemplateView.as_view(template_name="lektorium_main/index.html")),
]
