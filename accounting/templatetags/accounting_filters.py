from django import template
from decimal import Decimal, InvalidOperation, DivisionByZero

register = template.Library()

@register.filter(name='div')
def div(value, arg):
    """Divide the value by the argument"""
    try:
        # Convert to Decimal for more precise financial calculations
        value_dec = Decimal(str(value))
        arg_dec = Decimal(str(arg))
        return value_dec / arg_dec if arg_dec else Decimal('0')
    except (InvalidOperation, DivisionByZero, TypeError):
        return Decimal('0')

@register.filter(name='mul')
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        # Convert to Decimal for more precise financial calculations
        value_dec = Decimal(str(value))
        arg_dec = Decimal(str(arg))
        return value_dec * arg_dec
    except (InvalidOperation, TypeError):
        return Decimal('0')

@register.filter(name='sub')
def sub(value, arg):
    """Subtract the argument from the value"""
    try:
        # Convert to Decimal for more precise financial calculations
        value_dec = Decimal(str(value))
        arg_dec = Decimal(str(arg))
        return value_dec - arg_dec
    except (InvalidOperation, TypeError):
        return Decimal('0')

@register.filter(name='percentage')
def percentage(value):
    """Format a value as a percentage"""
    try:
        value_dec = Decimal(str(value)) * Decimal('100')
        return f"{value_dec:.0f}%"
    except (InvalidOperation, TypeError):
        return "0%"

@register.filter(name='currency')
def currency(value):
    """Format a value as NGN currency"""
    try:
        value_dec = Decimal(str(value))
        return f"₦{value_dec:,.2f}"
    except (InvalidOperation, TypeError):
        return "₦0.00"
