from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import User, StudentProfile

class StudentCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text="Required. 150 characters or fewer.")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Set a temporary password.")
    roll_number = forms.CharField(max_length=20, required=True, label="Roll Number")
    department = forms.CharField(max_length=100, required=True, label="Department")
    year = forms.IntegerField(required=True, label="Year (Example: 1, 2, 3, 4)")

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        # Save User (with role=STUDENT)
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'STUDENT'
        if commit:
            user.save()
            
            # Save Profile
            StudentProfile.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                department=self.cleaned_data['department'],
                year=self.cleaned_data['year']
            )
        return user

class AdminPasswordResetForm(SetPasswordForm):
    # Just inheriting from Django's built-in form
    pass
