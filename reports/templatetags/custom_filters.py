from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Access a dictionary by key."""
    return dictionary.get(key)



@register.filter
def percentage(value):
    """Converts a decimal value to a percentage"""
    try:
        return f"{value * 100:.2f}%" if value is not None else ""
    except (ValueError, TypeError):
        return ""
