from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import StudentProfile, AcademicStatus, AttendanceRecord


class StudentProfileForm(forms.ModelForm):
    """Form for creating and editing student profiles"""
    
    class Meta:
        model = StudentProfile
        fields = ['user', 'admission_number', 'date_of_birth', 'address', 'guardian_name', 'guardian_contact']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'admission_number': forms.TextInput(attrs={'placeholder': 'e.g., GTS/2024/001'}),
            'guardian_name': forms.TextInput(attrs={'placeholder': 'Full name of guardian'}),
            'guardian_contact': forms.TextInput(attrs={'placeholder': 'Phone number or email'}),
        }

    def clean_admission_number(self):
        admission_number = self.cleaned_data['admission_number'].strip().upper()
        
        # Check for existing admission number
        existing = StudentProfile.objects.filter(admission_number=admission_number)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError("A student with this admission number already exists.")
        
        return admission_number

    def clean_guardian_contact(self):
        contact = self.cleaned_data['guardian_contact'].strip()
        if contact and len(contact) < 10:
            raise forms.ValidationError("Guardian contact should be at least 10 characters.")
        return contact


class AcademicStatusForm(forms.ModelForm):
    """Form for managing student academic status"""
    
    class Meta:
        model = AcademicStatus
        fields = ['student', 'session', 'term', 'current_class', 'promoted', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'session': forms.TextInput(attrs={'placeholder': '2024/2025'}),
            'term': forms.Select(choices=[
                ('first', 'First Term'),
                ('second', 'Second Term'),
                ('third', 'Third Term')
            ]),
            'current_class': forms.TextInput(attrs={'placeholder': 'e.g., Primary 1, JSS 1, SS 1'}),
        }

    def clean_session(self):
        session = self.cleaned_data['session'].strip()
        # Validate session format (e.g., 2024/2025)
        if not session.replace('/', '').replace('-', '').isdigit():
            raise forms.ValidationError("Session should be in format like 2024/2025")
        return session


class AttendanceRecordForm(forms.ModelForm):
    """Form for recording student attendance"""
    
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'date', 'present']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError("Attendance date cannot be in the future")
        return date


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking"""
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    
    class_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Primary 1'})
    )
    
    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError("Attendance date cannot be in the future")
        return date
