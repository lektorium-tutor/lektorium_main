import logging
from openedx_filters import PipelineStep
from openedx_filters.learning.filters import CourseAboutRenderStarted
from web_fragments.fragment import Fragment
from django.template import Context, Template
from lektorium_main.tilda.models import TildaArticle
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from django.utils.translation import ugettext  as _tr
from django.shortcuts import render
import crum

log = logging.getLogger("edx.courseware")

class RenderAlternativeCourseAbout(PipelineStep):
    """
    Stop course about render raising RenderCustomResponse exception.

    Example usage:

    Add the following configurations to your configuration file:

        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.course_about.render.started.v1": {
                "fail_silently": False,
                "pipeline": [
                    "lektorium_main.tilda.pipeline.RenderAlternativeCourseAbout"
                ]
            }
        }
    """

    def run_filter(
        self, context, template_name
    ):  # pylint: disable=unused-argument, arguments-differ
        """Execute filter that modifies the instructor dashboard context.

        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
            
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
            'tilda_page': result_page,
            'disable_footer': True
        }
        """
        request = crum.get_current_request()
        registered = context['registered']
        show_courseware_link = context['show_courseware_link']
        course_target = context['course_target']
        is_course_full = context['is_course_full']
        invitation_only = context['invitation_only']
        can_enroll = context['can_enroll']
        is_shib_course = context['is_shib_course']
        allow_anonymous = context['allow_anonymous']
        course = context['course']
        context['disable_courseware_header'] = False
        article = TildaArticle.get_latest_object(course_id=course.id)
        if not article:
            raise CourseAboutRenderStarted.RenderInvalidCourseAbout(message="Tilda Article not found", course_about_template='static_templates/404.html')
        elif article:
            tilda_page = article.get_page()
            soup = BeautifulSoup(tilda_page, 'html.parser')
            
            parent_tag = soup.find("div", {"class": "tilda_course_about_button"})
            general_tag = parent_tag.div
            if registered:
                if show_courseware_link:
                    new_tag = soup.new_tag('a', attrs={'href': course_target, 'class': 'tn-atom'})
                    new_tag.string = _tr("View Course")
                    general_tag.replaceWith(new_tag)
            elif is_course_full:
                new_tag = soup.new_tag('span', attrs={'class': 'register disabled tn-atom'})
                new_tag.string = _tr("Course is full")
                general_tag.replaceWith(new_tag)
            elif invitation_only and not can_enroll:
                new_tag = soup.new_tag('span', attrs={'class': 'register disabled tn-atom'})
                new_tag.string = _tr("Enrollment in this course is by invitation only")          
                general_tag.replaceWith(new_tag)
            elif not is_shib_course and not can_enroll:
                new_tag = soup.new_tag('span', attrs={'class': 'register disabled tn-atom'})
                new_tag.string = _tr("Enrollment is Closed")
                general_tag.replaceWith(new_tag)
            elif allow_anonymous:
                if show_courseware_link:
                    new_tag = soup.new_tag('a', attrs={'href': course_target, 'class': 'tn-atom'})
                    new_tag.string = _tr("View Course")
                    general_tag.replaceWith(new_tag)
            else:
                new_tag = soup.new_tag('a', attrs={'href': '#', 'class': "register tn-atom"})
                new_tag.string = _tr("Enroll now")
                register_error = soup.new_tag('div', id='register_error')
                general_tag.replaceWith(new_tag)
                new_tag.insert_after(register_error)
            result_page = soup.prettify( formatter="html" )
            context['disable_footer'] = True
            context['result_page'] = result_page
            # template = Template(result_page)
            # html = template.render(Context(context))
            # frag = Fragment(result_page)
            template_name = 'lektorium_main/course_about_tilda_v2.html'
            template = Template(template_name)
            html = template.render(Context(context))
            # frag.add_css(self.resource_string("static/css/ontask.css"))
            return {"context": context, "template_name": html }