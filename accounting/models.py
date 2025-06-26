from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

# Create your models here.

class TuitionFee(models.Model):
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='tuition_fees')
    session = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='unpaid', choices=[('unpaid', 'Unpaid'), ('partial', 'Partial'), ('paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='tuitionfee_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='tuitionfee_updated')

    def __str__(self):
        return f"{self.student} - {self.session} {self.term} - {self.status}"

    def update_status(self):
        if self.amount_paid >= self.amount_due:
            self.status = 'paid'
            self.paid_date = timezone.now().date()
        elif self.amount_paid > 0:
            self.status = 'partial'
            self.paid_date = None
        else:
            self.status = 'unpaid'
            self.paid_date = None
        self.save(update_fields=['status', 'paid_date'])

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
        ('online', 'Online Payment'),
    ]
    tuition_fee = models.ForeignKey(TuitionFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_created')

    def __str__(self):
        return f"{self.tuition_fee} - {self.amount} on {self.payment_date}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Prevent overpayment
            total_paid = self.tuition_fee.amount_paid + self.amount
            if total_paid > self.tuition_fee.amount_due:
                raise ValueError('Payment exceeds amount due!')
            super().save(*args, **kwargs)
            self.tuition_fee.amount_paid += self.amount
            self.tuition_fee.save()

class Payroll(models.Model):
    staff = models.ForeignKey('staff.StaffProfile', on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='payroll_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='payroll_updated')

    def __str__(self):
        return f"{self.staff} - {self.month} {self.year} - {'Paid' if self.paid else 'Unpaid'}"

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('salary', 'Salary'),
        ('utility', 'Utility'),
        ('other', 'Other'),
    ]
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, choices=EXPENSE_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='expense_created')

    def __str__(self):
        return f"{self.description} - {self.amount} on {self.date}"
