"""
URLs for lektorium_main.
"""
from django.urls import path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from .courses.views import MatchingMaterialsView

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    path('', TemplateView.as_view(template_name="lektorium_main/index.html")),
    path('matching', MatchingMaterialsView.as_view()),
]
