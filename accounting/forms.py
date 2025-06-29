from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import TuitionFee, Payment, Payroll, Expense
from students.models import StudentProfile
from staff.models import StaffProfile


class TuitionFeeForm(forms.ModelForm):
    """Form for creating and editing tuition fees with validation"""
    
    class Meta:
        model = TuitionFee
        fields = ['student', 'session', 'term', 'amount_due', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'amount_due': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_amount_due(self):
        amount = self.cleaned_data['amount_due']
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive")
        if amount > 10000000:  # 10 million naira cap
            raise forms.ValidationError("Amount seems too high. Please verify.")
        return amount

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past")
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        session = cleaned_data.get('session')
        term = cleaned_data.get('term')
        
        # Check for duplicate fee for same student, session, and term
        if student and session and term:
            existing_fee = TuitionFee.objects.filter(
                student=student, 
                session=session, 
                term=term
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_fee.exists():
                raise ValidationError("A tuition fee already exists for this student, session, and term.")
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    """Form for recording payments with validation"""
    
    class Meta:
        model = Payment
        fields = ['tuition_fee', 'amount', 'payment_date', 'method', 'receipt_number', 'reference', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be positive")
        return amount

    def clean_payment_date(self):
        payment_date = self.cleaned_data['payment_date']
        if payment_date > timezone.now().date():
            raise forms.ValidationError("Payment date cannot be in the future")
        return payment_date

    def clean(self):
        cleaned_data = super().clean()
        tuition_fee = cleaned_data.get('tuition_fee')
        amount = cleaned_data.get('amount')
        
        # Check if payment would exceed amount due
        if tuition_fee and amount:
            outstanding = tuition_fee.amount_due - tuition_fee.amount_paid
            if amount > outstanding:
                raise ValidationError(f"Payment amount (₦{amount:,.2f}) exceeds outstanding balance (₦{outstanding:,.2f})")
        
        return cleaned_data


class PayrollForm(forms.ModelForm):
    """Form for staff payroll with validation"""
    
    class Meta:
        model = Payroll
        fields = ['staff', 'month', 'year', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Salary amount must be positive")
        if amount > 5000000:  # 5 million naira cap
            raise forms.ValidationError("Salary amount seems too high. Please verify.")
        return amount

    def clean_year(self):
        year = self.cleaned_data['year']
        current_year = timezone.now().year
        if year < current_year - 2 or year > current_year + 1:
            raise forms.ValidationError("Year must be within reasonable range")
        return year

    def clean(self):
        cleaned_data = super().clean()
        staff = cleaned_data.get('staff')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        
        # Check for duplicate payroll
        if staff and month and year:
            existing_payroll = Payroll.objects.filter(
                staff=staff, 
                month=month, 
                year=year
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_payroll.exists():
                raise ValidationError("Payroll already exists for this staff member, month, and year.")
        
        return cleaned_data


class ExpenseForm(forms.ModelForm):
    """Form for recording expenses with validation"""
    
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'description': forms.TextInput(attrs={'placeholder': 'Enter expense description'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Expense amount must be positive")
        if amount > 10000000:  # 10 million naira cap
            raise forms.ValidationError("Expense amount seems too high. Please verify.")
        return amount

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError("Expense date cannot be in the future")
        # Don't allow expenses older than 2 years
        if date < timezone.now().date().replace(year=timezone.now().year - 2):
            raise forms.ValidationError("Expense date cannot be more than 2 years old")
        return date

    def clean_description(self):
        description = self.cleaned_data['description'].strip()
        if len(description) < 3:
            raise forms.ValidationError("Description must be at least 3 characters long")
        return description


class StudentSearchForm(forms.Form):
    """Form for searching students"""
    
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, admission number, or email',
            'class': 'form-control'
        }),
        required=False
    )
    
    current_class = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by class',
            'class': 'form-control'
        }),
        required=False
    )


class StaffSearchForm(forms.Form):
    """Form for searching staff members"""
    
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, staff ID, or email',
            'class': 'form-control'
        }),
        required=False
    )
    
    department = forms.ChoiceField(
        choices=[('', 'All Departments')] + StaffProfile.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    position = forms.ChoiceField(
        choices=[('', 'All Positions')] + StaffProfile.POSITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
