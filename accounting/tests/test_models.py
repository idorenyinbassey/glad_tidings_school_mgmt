from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import TuitionFee, Payment
from students.models import StudentProfile

class TuitionFeeModelTest(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create a test student
        self.student = StudentProfile.objects.create(
            first_name='Test',
            last_name='Student',
            enrollment_id='ST001'
        )
        
        # Create a test tuition fee
        self.tuition_fee = TuitionFee.objects.create(
            student=self.student,
            session='2025/2026',
            term='First',
            amount_due=Decimal('1000.00'),
            due_date='2025-09-01',
            created_by=self.admin_user
        )
    
    def test_tuition_fee_creation(self):
        """Test the TuitionFee model"""
        self.assertEqual(self.tuition_fee.status, 'unpaid')
        self.assertEqual(self.tuition_fee.amount_paid, Decimal('0.00'))
        self.assertIsNone(self.tuition_fee.paid_date)
    
    def test_update_status(self):
        """Test the update_status method"""
        # Test partial payment
        self.tuition_fee.amount_paid = Decimal('500.00')
        self.tuition_fee.save()
        self.assertEqual(self.tuition_fee.status, 'partial')
        
        # Test full payment
        self.tuition_fee.amount_paid = Decimal('1000.00')
        self.tuition_fee.save()
        self.assertEqual(self.tuition_fee.status, 'paid')
        self.assertIsNotNone(self.tuition_fee.paid_date)
    
    def test_amount_outstanding(self):
        """Test the amount_outstanding property"""
        self.assertEqual(self.tuition_fee.amount_outstanding, Decimal('1000.00'))
        
        self.tuition_fee.amount_paid = Decimal('400.00')
        self.tuition_fee.save()
        self.assertEqual(self.tuition_fee.amount_outstanding, Decimal('600.00'))
    
    def test_payment_percentage(self):
        """Test the payment_percentage property"""
        self.assertEqual(self.tuition_fee.payment_percentage, 0)
        
        self.tuition_fee.amount_paid = Decimal('750.00')
        self.tuition_fee.save()
        self.assertEqual(self.tuition_fee.payment_percentage, 75)


class PaymentModelTest(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create a test student
        self.student = StudentProfile.objects.create(
            first_name='Test',
            last_name='Student',
            enrollment_id='ST001'
        )
        
        # Create a test tuition fee
        self.tuition_fee = TuitionFee.objects.create(
            student=self.student,
            session='2025/2026',
            term='First',
            amount_due=Decimal('1000.00'),
            due_date='2025-09-01',
            created_by=self.admin_user
        )
    
    def test_payment_creation(self):
        """Test the Payment model and its effect on TuitionFee"""
        payment = Payment.objects.create(
            tuition_fee=self.tuition_fee,
            amount=Decimal('500.00'),
            payment_date='2025-09-15',
            method='cash',
            receipt_number='REC001',
            created_by=self.admin_user
        )
        
        # Refresh tuition fee from database
        self.tuition_fee.refresh_from_db()
        
        # Check payment was created
        self.assertEqual(payment.amount, Decimal('500.00'))
        
        # Check tuition fee was updated
        self.assertEqual(self.tuition_fee.amount_paid, Decimal('500.00'))
        self.assertEqual(self.tuition_fee.status, 'partial')
