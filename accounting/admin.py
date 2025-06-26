from django.contrib import admin
from .models import TuitionFee, Payment, Payroll, Expense

@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'amount_due', 'amount_paid', 'status', 'due_date', 'paid_date')
    search_fields = ('student__admission_number', 'session', 'term', 'status')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('tuition_fee', 'amount', 'payment_date', 'method', 'reference')
    search_fields = ('tuition_fee__student__admission_number', 'method', 'reference')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('staff', 'month', 'year', 'amount', 'paid', 'paid_date')
    search_fields = ('staff__staff_id', 'month', 'year')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'date', 'category')
    search_fields = ('description', 'category')
