from django import template

register = template.Library()

@register.filter
def dict_key(value, arg):
    """Returns the value from a dictionary for the given key"""
    return dict(value).get(arg, "")