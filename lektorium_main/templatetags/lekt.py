from django import template

register = template.Library()  # pylint: disable=invalid-name


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
