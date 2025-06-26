from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """Multiply the arg and value"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='div')
def div(value, arg):
    """Divide the value by the arg"""
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError):
        return 0

@register.filter(name='sub')
def sub(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='add')
def add(value, arg):
    """Add the arg to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0
