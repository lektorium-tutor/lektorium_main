from django import template
from django.utils.safestring import mark_safe
from lektorium_main.tilda.models import TildaArticle
from django.shortcuts import get_object_or_404
import logging
register = template.Library()

log = logging.getLogger(__name__)


@register.simple_tag
def tilda_scripts(course_id):
    article = get_object_or_404(TildaArticle, course_id=course_id)
    return mark_safe(article.prepare_scripts())


@register.simple_tag
def tilda_styles(course_id):
    article = get_object_or_404(TildaArticle, course_id=course_id)
    return mark_safe(article.prepare_styles(course_id))


@register.simple_tag
def tilda_content(course_id):
    article = get_object_or_404(TildaArticle, course_id=course_id)
    return mark_safe(article.prepare_content())