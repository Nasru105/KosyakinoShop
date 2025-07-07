from django import template

from utils.utils import phone_number_format

register = template.Library()


@register.simple_tag
def phone_number_format_tag(phone_number):
    return phone_number_format(phone_number)
