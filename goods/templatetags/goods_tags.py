from django import template
from django.utils.http import urlencode

from goods.models import Category

register = template.Library()


@register.simple_tag()
def tag_categories():
    return Category.objects.all()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
