# Generated manually by Copilot

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20250626_1336'),
    ]

    operations = [
        # Add indices to TuitionFee model
        migrations.AddIndex(
            model_name='tuitionfee',
            index=models.Index(fields=['student', 'session', 'term'], name='accounting__student_b2ad3d_idx'),
        ),
        migrations.AddIndex(
            model_name='tuitionfee',
            index=models.Index(fields=['status', 'due_date'], name='accounting__status_9e4141_idx'),
        ),
        migrations.AlterField(
            model_name='tuitionfee',
            name='due_date',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='tuitionfee',
            name='session',
            field=models.CharField(db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='tuitionfee',
            name='status',
            field=models.CharField(choices=[('unpaid', 'Unpaid'), ('partial', 'Partial'), ('paid', 'Paid')], db_index=True, default='unpaid', max_length=20),
        ),
        migrations.AlterField(
            model_name='tuitionfee',
            name='term',
            field=models.CharField(db_index=True, max_length=20),
        ),
        
        # Add indices to Payment model
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['payment_date', 'method'], name='accounting__payment_2a9141_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['created_at', 'created_by'], name='accounting__created_fd4132_idx'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(choices=[('cash', 'Cash'), ('bank', 'Bank Transfer'), ('card', 'Card'), ('online', 'Online Payment')], db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='receipt_number',
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='reference',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        
        # Add indices to Expense model
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['date', 'category'], name='accounting__date_9c7d8c_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['created_at'], name='accounting__created_910db7_idx'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('supplies', 'Supplies'), ('maintenance', 'Maintenance'), ('salary', 'Salary'), ('utility', 'Utility'), ('other', 'Other')], db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(db_index=True),
        ),
    ]
