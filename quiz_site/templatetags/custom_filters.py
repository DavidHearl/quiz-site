from django import template

register = template.Library()

@register.filter
def sum_values(dictionary):
    """Returns the sum of the dictionary's values"""
    return sum(dictionary.values())

@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key in dictionary"""
    return dictionary.get(key, 0)