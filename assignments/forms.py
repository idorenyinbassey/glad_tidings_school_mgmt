from django import forms
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'subject',
            'assigned_class',
            'due_date',
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']


class SubmissionGradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade', 'feedback']
