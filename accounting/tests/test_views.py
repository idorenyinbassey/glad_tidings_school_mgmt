from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import TuitionFee, Payment
from students.models import StudentProfile

class AccountingViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='teststaff',
            email='staff@test.com',
            password='testpass123',
            role='staff',
            is_staff=True
        )
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='student'
        )
        
        # Create a test student
        self.student = StudentProfile.objects.create(
            first_name='Test',
            last_name='Student',
            enrollment_id='ST001'
        )
        
        # Create some tuition fees
        self.tuition_fee1 = TuitionFee.objects.create(
            student=self.student,
            session='2025/2026',
            term='First',
            amount_due=Decimal('1000.00'),
            due_date='2025-09-01',
            created_by=self.admin_user
        )
        
        self.tuition_fee2 = TuitionFee.objects.create(
            student=self.student,
            session='2025/2026',
            term='Second',
            amount_due=Decimal('1000.00'),
            due_date='2026-01-15',
            created_by=self.admin_user
        )
        
        # Create a payment
        self.payment = Payment.objects.create(
            tuition_fee=self.tuition_fee1,
            amount=Decimal('750.00'),
            payment_date='2025-09-15',
            method='cash',
            receipt_number='REC001',
            created_by=self.admin_user
        )
        
        # Set up client
        self.client = Client()
    
    def test_accounting_home_access(self):
        """Test that only staff can access accounting home"""
        # Test unauthenticated access
        response = self.client.get(reverse('accounting:accounting_home'))
        self.assertRedirects(response, '/login/?next=/accounting/')
        
        # Test regular user access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounting:accounting_home'))
        self.assertEqual(response.status_code, 403)
        
        # Test staff user access
        self.client.login(username='teststaff', password='testpass123')
        response = self.client.get(reverse('accounting:accounting_home'))
        self.assertEqual(response.status_code, 200)
        
        # Test admin user access
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('accounting:accounting_home'))
        self.assertEqual(response.status_code, 200)
    
    def test_fees_view(self):
        """Test the fees view"""
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('accounting:fees'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounting/fees.html')
        
        # Test context data
        self.assertIn('fees', response.context)
        self.assertIn('payments', response.context)
        self.assertIn('total_due', response.context)
        self.assertIn('total_paid', response.context)
        
        # Test values
        self.assertEqual(response.context['total_due'], Decimal('2000.00'))
        self.assertEqual(response.context['total_paid'], Decimal('750.00'))
        self.assertEqual(response.context['unpaid_count'], 1)
        self.assertEqual(response.context['partial_count'], 1)
