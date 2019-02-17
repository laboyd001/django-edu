from django import template

register = template.Library()

@register.filter
def model_name(obj):
    '''model_name template filter.  It can be applied in templates as object|model_name to get the model name for an object
    '''

    try:
        return obj._meta.model_name
    except AttributeError:
        return None