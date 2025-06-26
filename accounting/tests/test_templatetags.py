from django import template
from django.test import TestCase
from decimal import Decimal
from ..templatetags.accounting_filters import div, mul, sub, percentage, currency

class AccountingFiltersTest(TestCase):
    def test_div_filter(self):
        """Test the division filter"""
        self.assertEqual(div(10, 2), Decimal('5'))
        self.assertEqual(div(0, 5), Decimal('0'))
        self.assertEqual(div(10, 0), Decimal('0'))  # Division by zero
        self.assertEqual(div('abc', 2), Decimal('0'))  # Invalid input
    
    def test_mul_filter(self):
        """Test the multiplication filter"""
        self.assertEqual(mul(10, 2), Decimal('20'))
        self.assertEqual(mul(0, 5), Decimal('0'))
        self.assertEqual(mul('abc', 2), Decimal('0'))  # Invalid input
    
    def test_sub_filter(self):
        """Test the subtraction filter"""
        self.assertEqual(sub(10, 2), Decimal('8'))
        self.assertEqual(sub(5, 10), Decimal('-5'))
        self.assertEqual(sub('abc', 2), Decimal('0'))  # Invalid input
    
    def test_percentage_filter(self):
        """Test the percentage filter"""
        self.assertEqual(percentage(0.75), "75%")
        self.assertEqual(percentage(1), "100%")
        self.assertEqual(percentage(0), "0%")
        self.assertEqual(percentage('abc'), "0%")  # Invalid input
    
    def test_currency_filter(self):
        """Test the currency filter"""
        self.assertEqual(currency(1234.56), "₦1,234.56")
        self.assertEqual(currency(0), "₦0.00")
        self.assertEqual(currency('abc'), "₦0.00")  # Invalid input
