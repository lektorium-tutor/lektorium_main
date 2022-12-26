import logging

from completion.models import BlockCompletion
from xmodule.modulestore.django import modulestore

from lektorium_main.courses.models import COK, Course
from .models import EducontStatisticsItem

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

logger = logging.getLogger('EducontStatisticsMiddleware')


class EducontStatisticsMiddleware(MiddlewareMixin):

    def _get_profile(self, request):
        if request.user:
            user = request.user
            if user.is_active and hasattr(user, 'verified_profile_educont'):
                logger.warning(f'User: {user}, profile: {user.verified_profile_educont}')
                return user.verified_profile_educont
        return None
        # try:
        #     if request.user.is_active:
        #         return request.user.verified_profile_educont.first()
        # except AttributeError:
        #     return None

    def _get_view_name(self, request):
        try:
            logger.warning(f'View name: {request.view_name}')
            return request.view_name
        except AttributeError:
            return None

    def _write_stats(self, profile, content):
        status = False
        parent = None
        if content.courseTypeId == 3:
            ms = modulestore()
            vertical = ms.get_item(content.block_key, depth=2)
            completion = sum(BlockCompletion.objects.filter(
                user=profile.user,
                block_key__in=[child.location for child in vertical.get_children()]
            ).values_list('completion', flat=True))
            status = (completion >= len(vertical.get_children()))

        EducontStatisticsItem.objects.create(
            statisticType='s',
            externalId=content.externalId,
            profileId=profile.profile_id,
            status=status if status else None
        )
        if hasattr(content, 'externalParent'):
            parent = content.externalParent

        if parent:
            self._write_stats(profile, parent)

    def process_response(self, request, response):
        profile = self._get_profile(request)

        if not profile:
            return response

        view_name = self._get_view_name(request)
        if view_name == 'CourseHomeMetadataView':  # TODO: move to _write_stats
            course = COK.objects.get(course_id=request.path.split('/')[-1])
            EducontStatisticsItem.objects.create(
                statisticType='s',
                externalId=course.externalId,
                profileId=profile.profile_id,

            )
        elif view_name in ('render_xblock', 'handle_xblock_callback'):
            logger.warning(f'REQUEST_PATH: {request}')
            try:
                content = Course.objects.get(externalId=request.path.split('@')[-1])
            except Course.DoesNotExist:
                content = None
                logger.warning(f'EDUCONT content with externalId={request.path.split("@")[-1]} does not exist')
            if content:
                self._write_stats(profile, content)

        return response
