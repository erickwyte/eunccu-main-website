from xml.parsers.expat import model

from django.db import models
from datetime import date, datetime, time
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


#--- Devotions page models---

class Devotion(models.Model): 
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    written_by = models.CharField(max_length=100)
    scripture_reference = models.CharField(max_length=100)
    content = CKEditor5Field(config_name='default')
    image = models.ImageField(upload_to='devotions/')
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
        
# Exec positions choices
POSITIONS = [
    ('Chairperson', 'Chairperson'),
    ('Vice Chairperson', 'Vice Chairperson'),
    ('Secretary', 'Secretary'),
    ('Treasurer', 'Treasurer'),
    ('Vice Secretary', 'Vice Secretary'),
    ('Organizing Secretary', 'Organizing Secretary'),
    ('Librarian', 'Librarian'),
    ('Missions Coordinator', 'Missions Coordinator'),
    ('Technical Coordinator', 'Technical Coordinator'),
    ('Music Director', 'Music Director'),
    ('Prayer Secretary', 'Prayer Secretary'),
    ('STEM Staff', 'STEM Staff'),
]

# Image category choices
IMAGE_CATEGORIES = [
    ('event', 'event'),
    ('service', 'service'),
    ('fellowship', 'fellowship'),
    ('outdoors', 'outdoors'),
]


# --------------------------
# Custom User
# --------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        send_welcome_email = extra_fields.pop('send_welcome_email', True)
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user._send_welcome_email = send_welcome_email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'developer')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(_('email'), unique=True)

    ROLE_CHOICES = [
        ('developer', 'developer'),
        ('member', 'member'),
        ('leader', 'leader'),
    ]

    USER_TYPE_CHOICES = [
        ('student', 'Current Student'),
        ('alumnus', 'Alumnus'),
    ]

    YEAR_OF_STUDY_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
        (5, 'Year 5'),
        (6, 'Year 6'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    userType = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    registrationNumber = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    homeCounty = models.CharField(max_length=50, default="county")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=100, default="full name")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    yearOfStudy = models.IntegerField(choices=YEAR_OF_STUDY_CHOICES, default=1, null=True, blank=True)
    graduationYear = models.IntegerField(null=True, blank=True)
    currentOccupation = models.CharField(max_length=100, null=True, blank=True)
    workplace = models.CharField(max_length=100, null=True, blank=True)

#-----------------------
#Onboad logic
#--------------------
    # --what new new member needs to fill before joining ---
    # by default a new users created needs to fill the form, so Set to True once the user has completed the firstlogin registration form.
    completed = models.BooleanField(default=False)
    # Forces a password change on the complete-registration page.
    must_change_password = models.BooleanField(default=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.phone}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.full_name or f"{self.first_name} {self.last_name}"

    @property
    def is_developer(self):
        return self.role == 'developer'

    @property
    def is_member(self):
        return self.role == 'member'

    @property
    def is_leader(self):
        return self.role == 'leader'

    class Meta:
        swappable = 'AUTH_USER_MODEL'


# --------------------------
# Notification
# --------------------------
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.email} - {self.message[:20]}"

# --------------------------
# Event
# --------------------------
class Event(models.Model):
    event_name = models.CharField(max_length=100)
    event_image = models.ImageField(upload_to='events', null=True, blank=True)
    start_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_date = models.DateField()
    end_time = models.TimeField(blank=True, null=True)
    event_description = models.TextField()
    event_venue = models.CharField(max_length=100)

    def __str__(self):
        start_time = f" {self.start_time}" if self.start_time else ""
        end_time = f" {self.end_time}" if self.end_time else ""
        return f"{self.event_name} ({self.start_date}{start_time} - {self.end_date}{end_time})"

    @property
    def is_future(self):
        return self.end_at >= timezone.now()

    def _combine_datetime(self, date_value, time_value, is_end=False):
        if not date_value:
            return None
        if time_value:
            combined = datetime.combine(date_value, time_value)
        else:
            combined = datetime.combine(
                date_value,
                time.max if is_end else time.min,
            )
        return timezone.make_aware(combined, timezone.get_current_timezone())

    @property
    def start_at(self):
        return self._combine_datetime(self.start_date, self.start_time, is_end=False)

    @property
    def end_at(self):
        return self._combine_datetime(self.end_date, self.end_time, is_end=True)

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at

    @property
    def is_upcoming(self):
        return timezone.now() < self.start_at

    def ongoing(self):
        return self.is_ongoing

    ongoing.boolean = True

