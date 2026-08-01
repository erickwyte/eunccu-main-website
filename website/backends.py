from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Look for a user with the provided email
            user = User.objects.get(email=email)
            # Check the password and return the user if it's correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class CustomUserAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

