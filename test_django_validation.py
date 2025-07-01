#!/usr/bin/env python
"""
Simple test to verify Django admin payment validation
"""
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')

try:
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    exit(1)

# Import models
try:
    from accounting.models import TuitionFee, Payment
    from accounting.admin import PaymentAdminForm
    from django.core.exceptions import ValidationError
    from django import forms
    print("✓ Models and forms imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_admin_form_validation():
    """Test the admin form validation"""
    print("\n--- Testing Admin Form Validation ---")
    
    # Get a tuition fee with outstanding balance
    try:
        tuition = TuitionFee.objects.filter(status__in=['unpaid', 'partial']).first()
        if not tuition:
            print("❌ No tuition fees found with outstanding balance")
            return False
        
        print(f"✓ Using tuition fee: {tuition}")
        remaining = tuition.amount_due - tuition.amount_paid
        print(f"  Remaining balance: ₦{remaining:,.2f}")
        
        # Test 1: Valid form data
        print("\n--- Test 1: Valid Form Data ---")
        valid_amount = remaining / 2 if remaining > 0 else 1000
        form_data = {
            'tuition_fee': tuition.id,
            'amount': valid_amount,
            'payment_date': '2025-07-01',
            'method': 'cash',
            'reference': 'TEST123'
        }
        
        form = PaymentAdminForm(data=form_data)
        if form.is_valid():
            print(f"✓ Valid form with ₦{valid_amount:,.2f} passed validation")
        else:
            print(f"❌ Valid form failed validation: {form.errors}")
            return False
        
        # Test 2: Invalid form data (exceeds balance)
        print("\n--- Test 2: Invalid Form Data (Exceeds Balance) ---")
        invalid_amount = remaining + 1000
        form_data['amount'] = invalid_amount
        
        form = PaymentAdminForm(data=form_data)
        if form.is_valid():
            print(f"❌ Invalid form with ₦{invalid_amount:,.2f} incorrectly passed validation")
            return False
        else:
            print(f"✓ Invalid form correctly failed validation: {form.errors}")
        
        # Test 3: Zero amount
        print("\n--- Test 3: Zero Amount ---")
        form_data['amount'] = 0
        
        form = PaymentAdminForm(data=form_data)
        if form.is_valid():
            print("❌ Zero amount form incorrectly passed validation")
            return False
        else:
            print(f"✓ Zero amount form correctly failed validation: {form.errors}")
        
        print("\n✅ All admin form validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_validation():
    """Test the model validation"""
    print("\n--- Testing Model Validation ---")
    
    try:
        tuition = TuitionFee.objects.filter(status__in=['unpaid', 'partial']).first()
        if not tuition:
            print("❌ No tuition fees found with outstanding balance")
            return False
        
        remaining = tuition.amount_due - tuition.amount_paid
        
        # Test model validation with excessive payment
        excessive_amount = remaining + 1000
        payment = Payment(
            tuition_fee=tuition,
            amount=excessive_amount,
            method='cash',
            reference='TEST_MODEL'
        )
        
        try:
            payment.full_clean()
            print(f"❌ Model validation incorrectly passed for ₦{excessive_amount:,.2f}")
            return False
        except ValidationError as e:
            print(f"✓ Model validation correctly caught excessive payment: {e}")
            return True
        
    except Exception as e:
        print(f"❌ Model test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Django Payment Validation Test ===")
    
    model_test = test_model_validation()
    admin_test = test_admin_form_validation()
    
    if model_test and admin_test:
        print("\n🎉 All tests passed! Payment validation is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
