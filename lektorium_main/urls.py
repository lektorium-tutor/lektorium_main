"""
URLs for lektorium_main.
"""
from django.conf.urls import url
from django.urls import path, include  # pylint: disable=unused-import

from lektorium_main.admin import lekt_admin_site
from lektorium_main.api import api
from .courses.views import MatchingMaterialsView
from .profile.views import sse

app_name = "lektorium_main"

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    # url('^lekt-admin/', lekt_admin_site.urls),
    url('^api/', api.urls),
    # re_path(r'', TemplateView.as_view(template_name="lektorium_main/index.html")),
    path('matching', MatchingMaterialsView.as_view()),
    path('sse', sse),
]

urlpatterns += [
    path('lekt-admin/', lekt_admin_site.urls)
]