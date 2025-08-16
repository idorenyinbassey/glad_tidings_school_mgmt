from django import forms
from .models import InboxMessage


class AdmissionApplicationForm(forms.ModelForm):
    agree_terms = forms.BooleanField(required=True)

    class Meta:
        model = InboxMessage
        fields = [
            'application_type', 'academic_year', 'grade_level',
            'first_name', 'middle_name', 'last_name', 'dob', 'gender',
            'parent_name', 'relationship', 'email', 'phone', 'address',
            'previous_school', 'agree_terms'
        ]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.message_type = 'admission'
        obj.full_name = f"{self.cleaned_data.get('first_name','')} {self.cleaned_data.get('last_name','')}".strip()
        if commit:
            obj.save()
        return obj


class ContactForm(forms.ModelForm):
    class Meta:
        model = InboxMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.message_type = 'contact'
        if commit:
            obj.save()
        return obj
