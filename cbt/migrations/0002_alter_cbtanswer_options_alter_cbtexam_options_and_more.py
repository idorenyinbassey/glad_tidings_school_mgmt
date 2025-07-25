# Generated by Django 5.2.4 on 2025-07-03 18:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbt', '0001_initial'),
        ('students', '0002_studentprofile_created_at_studentprofile_updated_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cbtanswer',
            options={'ordering': ['question']},
        ),
        migrations.AlterModelOptions(
            name='cbtexam',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='cbtquestion',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='cbtsession',
            options={'ordering': ['-started_at']},
        ),
        migrations.AddField(
            model_name='cbtanswer',
            name='answered_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cbtexam',
            name='duration_minutes',
            field=models.PositiveIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='cbtexam',
            name='instructions',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='cbtexam',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cbtexam',
            name='pass_mark',
            field=models.PositiveIntegerField(default=50),
        ),
        migrations.AddField(
            model_name='cbtexam',
            name='total_marks',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='cbtquestion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cbtquestion',
            name='marks',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='cbtsession',
            name='is_submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cbtsession',
            name='percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='cbtquestion',
            name='option_a',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='cbtquestion',
            name='option_b',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='cbtquestion',
            name='option_c',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='cbtquestion',
            name='option_d',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterUniqueTogether(
            name='cbtanswer',
            unique_together={('session', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='cbtsession',
            unique_together={('exam', 'student')},
        ),
    ]
