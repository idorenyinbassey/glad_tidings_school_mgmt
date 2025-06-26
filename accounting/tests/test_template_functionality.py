from django.test import TestCase
from django.template import Context, Template
from decimal import Decimal

class TemplateFunctionalityTest(TestCase):
    def test_loading_accounting_filters(self):
        """Test that accounting filters can be loaded and used in templates"""
        template_str = "{% load accounting_filters %}" \
                      "{{ value|div:divisor }}" \
                      "{{ value|mul:multiplier }}" \
                      "{{ value|sub:subtrahend }}" \
                      "{{ decimal_value|percentage }}" \
                      "{{ value|currency }}"
        
        context = Context({
            'value': 100,
            'divisor': 4,
            'multiplier': 3,
            'subtrahend': 10,
            'decimal_value': 0.75
        })
        
        template = Template(template_str)
        rendered = template.render(context)
        
        self.assertIn("25", rendered)  # div result
        self.assertIn("300", rendered)  # mul result
        self.assertIn("90", rendered)  # sub result
        self.assertIn("75%", rendered)  # percentage result
        self.assertIn("₦100.00", rendered)  # currency result
