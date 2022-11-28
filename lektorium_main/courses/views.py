import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.views.generic import View
from lms.djangoapps import branding
from openedx.features.course_experience.utils import get_course_outline_block_tree

# from lms.djangoapps.course_blocks.api import get_course_blocks
# from openedx.core.lib.courses import get_course_by_id

log = logging.getLogger(__name__)


class MatchingMaterialsView(View):
    """
    1. Получить все курсы
    2. Деркуть course_metadata (/api/course_home/course_metadata/{{ course_id }}?browser_timezone=Asia%2FYekaterinburg)
    2. Дернуть структуру курса едх (/api/course_home/outline/{{ course_id }})
    3. Разложить на объекты, привязать к объектам ЦОК, дополнить поля
    4. Придумать что делать при обновлении/повторном запуске матчинга.
    """

    template_name = "lektorium_main/materials.html"

    def get(self, request, *args, **kwargs):
        context = dict()
        courses = list()

        # Get courses

        courses_qs = branding.get_visible_courses(
        ).prefetch_related(
            'modes',
        ).select_related(
            'image_set'
        )
        for course_obj in courses_qs:
            course_outline = get_course_outline_block_tree(request, str(course_obj.id), request.user)
            blocks = json.dumps(dict(sorted(course_outline.items())),
                                sort_keys=False,
                                indent=2,
                                cls=DjangoJSONEncoder

                                )
            courses.append({
                'obj': course_obj,
                'blocks': blocks

            })

        context['courses'] = courses
        return render(request, self.template_name, context)
