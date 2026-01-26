from django import template

register = template.Library()

@register.filter(name="get_item")
def get_item(d, key):
    if not d:
        return None
    return d.get(key)
