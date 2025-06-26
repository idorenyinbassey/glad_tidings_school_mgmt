from django.test import TestCase
from django.urls import reverse, resolve
from .. import views

class AccountingUrlsTest(TestCase):
    def test_accounting_home_url(self):
        """Test the accounting home URL"""
        url = reverse('accounting:accounting_home')
        self.assertEqual(url, '/accounting/')
        self.assertEqual(resolve(url).func, views.accounting_home)
    
    def test_fees_url(self):
        """Test the fees URL"""
        url = reverse('accounting:fees')
        self.assertEqual(url, '/accounting/fees/')
        self.assertEqual(resolve(url).func, views.fees)
    
    def test_reports_url(self):
        """Test the reports URL"""
        url = reverse('accounting:reports')
        self.assertEqual(url, '/accounting/reports/')
        self.assertEqual(resolve(url).func, views.reports)
