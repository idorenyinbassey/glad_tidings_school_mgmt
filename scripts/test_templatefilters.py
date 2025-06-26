#!/usr/bin/env python
import os
import sys
import django

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

# Now we can import from Django apps
from django.template import Template, Context
from django.template.loader import get_template

def test_template_filters():
    print("Testing custom template filters...")
    
    # Test loading the templatetags
    try:
        from accounting.templatetags import accounting_filters
        print("Successfully imported accounting_filters module")
        
        # Test each filter function directly
        print(f"div filter: 10 / 2 = {accounting_filters.div(10, 2)}")
        print(f"mul filter: 10 * 2 = {accounting_filters.mul(10, 2)}")
        print(f"sub filter: 10 - 2 = {accounting_filters.sub(10, 2)}")
        print(f"percentage filter: 0.75 = {accounting_filters.percentage(0.75)}")
        print(f"currency filter: 1234.56 = {accounting_filters.currency(1234.56)}")
        
        # Test in template context
        template_str = "{% load accounting_filters %}\n" + \
                      "Division: {{ 10|div:2 }}\n" + \
                      "Multiplication: {{ 10|mul:2 }}\n" + \
                      "Subtraction: {{ 10|sub:2 }}\n" + \
                      "Percentage: {{ 0.75|percentage }}\n" + \
                      "Currency: {{ 1234.56|currency }}"
                      
        template = Template(template_str)
        context = Context({})
        result = template.render(context)
        
        print("\nTemplate Rendering Result:")
        print(result)
        
        print("\nTrying to get the fees.html template...")
        fees_template = get_template('accounting/fees.html')
        print("Successfully loaded fees.html template")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_filters()
