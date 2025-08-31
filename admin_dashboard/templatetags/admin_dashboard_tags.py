from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value, total):
    if total == 0:
        return 0
    return round((value / total) * 100)