# --------------------------
# Testimony
# --------------------------
class Testimony(models.Model):
    testimony_giver = models.CharField(max_length=100)
    image = models.ImageField(upload_to='testimonies', null=True)
    position = models.CharField(max_length=100, default='Member', blank=True)
    testimony = models.TextField()
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_testimonies',
    )
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Testimonies"

    def __str__(self):
        return f"{self.testimony_giver}'s testimony."

# --------------------------
# Exec
# --------------------------
class Exec(models.Model):
    spiritual_year = models.CharField(max_length=50)
    current_spiritual_year = models.CharField(max_length=50, default='2024/2025')
    group_image = models.ImageField(upload_to='execs', null=True, blank=True)
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            # Unset is_current on all other Exec records
            Exec.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.spiritual_year
# --------------------------
# Leader
# --------------------------
class Leader(models.Model):
    leader_name = models.CharField(max_length=150)
    leader_image = models.ImageField(upload_to='leaders')
    leader_position = models.CharField(max_length=150, choices=POSITIONS)
    leader_description = models.TextField(max_length=600)
    leader_contact = models.CharField(max_length=50)
    exec_year = models.ForeignKey(Exec, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.leader_position} - {self.exec_year}"

# --------------------------
# Ministry
# --------------------------
class Ministry(models.Model):
    ministry_name = models.CharField(max_length=100)
    ministry_image = models.ImageField(upload_to='ministries')
    ministry_description = models.TextField(max_length=600)
    ministry_chair_name = models.CharField(max_length=50)
    ministry_chair_number = models.CharField(max_length=50 , null=True)


    class Meta:
        verbose_name_plural = "ministries"

    def __str__(self):
        return self.ministry_name

# --------------------------
# Eteam
# --------------------------
class Eteam(models.Model):
    team_name = models.CharField(max_length=100)
    team_image = models.ImageField(upload_to='ministries')
    team_description = models.TextField(max_length=600)
    team_chair_name = models.CharField(max_length=50)

    def __str__(self):
        return self.team_name

# --------------------------
# Class
# --------------------------
class Class(models.Model):
    class_name = models.CharField(max_length=100)
    class_image = models.ImageField(upload_to='ministries')
    class_description = models.TextField(max_length=600)
    class_chair_name = models.CharField(max_length=50)   
    class_chair_number = models.CharField(max_length=50, null=True)   

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.class_name
    
# --------------------------
# Special Committes
# --------------------------

class SpecialCommittee(models.Model):
    committee_name = models.CharField(max_length=100)
    committee_image = models.ImageField(upload_to='ministries')
    committee_description = models.TextField(max_length=600)
    committee_chair = models.CharField(max_length=50)
    committee_chair_number = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Special Committee"
        verbose_name_plural = "Special Committees"

    def __str__(self):
        return self.committee_name

#---------------------------------
 # SEMESTER THEME SECTION  
#---------------------------------

class SemesterTheme(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=300)
    verse_reference = models.CharField(max_length=100)
    verse_text = models.TextField(max_length=250)
    spiritual_year = models.CharField(max_length=50)
    semester_number = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
# --------------------------
# Image
# --------------------------
class Image(models.Model):
    image = models.ImageField(upload_to='gallery')
    image_category = models.CharField(max_length=50, choices=IMAGE_CATEGORIES)
    image_to_show_on_website = models.BooleanField(default=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.image_category} - {self.id}"


# --------------------------
# PasswordReset
# --------------------------
class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    success_url = reverse_lazy('password_reset')

    def __str__(self):
        return f"password reset for {self.user.registrationNumber} at {self.created}"

# --------------------------
# Contact
# --------------------------
class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"message from {self.name}"
