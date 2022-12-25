import logging

from lektorium_main.courses.models import COK, Course
from .models import EducontStatisticsItem

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

logger = logging.getLogger(__file__)


class EducontStatisticsMiddleware(MiddlewareMixin):

    def _get_profile(self, request):
        try:
            if request.user.is_active:
                return request.user.verified_profile_educont.first()
        except AttributeError:
            return None

    def _get_view_name(self, request):
        try:
            return request.view_name
        except AttributeError:
            return None

    def _write_stats(self, profile, externalId):
        content = Course.objects.get(externalId=externalId)
        EducontStatisticsItem.objects.create(
            statisticType='s',
            externalId=content.externalId,
            profileId=profile.id,
        )
        try:
            parent = content.externalParent
        except:
            parent = None
        if parent:
            self._write_stats(profile, content.externalParent.externalId)

    def process_response(self, request, response):
        profile = self._get_profile(request)
        view_name = self._get_view_name(request)
        if view_name == 'CourseHomeMetadataView':
            course = COK.objects.get(course_id=request.path.split('/')[-1])
            EducontStatisticsItem.objects.create(
                statisticType='s',
                externalId=course.externalId,
                profileId=profile.id,

            )
        elif view_name == 'render_xblock':
            content = Course.objects.get(externalId=request.path.split('@')[-1])
            self._write_stats(profile, content.externalId)

        return response
