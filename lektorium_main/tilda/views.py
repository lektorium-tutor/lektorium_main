import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie

from opaque_keys.edx.keys import CourseKey
from openedx_filters.learning.filters import CourseAboutRenderStarted
from pytz import UTC
from requests.exceptions import ConnectionError, Timeout  # pylint: disable=redefined-builtin
from xmodule.course_block import COURSE_VISIBILITY_PUBLIC, COURSE_VISIBILITY_PUBLIC_OUTLINE
from xmodule.modulestore.django import modulestore

from common.djangoapps.course_modes.models import CourseMode, get_course_prices
from common.djangoapps.edxmako.shortcuts import render_to_response

from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.util.cache import cache, cache_if_anonymous
from common.djangoapps.util.milestones_helpers import get_prerequisite_courses_display
from common.djangoapps.util.views import ensure_valid_course_key
from lms.djangoapps.commerce.utils import EcommerceService
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.access_utils import check_public_access
from lms.djangoapps.courseware.courses import (
    can_self_enroll_in_course,
    get_course_with_access,
    get_permission_for_course_about,
    get_studio_url,
)
from lms.djangoapps.courseware.exceptions import CourseAccessRedirect
from lms.djangoapps.courseware.permissions import MASQUERADE_AS_STUDENT, VIEW_COURSE_HOME, VIEW_COURSEWARE
from lms.djangoapps.courseware.toggles import course_is_invitation_only
from lms.djangoapps.instructor.enrollment import uses_shib
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.enrollments.permissions import ENROLL_IN_COURSE
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.features.course_experience import course_home_url
from openedx.features.course_experience.waffle import ENABLE_COURSE_ABOUT_SIDEBAR_HTML
from django.shortcuts import render

# from ..block_render import get_block, get_block_by_usage_id, get_block_for_descriptor
# from ..tabs import _get_dynamic_tabs
# from ..toggles import COURSEWARE_OPTIMIZED_RENDER_XBLOCK

log = logging.getLogger("edx.courseware")

from lektorium_main.tilda.models import TildaArticle
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from django.utils.translation import ugettext  as _tr

def _course_home_redirect_enabled():
    """
    Return True value if user needs to be redirected to course home based on value of
    `ENABLE_MKTG_SITE` and `ENABLE_COURSE_HOME_REDIRECT feature` flags
    Returns: boolean True or False
    """
    if configuration_helpers.get_value(
            'ENABLE_MKTG_SITE', settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    ) and configuration_helpers.get_value(
        'ENABLE_COURSE_HOME_REDIRECT', settings.FEATURES.get('ENABLE_COURSE_HOME_REDIRECT', True)
    ):
        return True

def registered_for_course(course, user):
    """
    Return True if user is registered for course, else False
    """
    if user is None:
        return False
    if user.is_authenticated:
        return CourseEnrollment.is_enrolled(user, course.id)
    else:
        return False

