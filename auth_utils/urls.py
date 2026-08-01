from django.urls import path
from . import views

app_name = 'auth_utils'

urlpatterns = [
    path('reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_sent'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/complete/', views.CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]