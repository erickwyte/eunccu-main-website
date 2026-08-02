from django.urls import path
from . import views

app_name = 'website'

handler404 = views.handler404

urlpatterns = [
    path('', views.index, name='home'),
    path('check-email/', views.check_email, name='check_email'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/past/', views.all_past_events, name='all_past_events'),
    path('about/', views.about, name='about'),
    path('constitution/', views.constitution, name='constitution'),
    path('privacy/', views.privacyPolicy, name='privacy'),
    path('contact/', views.contact, name='contact'),
    # Public self-registration is disabled — this URL redirects to login.
    path('register/', views.registration, name='register'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('leadership/', views.LeadershipView.as_view(), name='leadership'),
    path('ministries/', views.MinistriesView.as_view(), name='ministries'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('gallery/download/', views.download_drive_file_view, name='download_drive_file'),
    # Development-only: serve media at /media/... via debug view
    path('media/<path:path>', views.debug_media_serve, name='dev_media_serve'),
    # Debug-only media serve (temporary)
    path('media-files/<path:path>', views.debug_media_serve, name='debug_media_serve'),
    path('api/photos/', views.api_photos, name='api_photos'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('notifications/', views.UserNotificationsView.as_view(), name='user_notifications'),
    path('testimonies/submit/', views.submit_testimony, name='submit_testimony'),
    path('devotions/', views.devotion_list, name='devotion_list'),
    path('devotions/<slug:slug>/', views.devotion_detail, name='devotion_detail'),

    # --- First-login profile completion ---
    path('complete-registration/', views.CompleteRegistrationView.as_view(), name='complete_registration'),
    path(
        'complete-registration/<uidb64>/<token>/',
        views.CompleteRegistrationView.as_view(),
        name='complete_registration_token'
    ),

    # --- User Manager dashboard (User Manager group only) ---
    path('user-manager/', views.UserManagerDashboardView.as_view(), name='user_manager_dashboard'),
    path('user-manager/create/', views.CreateUserView.as_view(), name='user_manager_create'),
    path('user-manager/bulk-create/', views.BulkCreateUsersView.as_view(), name='user_manager_bulk_create'),
]
