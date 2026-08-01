from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .forms import SharedPasswordResetForm, SharedPasswordSetForm

class CustomPasswordResetView(PasswordResetView):
    form_class = SharedPasswordResetForm
    template_name = 'auth_utils/password_reset_form.html'
    email_template_name = 'auth_utils/emails/password_reset_email.txt'
    success_url = reverse_lazy('auth_utils:password_reset_sent')  # Fixed URL name

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth_utils/password_reset_sent.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SharedPasswordSetForm
    template_name = 'auth_utils/password_reset_confirm.html'
    success_url = reverse_lazy('auth_utils:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth_utils/password_reset_complete.html'
    
def app_specific_404(request, exception):
    return render(request, 'website/404.html', status=404)