#!/usr/bin/env python
import os
import sys
import django

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.template.loader import render_to_string
from accounting.views import fees

def test_fees_template():
    print("Testing fees template directly...")
    
    # Create context data similar to what the view would provide
    context = {
        'total_due': 1000.0,
        'total_paid': 750.0,
        'unpaid_count': 10,
        'partial_count': 5,
        'paid_count': 20,
        'outstanding': 250.0,
        'fees': [],
        'payments': []
    }
    
    try:
        # Try to render the template with the context data
        rendered = render_to_string('accounting/fees.html', context)
        print("Template rendered successfully!")
        # Print a small part of the rendered template to confirm it worked
        print(rendered[:200] + "...")
        return True
    except Exception as e:
        print(f"Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fees_template()
    if success:
        print("\nTemplate test passed! The template filters appear to be working correctly.")
    else:
        print("\nTemplate test failed. The template filters may not be registered correctly.")
