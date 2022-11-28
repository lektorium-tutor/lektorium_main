"""
URLs for lektorium_main.
"""
from django.urls import path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import
from django.conf.urls import url, include

from lektorium_main.api import api
from lektorium_main.courses.admin import lekt_admin_site

from .courses.views import MatchingMaterialsView

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    url('^admin/', lekt_admin_site.urls),
    url('^api/', api.urls),
    # re_path(r'', TemplateView.as_view(template_name="lektorium_main/index.html")),
    path('matching', MatchingMaterialsView.as_view()),
]
