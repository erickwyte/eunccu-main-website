import re
import uuid

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from .models import Contact, Testimony

User = get_user_model()

class ProfileForm(forms.ModelForm):
    """Enhanced profile form with better widgets and validation"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    COUNTRY_CHOICES = [
        ('Kenya', 'Kenya'),
        ('International', 'International'),
    ]

    KENYA_COUNTIES = [
        ('', '--- Select County ---'),
        ('Mombasa', 'Mombasa'),
        ('Kwale', 'Kwale'),
        ('Kilifi', 'Kilifi'),
        ('Tana River', 'Tana River'),
        ('Lamu', 'Lamu'),
        ('Taita–Taveta', 'Taita–Taveta'),
        ('Garissa', 'Garissa'),
        ('Wajir', 'Wajir'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Isiolo', 'Isiolo'),
        ('Meru', 'Meru'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'),
        ('Embu', 'Embu'),
        ('Kitui', 'Kitui'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Murang\'a', 'Murang\'a'),
        ('Kiambu', 'Kiambu'),
        ('Turkana', 'Turkana'),
        ('West Pokot', 'West Pokot'),
        ('Samburu', 'Samburu'),
        ('Trans Nzoia', 'Trans Nzoia'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
        ('Nandi', 'Nandi'),
        ('Baringo', 'Baringo'),
        ('Laikipia', 'Laikipia'),
        ('Nakuru', 'Nakuru'),
        ('Narok', 'Narok'),
        ('Kajiado', 'Kajiado'),
        ('Kericho', 'Kericho'),
        ('Bomet', 'Bomet'),
        ('Kakamega', 'Kakamega'),
        ('Vihiga', 'Vihiga'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Siaya', 'Siaya'),
        ('Kisumu', 'Kisumu'),
        ('Homa Bay', 'Homa Bay'),
        ('Migori', 'Migori'),
        ('Kisii', 'Kisii'),
        ('Nyamira', 'Nyamira'),
        ('Nairobi City', 'Nairobi City'),
    ]

    RESIDENCY_TYPE_CHOICES = [
        ('on-campus', 'On-Campus Resident (Living in University Hostels/Residence)'),
        ('off-campus', 'Off-Campus Resident (Living in private residences around campus)'),
    ]

    HALL_OF_RESIDENCE_CHOICES = [
        ('', '--- Select Hall ---'),
        ('Old Hall', 'Old Hall'),
        ('Tatton', 'Tatton'),
        ('Buruburu/Hollywood', 'Buruburu/Hollywood'),
        ('Riverview/Riverside', 'Riverview/Riverside'),
        ('UpSchool-CBD, Ruwenzori, Baringo, Mama-Ngina, Taifa, Uganda, Barret', 'UpSchool-CBD, Ruwenzori, Baringo, Mama-Ngina, Taifa, Uganda, Barret'),
    ]

    OFF_CAMPUS_AREA_CHOICES = [
        ('', '--- Select Area ---'),
        ('Main Gate', 'Main Gate'),
        ('Njokerio', 'Njokerio'),
        ('Ng\'ondu', 'Ng\'ondu'),
        ('Ahero', 'Ahero'),
    ]
    
    class Meta:
        model = User
        fields = ['profile_picture', 'username', 'full_name', 'email', 'phone', 'gender', 'country', 'homeCounty', 'residencyType', 'hallOfResidence', 'offCampusArea', 'registrationNumber', 'yearOfStudy']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a unique username (3-50 characters)',
                'minlength': '3',
                'maxlength': '50',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'minlength': '2',
                'maxlength': '100',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 7XX XXX XXX',
                'pattern': r'[0-9\+\-\s]+',
                'maxlength': '20',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }),
            'country': forms.Select(attrs={
                'class': 'form-control',
            }),
            'homeCounty': forms.Select(attrs={
                'class': 'form-control',
            }),
            'residencyType': forms.RadioSelect(attrs={
                'class': 'form-check-input',
                'id': 'id_residencyType',
            }),
            'hallOfResidence': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_hallOfResidence',
                'style': 'display:none;',
            }),
            'offCampusArea': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_offCampusArea',
                'style': 'display:none;',
            }),
            'registrationNumber': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your registration/student number',
                'maxlength': '20',
            }),
            'yearOfStudy': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        help_texts = {
            'profile_picture': 'Upload a JPG, PNG, WebP or GIF image (Max 5MB)',
            'username': 'Used for login. Cannot be changed frequently.',
            'email': 'Used for account recovery and notifications',
            'phone': 'Optional: For community communication',
            'gender': 'Optional: Your gender',
            'country': 'Optional: Your country',
            'homeCounty': 'Optional: Your home county (for Kenya)',
            'residencyType': 'Optional: Where you live',
            'hallOfResidence': 'Optional: Your hall of residence',
            'offCampusArea': 'Optional: Your off-campus area',
            'yearOfStudy': 'Optional: Your current year of study',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set gender choices
        self.fields['gender'] = forms.ChoiceField(
            choices=[('', '--- Select ---')] + self.GENDER_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        # Set country choices
        self.fields['country'] = forms.ChoiceField(
            choices=self.COUNTRY_CHOICES,
            required=False,
            initial='Kenya',
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        # Set county choices
        self.fields['homeCounty'] = forms.ChoiceField(
            choices=self.KENYA_COUNTIES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        # Set residency type choices
        self.fields['residencyType'] = forms.ChoiceField(
            choices=self.RESIDENCY_TYPE_CHOICES,
            required=False,
            widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        )
        # Set hall of residence choices
        self.fields['hallOfResidence'] = forms.ChoiceField(
            choices=self.HALL_OF_RESIDENCE_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        # Set off-campus area choices
        self.fields['offCampusArea'] = forms.ChoiceField(
            choices=self.OFF_CAMPUS_AREA_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        # Set year of study choices
        year_choices = [('', '--- Select Year ---')] + list(User.YEAR_OF_STUDY_CHOICES)
        self.fields['yearOfStudy'] = forms.ChoiceField(
            choices=year_choices,
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email address is already registered. Please use another email.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name) < 2:
            raise ValidationError('Full name must be at least 2 characters long.')
        return full_name
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Validate file size (5MB max)
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError('File size must not exceed 5MB.')
            # Validate file type
            allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            if not profile_picture.name.lower().split('.')[-1] in allowed_formats:
                raise ValidationError('Only JPG, PNG, GIF, and WebP files are allowed.')
        return profile_picture


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
            'autocomplete': 'current-password',
        }),
        required=True,
    )
    new_password = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a strong new password',
            'autocomplete': 'new-password',
        }),
        required=True,
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your new password',
            'autocomplete': 'new-password',
        }),
        required=True,
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if self.user and not self.user.check_password(current_password):
            raise ValidationError('Current password is incorrect.')
        return current_password

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('new_password')
        pw2 = cleaned.get('confirm_password')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('confirm_password', 'The two passwords do not match.')
        elif pw1 and self.user:
            password_validation.validate_password(pw1, self.user)
        return cleaned


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

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    COUNTRY_CHOICES = [
        ('Kenya', 'Kenya'),
        ('International', 'International'),
    ]

    RESIDENCY_TYPE_CHOICES = [
        ('on-campus', 'On-Campus Resident (Living in University Hostels/Residence)'),
        ('off-campus', 'Off-Campus Resident (Living in private residences around campus)'),
    ]

    HALL_OF_RESIDENCE_CHOICES = [
        ('', '--- Select Hall ---'),
        ('Old Hall', 'Old Hall'),
        ('Tatton', 'Tatton'),
        ('Buruburu/Hollywood', 'Buruburu/Hollywood'),
        ('Riverview/Riverside', 'Riverview/Riverside'),
        ('UpSchool-CBD, Ruwenzori, Baringo, Mama-Ngina, Taifa, Uganda, Barret', 'UpSchool-CBD, Ruwenzori, Baringo, Mama-Ngina, Taifa, Uganda, Barret'),
    ]

    OFF_CAMPUS_AREA_CHOICES = [
        ('', '--- Select Area ---'),
        ('Main Gate', 'Main Gate'),
        ('Njokerio', 'Njokerio'),
        ("Ng'ondu", "Ng'ondu"),
        ('Ahero', 'Ahero'),
    ]

    KENYA_COUNTIES = [
        ('', '--- Select County ---'),
        ('Mombasa', 'Mombasa'),
        ('Kwale', 'Kwale'),
        ('Kilifi', 'Kilifi'),
        ('Tana River', 'Tana River'),
        ('Lamu', 'Lamu'),
        ('Taita�Taveta', 'Taita�Taveta'),
        ('Garissa', 'Garissa'),
        ('Wajir', 'Wajir'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Isiolo', 'Isiolo'),
        ('Meru', 'Meru'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'),
        ('Embu', 'Embu'),
        ('Kitui', 'Kitui'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Murang\'a', 'Murang\'a'),
        ('Kiambu', 'Kiambu'),
        ('Turkana', 'Turkana'),
        ('West Pokot', 'West Pokot'),
        ('Samburu', 'Samburu'),
        ('Trans Nzoia', 'Trans Nzoia'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
        ('Nandi', 'Nandi'),
        ('Baringo', 'Baringo'),
        ('Laikipia', 'Laikipia'),
        ('Nakuru', 'Nakuru'),
        ('Narok', 'Narok'),
        ('Kajiado', 'Kajiado'),
        ('Kericho', 'Kericho'),
        ('Bomet', 'Bomet'),
        ('Kakamega', 'Kakamega'),
        ('Vihiga', 'Vihiga'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Siaya', 'Siaya'),
        ('Kisumu', 'Kisumu'),
        ('Homa Bay', 'Homa Bay'),
        ('Migori', 'Migori'),
        ('Kisii', 'Kisii'),
        ('Nyamira', 'Nyamira'),
        ('Nairobi City', 'Nairobi City'),
    ]


    # --- Personal Information ---
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Gender',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    phone = forms.CharField(
        max_length=20,
        label='Phone Number',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254 7XX XXX XXX'}),
    )
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        label='Country',
        required=False,
        initial='Kenya',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_country'}),
    )
    
    homeCounty = forms.ChoiceField(
        choices=KENYA_COUNTIES,
        label='County (Kenya)',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_homeCounty'}),
    )
    
    residencyType = forms.ChoiceField(
        choices=RESIDENCY_TYPE_CHOICES,
        label='Residency Type',
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input', 'id': 'id_residencyType'}),
    )
    
    hallOfResidence = forms.ChoiceField(
        choices=HALL_OF_RESIDENCE_CHOICES,
        label='Hall of Residence',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_hallOfResidence', 'style': 'display:none;'}),
    )
    
    offCampusArea = forms.ChoiceField(
        choices=OFF_CAMPUS_AREA_CHOICES,
        label='Off-Campus Area',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_offCampusArea', 'style': 'display:none;'}),
    )
    
    userType = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label='Member Type',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    yearOfStudy = forms.ChoiceField(
        choices=[('', '--- Select ---')] + YEAR_CHOICES,
        label='Year of Study',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    currentOccupation = forms.CharField(
        max_length=100,
        label='Current Occupation',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
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
