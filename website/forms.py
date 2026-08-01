import re
import uuid

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from .models import Contact, Testimony

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture', 'username', 'full_name', 'email', 'phone', 'homeCounty']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'homeCounty': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Leave blank to create an unusable password and send a reset link later.',
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'full_name',
            'phone',
            'registrationNumber',
            'homeCounty',
            'userType',
            'yearOfStudy',
            'role',
        )
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'registrationNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'homeCounty': forms.TextInput(attrs={'class': 'form-control'}),
            'userType': forms.Select(attrs={'class': 'form-control'}),
            'yearOfStudy': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('The two password fields didn’t match.')
        return password2

    def generate_username(self, base_value):
        base = re.sub(r'[^A-Za-z0-9]+', '', str(base_value or 'user'))[:30] or uuid.uuid4().hex[:12]
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        registration = self.cleaned_data.get('registrationNumber')
        user.username = self.generate_username(registration or user.email.split('@')[0])

        if commit:
            user.save()
        return user

class ContactMessageReplyForm(forms.ModelForm):
    reply = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        required=False,
        label="Reply",
    )

    class Meta:
        model = Contact
        fields = ['name', 'email', 'message', 'reply']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'message': forms.Textarea(attrs={'readonly': 'readonly'}),
        }


class TestimonySubmissionForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Photo',
    )

    class Meta:
        model = Testimony
        fields = ['testimony', 'image']
        widgets = {
            'testimony': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share what God has done in your life...',
            }),
        }
        labels = {
            'testimony': 'Your testimony',
        }


# ---------------------------------------------------------------------------
# Onboarding: User Manager creates a new user account
# ---------------------------------------------------------------------------

class OnboardUserForm(forms.Form):
    """
    Minimal form used by User Manager members to create new user accounts.
    Only three fields are entered manually; all other attributes are derived
    or set automatically.
    """

    REG_NUMBER_HINT = 'e.g. A11/0000/24'

    full_name = forms.CharField(
        max_length=100,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Uncle P',
            'autocomplete': 'off',
        }),
    )
    registrationNumber = forms.CharField(
        max_length=20,
        label='Registration Number',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': REG_NUMBER_HINT,
            'autocomplete': 'off',
        }),
        help_text=REG_NUMBER_HINT,
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student@egerton.ac.ke/youremail@gmail.com',
            'autocomplete': 'off',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email

    def clean_registrationNumber(self):
        reg_no = self.cleaned_data.get('registrationNumber', '').strip()
        if not reg_no:
            return reg_no
        User = get_user_model()
        if User.objects.filter(registrationNumber=reg_no).exists():
            raise ValidationError('This registration number is already in use.')
        return reg_no

    @staticmethod
    def _generate_username(email):
        """Derive a unique username from the email local part."""
        User = get_user_model()
        base = re.sub(r'[^A-Za-z0-9]+', '', email.split('@')[0])[:30] or uuid.uuid4().hex[:12]
        username = base.lower()
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base.lower()}{counter}"
            counter += 1
        return username


# ---------------------------------------------------------------------------
# Onboarding: User completes their profile on first login
# ---------------------------------------------------------------------------

class CompleteRegistrationForm(forms.Form):
    """
    First-login form that collects all remaining profile information and
    forces a password change away from the temporary password.
    """

    YEAR_CHOICES = [
        (1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'),
        (4, 'Year 4'), (5, 'Year 5'), (6, 'Year 6'),
    ]

    USER_TYPE_CHOICES = [
        ('student', 'Current Student'),
        ('alumnus', 'Alumnus'),
    ]

    # --- Identity ---
    phone = forms.CharField(
        max_length=20,
        label='Phone Number',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254 7XX XXX XXX'}),
    )
    homeCounty = forms.CharField(
        max_length=50,
        label='Home County',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nakuru'}),
    )
    userType = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label='Member Type',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    yearOfStudy = forms.ChoiceField(
        choices=[('', '--- Select ---')] + YEAR_CHOICES,
        label='Year of Study',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    graduationYear = forms.IntegerField(
        label='Graduation Year',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2022'}),
    )
    currentOccupation = forms.CharField(
        max_length=100,
        label='Current Occupation',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
    )
    workplace = forms.CharField(
        max_length=100,
        label='Workplace / Institution',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Egerton University'}),
    )
    profile_picture = forms.ImageField(
        label='Profile Photo',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    )

    # --- Password change (required because must_change_password=True) ---
    new_password = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a strong password',
            'autocomplete': 'new-password',
        }),
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your new password',
            'autocomplete': 'new-password',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('new_password', '')
        pw2 = cleaned.get('confirm_password', '')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('confirm_password', 'The two passwords do not match.')
        return cleaned
