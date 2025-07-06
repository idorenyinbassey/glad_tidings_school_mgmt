"""
Financial report generation utilities
"""
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
import json
from .models import TuitionFee, Payment, Expense, Payroll


class ReportGenerator:
    """Generate different types of financial reports"""
    
    def __init__(self, start_date, end_date, period_name):
        self.start_date = start_date
        self.end_date = end_date
        self.period_name = period_name
    
    def _format_decimal(self, value):
        """Format decimal values consistently and return as float for JSON serialization"""
        if value is None:
            return 0.00
        decimal_value = Decimal(str(value)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return float(decimal_value)
    
    def generate_income_statement(self):
        """Generate income statement data"""
        try:
            # Revenue calculations using the correct field name 'payment_date'
            total_revenue = Payment.objects.filter(
                payment_date__gte=self.start_date,
                payment_date__lte=self.end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            print(f"Debug: Found {Payment.objects.filter(payment_date__gte=self.start_date, payment_date__lte=self.end_date).count()} payments")
            print(f"Debug: Total revenue: {total_revenue}")
            
            # Revenue breakdown by method
            revenue_by_method = list(Payment.objects.filter(
                payment_date__gte=self.start_date,
                payment_date__lte=self.end_date
            ).values('method').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total'))
            
            # Convert revenue_by_method amounts to float
            for item in revenue_by_method:
                if 'total' in item and item['total']:
                    item['total'] = float(item['total'])
            
            # Expense calculations by category
            expense_categories = {}
            categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
            total_expenses = 0.0
            
            for category in categories:
                amount = Expense.objects.filter(
                    date__gte=self.start_date,
                    date__lte=self.end_date,
                    category=category
                ).aggregate(total=Sum('amount'))['total'] or 0
                expense_categories[category] = self._format_decimal(amount)
                total_expenses += expense_categories[category]
            
            print(f"Debug: Total expenses: {total_expenses}")
            
            # Net income calculation
            net_income = self._format_decimal(total_revenue) - total_expenses
            
            # Profit margin calculation
            profit_margin = (net_income / self._format_decimal(total_revenue) * 100) if total_revenue > 0 else 0
            
            return {
                'report_type': 'income_statement',
                'period_name': self.period_name,
                'total_revenue': self._format_decimal(total_revenue),
                'revenue_by_method': revenue_by_method,
                'expense_categories': expense_categories,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'profit_margin': self._format_decimal(profit_margin),
                'generated_at': timezone.now().isoformat()
            }
        except Exception as e:
            print(f"Error in generate_income_statement: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def generate_balance_sheet(self):
        """Generate balance sheet data"""
        # Assets
        cash_on_hand = Payment.objects.filter(
            payment_date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        accounts_receivable = TuitionFee.objects.filter(
            status__in=['unpaid', 'partial']
        ).aggregate(
            total_due=Sum('amount_due'),
            total_paid=Sum('amount_paid')
        )
        
        outstanding_receivables = self._format_decimal(
            (accounts_receivable['total_due'] or 0) - 
            (accounts_receivable['total_paid'] or 0)
        )
        
        total_assets = self._format_decimal(cash_on_hand) + outstanding_receivables
        
        # Liabilities
        unpaid_payroll = Payroll.objects.filter(
            paid=False
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_liabilities = self._format_decimal(unpaid_payroll)
        
        # Equity
        net_equity = total_assets - total_liabilities
        
        return {
            'report_type': 'balance_sheet',
            'period_name': self.period_name,
            'assets': {
                'cash_on_hand': self._format_decimal(cash_on_hand),
                'accounts_receivable': outstanding_receivables,
                'total_assets': total_assets
            },
            'liabilities': {
                'unpaid_payroll': self._format_decimal(unpaid_payroll),
                'total_liabilities': total_liabilities
            },
            'equity': {
                'net_equity': net_equity
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def generate_cash_flow(self):
        """Generate cash flow statement data"""
        # Operating Activities
        cash_from_operations = Payment.objects.filter(
            payment_date__gte=self.start_date,
            payment_date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        cash_for_expenses = Expense.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        cash_for_payroll = Payroll.objects.filter(
            paid=True,
            paid_date__gte=self.start_date,
            paid_date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        net_operating_cash = (
            self._format_decimal(cash_from_operations) - 
            self._format_decimal(cash_for_expenses) - 
            self._format_decimal(cash_for_payroll)
        )
        
        return {
            'report_type': 'cash_flow',
            'period_name': self.period_name,
            'operating_activities': {
                'cash_from_operations': self._format_decimal(cash_from_operations),
                'cash_for_expenses': self._format_decimal(cash_for_expenses),
                'cash_for_payroll': self._format_decimal(cash_for_payroll),
                'net_operating_cash': net_operating_cash
            },
            'investing_activities': {
                'equipment_purchases': 0.00,  # Changed from Decimal to float
                'net_investing_cash': 0.00  # Changed from Decimal to float
            },
            'financing_activities': {
                'loans_received': 0.00,  # Changed from Decimal to float
                'net_financing_cash': 0.00  # Changed from Decimal to float
            },
            'net_change_in_cash': net_operating_cash,
            'generated_at': timezone.now().isoformat()
        }
    
    def generate_fee_collection_report(self):
        """Generate comprehensive fee collection report"""
        # Get fee payments within the date range
        fee_payments = Payment.objects.filter(
            payment_date__gte=self.start_date,
            payment_date__lte=self.end_date
        ).select_related('tuition_fee', 'tuition_fee__student')
        
        # Build detailed payment data
        payment_list = []
        for payment in fee_payments:
            tuition_fee = payment.tuition_fee
            if tuition_fee and tuition_fee.student:
                student = tuition_fee.student
                outstanding = tuition_fee.amount_due - tuition_fee.amount_paid
                
                # Determine status
                if tuition_fee.amount_paid >= tuition_fee.amount_due:
                    status = 'Paid'
                elif tuition_fee.amount_paid > 0:
                    status = 'Partial'
                else:
                    status = 'Unpaid'
                
                payment_list.append({
                    'student_name': f"{student.user.first_name} {student.user.last_name}",
                    'student_class': getattr(student, 'current_class', 'N/A'),
                    'fee_type': f"{tuition_fee.session} {tuition_fee.term}",
                    'amount_due': float(tuition_fee.amount_due),  # Convert to float
                    'amount_paid': float(payment.amount),  # Convert to float
                    'outstanding': float(outstanding),  # Convert to float
                    'payment_date': payment.payment_date,
                    'status': status
                })
        
        # Calculate totals
        total_due = sum(item['amount_due'] for item in payment_list)
        total_paid = sum(item['amount_paid'] for item in payment_list)
        total_outstanding = sum(item['outstanding'] for item in payment_list)
        
        # Collection statistics
        collection_rate = (total_paid / total_due * 100) if total_due > 0 else 0
        students_paid = len([p for p in payment_list if p['status'] in ['Paid', 'Partial']])
        total_students = len(set(p['student_name'] for p in payment_list))
        average_payment = (total_paid / len(payment_list)) if payment_list else 0
        
        # Payment methods breakdown
        payment_methods = list(Payment.objects.filter(
            payment_date__gte=self.start_date,
            payment_date__lte=self.end_date
        ).values('method').annotate(
            amount=Sum('amount')
        ).order_by('-amount'))
        
        # Convert payment method amounts to float for JSON serialization
        for method in payment_methods:
            if 'amount' in method and method['amount']:
                method['amount'] = float(method['amount'])
        
        # Outstanding by class (simulated data structure)
        outstanding_by_class = []
        class_data = {}
        for payment in payment_list:
            class_name = payment['student_class']
            if class_name not in class_data:
                class_data[class_name] = {
                    'class_name': class_name,
                    'student_count': 0,
                    'total_outstanding': 0.0,  # Changed from Decimal to float
                    'students': set()
                }
            
            if payment['student_name'] not in class_data[class_name]['students']:
                class_data[class_name]['students'].add(payment['student_name'])
                class_data[class_name]['student_count'] += 1
            
            class_data[class_name]['total_outstanding'] += payment['outstanding']
        
        for class_info in class_data.values():
            avg_outstanding = (class_info['total_outstanding'] / class_info['student_count']) if class_info['student_count'] > 0 else 0
            outstanding_by_class.append({
                'class_name': class_info['class_name'],
                'student_count': class_info['student_count'],
                'total_outstanding': float(class_info['total_outstanding']),  # Ensure it's float
                'average_outstanding': float(avg_outstanding)  # Ensure it's float
            })
        
        return {
            'report_type': 'fee_collection',
            'period_name': self.period_name,
            'fee_payments': payment_list,
            'total_due': self._format_decimal(total_due),
            'total_paid': self._format_decimal(total_paid),
            'total_outstanding': self._format_decimal(total_outstanding),
            'collection_rate': self._format_decimal(collection_rate),
            'students_paid': students_paid,
            'total_students': total_students,
            'average_payment': self._format_decimal(average_payment),
            'payment_methods': payment_methods,
            'outstanding_by_class': outstanding_by_class,
            'generated_at': timezone.now().isoformat()
        }
    
    def generate_expense_report(self):
        """Generate comprehensive expense report"""
        # Get expenses within the date range
        expenses = Expense.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date
        ).order_by('-date')
        
        # Build detailed expense list
        expense_list = []
        for expense in expenses:
            expense_list.append({
                'date': expense.date,
                'category': expense.category.title() if expense.category else 'Other',
                'description': expense.description,
                'vendor': getattr(expense, 'vendor', None),
                'amount': float(expense.amount),  # Convert to float
                'payment_method': getattr(expense, 'payment_method', 'Cash'),
                'reference': getattr(expense, 'reference', None),
                'approved_by': getattr(expense, 'approved_by', None)
            })
        
        # Calculate total expenses
        total_expenses = sum(exp['amount'] for exp in expense_list)
        
        # Expenses by category with percentages
        expenses_by_category = []
        categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
        for category in categories:
            category_total = sum(
                exp['amount'] for exp in expense_list 
                if exp['category'].lower() == category
            )
            percentage = (category_total / total_expenses * 100) if total_expenses > 0 else 0
            
            expenses_by_category.append({
                'name': category.title(),
                'amount': self._format_decimal(category_total),
                'percentage': self._format_decimal(percentage)
            })
        
        # Payment methods breakdown
        payment_methods = {}
        for expense in expense_list:
            method = expense['payment_method']
            if method not in payment_methods:
                payment_methods[method] = 0.0  # Changed from Decimal to float
            payment_methods[method] += expense['amount']
        
        payment_method_list = []
        for method, amount in payment_methods.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            payment_method_list.append({
                'method': method,
                'amount': self._format_decimal(amount),
                'percentage': self._format_decimal(percentage)
            })
        
        # Monthly trend
        monthly_trend = []
        current_date = self.start_date.replace(day=1)
        previous_total = None
        
        while current_date <= self.end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            if month_end > self.end_date:
                month_end = self.end_date
            
            month_expenses = [
                exp for exp in expense_list
                if current_date <= exp['date'] <= month_end
            ]
            
            month_total = sum(exp['amount'] for exp in month_expenses)
            month_count = len(month_expenses)
            month_average = (month_total / month_count) if month_count > 0 else 0
            
            # Calculate percentage change
            change = 0
            if previous_total is not None and previous_total > 0:
                change = ((month_total - previous_total) / previous_total * 100)
            
            monthly_trend.append({
                'month_name': current_date.strftime('%B %Y'),
                'total': self._format_decimal(month_total),
                'count': month_count,
                'average': self._format_decimal(month_average),
                'change': self._format_decimal(change)
            })
            
            previous_total = month_total
            current_date = next_month
        
        # Top vendors
        vendor_totals = {}
        for expense in expense_list:
            vendor = expense['vendor'] or 'Unknown'
            if vendor not in vendor_totals:
                vendor_totals[vendor] = {'total': 0.0, 'count': 0}  # Changed from Decimal to float
            vendor_totals[vendor]['total'] += expense['amount']
            vendor_totals[vendor]['count'] += 1
        
        top_vendors = []
        for vendor, data in sorted(vendor_totals.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            average = (data['total'] / data['count']) if data['count'] > 0 else 0
            top_vendors.append({
                'name': vendor,
                'total': self._format_decimal(data['total']),
                'count': data['count'],
                'average': self._format_decimal(average)
            })
        
        # Summary statistics
        largest_expense = max((exp['amount'] for exp in expense_list), default=0.0)  # Changed from Decimal to float
        unique_vendors = len(set(exp['vendor'] for exp in expense_list if exp['vendor']))
        total_transactions = len(expense_list)
        average_transaction = (total_expenses / total_transactions) if total_transactions > 0 else 0
        
        return {
            'report_type': 'expense_report',
            'period_name': self.period_name,
            'expenses': expense_list,
            'total_expenses': self._format_decimal(total_expenses),
            'expenses_by_category': expenses_by_category,
            'payment_methods': payment_method_list,
            'monthly_trend': monthly_trend,
            'top_vendors': top_vendors,
            'total_transactions': total_transactions,
            'average_transaction': self._format_decimal(average_transaction),
            'largest_expense': self._format_decimal(largest_expense),
            'unique_vendors': unique_vendors,
            'generated_at': timezone.now().isoformat()
        }


def get_report_data(report_type, start_date, end_date, period_name):
    """Factory function to generate report data"""
    generator = ReportGenerator(start_date, end_date, period_name)
    
    if report_type == 'income_statement':
        return generator.generate_income_statement()
    elif report_type == 'balance_sheet':
        return generator.generate_balance_sheet()
    elif report_type == 'cash_flow':
        return generator.generate_cash_flow()
    elif report_type == 'fee_collection':
        return generator.generate_fee_collection_report()
    elif report_type == 'expense_report':
        return generator.generate_expense_report()
    else:
        return generator.generate_income_statement()  # Default
