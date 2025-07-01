#!/usr/bin/env python
"""
Test script to verify payment validation is working correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from accounting.models import TuitionFee, Payment
from django.core.exceptions import ValidationError

def test_payment_validation():
    print("Testing Payment Validation...")
    
    # Get a tuition fee with outstanding balance
    tuition = TuitionFee.objects.filter(status__in=['unpaid', 'partial']).first()
    
    if not tuition:
        print("❌ No tuition fees found with outstanding balance")
        return False
    
    print(f"✓ Found tuition fee: {tuition}")
    print(f"  Amount due: ₦{tuition.amount_due:,.2f}")
    print(f"  Amount paid: ₦{tuition.amount_paid:,.2f}")
    
    remaining = tuition.amount_due - tuition.amount_paid
    print(f"  Remaining balance: ₦{remaining:,.2f}")
    
    # Test 1: Valid payment (within remaining balance)
    print("\n--- Test 1: Valid Payment ---")
    valid_amount = remaining - 1000 if remaining > 1000 else remaining / 2
    payment = Payment(
        tuition_fee=tuition,
        amount=valid_amount,
        method='cash',
        reference='TEST_VALID'
    )
    
    try:
        payment.clean()
        print(f"✓ Valid payment of ₦{valid_amount:,.2f} passed validation")
    except ValidationError as e:
        print(f"❌ Valid payment failed validation: {e}")
        return False
    
    # Test 2: Invalid payment (exceeds remaining balance)
    print("\n--- Test 2: Invalid Payment (Exceeds Balance) ---")
    invalid_amount = remaining + 1000
    payment = Payment(
        tuition_fee=tuition,
        amount=invalid_amount,
        method='cash',
        reference='TEST_INVALID'
    )
    
    try:
        payment.clean()
        print(f"❌ Invalid payment of ₦{invalid_amount:,.2f} incorrectly passed validation")
        return False
    except ValidationError as e:
        print(f"✓ Invalid payment correctly caught: {e}")
    
    # Test 3: Zero/negative payment
    print("\n--- Test 3: Zero/Negative Payment ---")
    payment = Payment(
        tuition_fee=tuition,
        amount=0,
        method='cash',
        reference='TEST_ZERO'
    )
    
    try:
        payment.clean()
        print("❌ Zero payment incorrectly passed validation")
        return False
    except ValidationError as e:
        print(f"✓ Zero payment correctly caught: {e}")
    
    print("\n✅ All payment validation tests passed!")
    return True

if __name__ == '__main__':
    test_payment_validation()
