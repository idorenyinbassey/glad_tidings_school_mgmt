from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError


# Create your models here.


class TuitionFee(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ]

    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='tuition_fees')
    session = models.CharField(max_length=20, db_index=True)  # Added index for improved querying
    term = models.CharField(max_length=20, db_index=True)  # Added index for improved querying
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(db_index=True)  # Added index for due date filtering
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        default='unpaid',
        choices=STATUS_CHOICES,
        db_index=True
    )  # Added index for status filtering
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tuitionfee_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tuitionfee_updated'
    )

    class Meta:
        # Composite index for commonly queried combinations
        indexes = [
            models.Index(fields=['student', 'session', 'term']),
            models.Index(fields=['status', 'due_date']),
        ]

    def clean(self):
        """Validate the model fields"""
        super().clean()

        # Validate amount_due
        if self.amount_due and self.amount_due <= 0:
            raise ValidationError("Amount due must be greater than zero")

        # Validate amount_paid
        if self.amount_paid and self.amount_paid < 0:
            raise ValidationError("Amount paid cannot be negative")

        # Validate that amount_paid doesn't exceed amount_due
        if self.amount_paid and self.amount_due and self.amount_paid > self.amount_due:
            raise ValidationError("Amount paid cannot exceed amount due")

        # Validate due_date
        if self.due_date and self.due_date < timezone.now().date().replace(year=timezone.now().year - 1):
            raise ValidationError("Due date cannot be more than a year in the past")

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
        return self.status

    def save(self, *args, **kwargs):
        if 'update_fields' not in kwargs or 'status' not in kwargs.get('update_fields', []):
            self.status = self.update_status()
        super().save(*args, **kwargs)

    @property
    def amount_outstanding(self):
        """Calculate the outstanding amount"""
        return max(0, self.amount_due - self.amount_paid)

    @property
    def payment_percentage(self):
        """Calculate the payment percentage"""
        if self.amount_due > 0:
            return (self.amount_paid / self.amount_due) * 100
        return 0

    @classmethod
    def get_fee_statistics(cls):
        """Get overall fee statistics"""
        from django.db.models import Sum

        total_due = cls.objects.aggregate(total=Sum('amount_due'))['total'] or 0
        total_paid = cls.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
        unpaid_count = cls.objects.filter(status='unpaid').count()
        partial_count = cls.objects.filter(status='partial').count()
        paid_count = cls.objects.filter(status='paid').count()

        return {
            'total_due': total_due,
            'total_paid': total_paid,
            'outstanding': max(0, total_due - total_paid),
            'unpaid_count': unpaid_count,
            'partial_count': partial_count,
            'paid_count': paid_count,
            'collection_percentage': (total_paid / total_due * 100) if total_due > 0 else 0
        }


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
        ('online', 'Online Payment'),
    ]
    tuition_fee = models.ForeignKey(TuitionFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(db_index=True)  # Add index for payment date
    method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        db_index=True
    )  # Add index for filtering by method
    receipt_number = models.CharField(max_length=50, blank=True, db_index=True)  # Add index for searching by receipt
    reference = models.CharField(max_length=100, blank=True, db_index=True)  # Add index for searching by reference
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payment_created'
    )

    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['payment_date', 'method']),
            models.Index(fields=['created_at', 'created_by']),
        ]

    def __str__(self):
        return f"{self.tuition_fee} - {self.amount} on {self.payment_date}"

    def clean(self):
        """Validate the payment before saving"""
        super().clean()

        if self.amount and self.amount <= 0:
            raise ValidationError("Payment amount must be greater than zero")

        if self.tuition_fee and self.amount:
            # Check for overpayment only for new payments
            if not self.pk:  # New payment
                total_paid = self.tuition_fee.amount_paid + self.amount
                remaining_due = self.tuition_fee.amount_due - self.tuition_fee.amount_paid

                if total_paid > self.tuition_fee.amount_due:
                    raise ValidationError(
                        f"Payment of ₦{self.amount:,.2f} exceeds remaining balance of ₦{remaining_due:,.2f}. "
                        f"Maximum payment allowed is ₦{remaining_due:,.2f}."
                    )

    def save(self, *args, **kwargs):
        # Run validation
        self.clean()

        with transaction.atomic():
            # Check if this is a new payment
            is_new = self.pk is None

            super().save(*args, **kwargs)

            # Only update tuition fee for new payments
            if is_new:
                # Update the tuition fee
                tuition = self.tuition_fee
                tuition.amount_paid += self.amount
                # Update status manually before saving to avoid recursion
                if tuition.amount_paid >= tuition.amount_due:
                    tuition.status = 'paid'
                    tuition.paid_date = timezone.now().date()
                elif tuition.amount_paid > 0:
                    tuition.status = 'partial'
                # Save with specific fields to avoid triggering unnecessary updates
                tuition.save(update_fields=['amount_paid', 'status', 'paid_date'])


class Payroll(models.Model):
    staff = models.ForeignKey('staff.StaffProfile', on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payroll_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payroll_updated'
    )

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
    date = models.DateField(db_index=True)  # Add index for date filtering
    category = models.CharField(
        max_length=100,
        choices=EXPENSE_CATEGORIES,
        db_index=True
    )  # Add index for category filtering
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='expense_created'
    )

    class Meta:
        indexes = [
            models.Index(fields=['date', 'category']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount} on {self.date}"