@ensure_csrf_cookie
@ensure_valid_course_key
@cache_if_anonymous()
def course_about(request, course_id):  # pylint: disable=too-many-statements
    """
    Display the course's about page.
    """
    course_key = CourseKey.from_string(course_id)

    # If a user is not able to enroll in a course then redirect
    # them away from the about page to the dashboard.
    if not can_self_enroll_in_course(course_key):
        return redirect(reverse('dashboard'))

    # If user needs to be redirected to course home then redirect
    if _course_home_redirect_enabled():
        return redirect(course_home_url(course_key))

    with modulestore().bulk_operations(course_key):
        permission = get_permission_for_course_about()
        course = get_course_with_access(request.user, permission, course_key)
        course_details = CourseDetails.populate(course)
        modes = CourseMode.modes_for_course_dict(course_key)
        registered = registered_for_course(course, request.user)

        staff_access = bool(has_access(request.user, 'staff', course))
        studio_url = get_studio_url(course, 'settings/details')

        if request.user.has_perm(VIEW_COURSE_HOME, course):
            course_target = course_home_url(course.id)
        else:
            course_target = reverse('about_course', args=[str(course.id)])

        show_courseware_link = bool(
            (
                request.user.has_perm(VIEW_COURSEWARE, course)
            ) or settings.FEATURES.get('ENABLE_LMS_MIGRATION')
        )

        # If the ecommerce checkout flow is enabled and the mode of the course is
        # professional or no id professional, we construct links for the enrollment
        # button to add the course to the ecommerce basket.
        ecomm_service = EcommerceService()
        ecommerce_checkout = ecomm_service.is_enabled(request.user)
        ecommerce_checkout_link = ''
        ecommerce_bulk_checkout_link = ''
        single_paid_mode = None
        if ecommerce_checkout:
            if len(modes) == 1 and list(modes.values())[0].min_price:
                single_paid_mode = list(modes.values())[0]
            else:
                # have professional ignore other modes for historical reasons
                single_paid_mode = modes.get(CourseMode.PROFESSIONAL)

            if single_paid_mode and single_paid_mode.sku:
                ecommerce_checkout_link = ecomm_service.get_checkout_page_url(single_paid_mode.sku)
            if single_paid_mode and single_paid_mode.bulk_sku:
                ecommerce_bulk_checkout_link = ecomm_service.get_checkout_page_url(single_paid_mode.bulk_sku)

        registration_price, course_price = get_course_prices(course)  # lint-amnesty, pylint: disable=unused-variable

        # Used to provide context to message to student if enrollment not allowed
        can_enroll = bool(request.user.has_perm(ENROLL_IN_COURSE, course))
        invitation_only = course_is_invitation_only(course)
        is_course_full = CourseEnrollment.objects.is_course_full(course)

        # Register button should be disabled if one of the following is true:
        # - Student is already registered for course
        # - Course is already full
        # - Student cannot enroll in course
        active_reg_button = not (registered or is_course_full or not can_enroll)

        is_shib_course = uses_shib(course)

        # get prerequisite courses display names
        pre_requisite_courses = get_prerequisite_courses_display(course)

        # Overview
        overview = CourseOverview.get_from_id(course.id)

        sidebar_html_enabled = ENABLE_COURSE_ABOUT_SIDEBAR_HTML.is_enabled()

        allow_anonymous = check_public_access(course, [COURSE_VISIBILITY_PUBLIC, COURSE_VISIBILITY_PUBLIC_OUTLINE])

        article = TildaArticle.get_latest_object(course_id=course.id)
        tilda_page = article.get_page()
        # soup = BeautifulSoup(tilda_page, 'html.parser')
        
        context = {
            'course': course,
            'course_details': course_details,
            'staff_access': staff_access,
            'studio_url': studio_url,
            'registered': registered,
            'course_target': course_target,
            'is_cosmetic_price_enabled': settings.FEATURES.get('ENABLE_COSMETIC_DISPLAY_PRICE'),
            'course_price': course_price,
            'ecommerce_checkout': ecommerce_checkout,
            'ecommerce_checkout_link': ecommerce_checkout_link,
            'ecommerce_bulk_checkout_link': ecommerce_bulk_checkout_link,
            'single_paid_mode': single_paid_mode,
            'show_courseware_link': show_courseware_link,
            'is_course_full': is_course_full,
            'can_enroll': can_enroll,
            'invitation_only': invitation_only,
            'active_reg_button': active_reg_button,
            'is_shib_course': is_shib_course,
            # We do not want to display the internal courseware header, which is used when the course is found in the
            # context. This value is therefore explicitly set to render the appropriate header.
            'disable_courseware_header': True,
            'pre_requisite_courses': pre_requisite_courses,
            'course_image_urls': overview.image_urls,
            'sidebar_html_enabled': sidebar_html_enabled,
            'allow_anonymous': allow_anonymous,
            'disable_footer': True,
            'tilda_page': tilda_page
        }
        
        course_about_template = 'lektorium_main/course_about_tilda.html'
        # try:
        #     # .. filter_implemented_name: CourseAboutRenderStarted
        #     # .. filter_type: org.openedx.learning.course_about.render.started.v1
        #     context, course_about_template = CourseAboutRenderStarted.run_filter(
        #         context=context, template_name=course_about_template,
        #     )
        # except CourseAboutRenderStarted.RenderInvalidCourseAbout as exc:
        #     response = render(request, exc.course_about_template, exc.template_context)
        # except CourseAboutRenderStarted.RedirectToPage as exc:
        #     raise CourseAccessRedirect(exc.redirect_to or reverse('dashboard')) from exc
        # except CourseAboutRenderStarted.RenderCustomResponse as exc:
        #     response = exc.response or render(request, course_about_template, context)
        # else:
        response = render(request, course_about_template, context)

        return response
