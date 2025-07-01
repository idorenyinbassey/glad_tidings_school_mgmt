from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from django import forms
from .models import TuitionFee, Payment, Payroll, Expense

class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter tuition fees to show only those with outstanding balance
        if not self.instance.pk:  # New payment
            self.fields['tuition_fee'].queryset = TuitionFee.objects.filter(
                Q(status='unpaid') | Q(status='partial')
            ).select_related('student__user')
    
    def clean(self):
        cleaned_data = super().clean()
        tuition_fee = cleaned_data.get('tuition_fee')
        amount = cleaned_data.get('amount')
        
        if tuition_fee and amount:
            # Validate amount is positive
            if amount <= 0:
                raise forms.ValidationError("Payment amount must be greater than zero.")
            
            # Only validate for new payments
            if not self.instance.pk:
                remaining_balance = tuition_fee.amount_due - tuition_fee.amount_paid
                if amount > remaining_balance:
                    raise forms.ValidationError(
                        f"Payment amount of ₦{amount:,.2f} exceeds the remaining balance of ₦{remaining_balance:,.2f}. "
                        f"Please enter an amount not greater than ₦{remaining_balance:,.2f}."
                    )
        
        return cleaned_data

@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'amount_due', 'amount_paid', 'remaining_balance', 'status', 'due_date', 'paid_date')
    search_fields = ('student__admission_number', 'student__user__first_name', 'student__user__last_name', 'session', 'term', 'status')
    list_filter = ('status', 'session', 'term', 'due_date')
    readonly_fields = ('amount_paid', 'paid_date')
    
    def remaining_balance(self, obj):
        balance = obj.amount_due - obj.amount_paid
        if balance <= 0:
            return format_html('<span style="color: green;">₦0.00</span>')
        return format_html('<span style="color: red;">₦{:,.2f}</span>', balance)
    remaining_balance.short_description = 'Remaining Balance'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ('tuition_fee', 'student_name', 'amount', 'payment_date', 'method', 'reference', 'remaining_after_payment')
    search_fields = ('tuition_fee__student__user__first_name', 'tuition_fee__student__user__last_name', 
                    'tuition_fee__student__admission_number', 'method', 'reference')
    list_filter = ('payment_date', 'method', 'tuition_fee__status')
    readonly_fields = ('created_at', 'created_by')
    
    def student_name(self, obj):
        return obj.tuition_fee.student.user.get_full_name()
    student_name.short_description = 'Student'
    
    def remaining_after_payment(self, obj):
        remaining = obj.tuition_fee.amount_due - obj.tuition_fee.amount_paid
        if remaining <= 0:
            return format_html('<span style="color: green;">Fully Paid</span>')
        return format_html('<span style="color: orange;">₦{:,.2f}</span>', remaining)
    remaining_after_payment.short_description = 'Balance After Payment'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new payments
            obj.created_by = request.user
        
        # The form validation should have already been run by Django
        # But we can add an extra safety check here
        super().save_model(request, obj, form, change)

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('staff', 'month', 'year', 'amount', 'paid', 'paid_date')
    search_fields = ('staff__staff_id', 'month', 'year')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'date', 'category')
    search_fields = ('description', 'category')
