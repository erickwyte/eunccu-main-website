"""
Views for the website application.
This module contains all the view functions that handle HTTP requests and responses.
"""

from dj_database_url import config
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import get_random_string
import os
from django.http import JsonResponse, HttpResponse
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import DisallowedHost, ImproperlyConfigured
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import TemplateView
from .models import (
    Event, Testimony, Leader, Ministry, Eteam, 
    Image, Contact, Class, Notification, Exec, SpecialCommittee,
    SemesterTheme
    
)
from .models import Devotion
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .forms import ProfileForm, ChangePasswordForm
from .forms import TestimonySubmissionForm
from .forms import OnboardUserForm, CompleteRegistrationForm
from datetime import date
from website.utils import (
    LoginRequiredWithMessageMixin,
    get_latest_youtube_video,
    schedule_notification_task,
    send_html_email,
)
from .decorators import user_manager_required, UserManagerMixin
from .permissions import is_user_manager
from .google_drive_utils import (
    get_google_drive_folders,
    get_google_drive_photos,
    download_google_drive_file,
    get_file_info,
    get_drive_folder_breadcrumb,
)
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
User = get_user_model()


def generate_temp_password(length=12):
    return get_random_string(length=length)


def build_absolute_url(request, path):
    try:
        return request.build_absolute_uri(path)
    except DisallowedHost:
        site_url = getattr(settings, 'SITE_URL', None)
        if site_url:
            return f"{site_url.rstrip('/')}{path}"
        raise


def build_complete_registration_link(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return build_absolute_url(
        request,
        reverse('website:complete_registration_token', kwargs={'uidb64': uidb64, 'token': token}),
    )


#-- DEVOTIONS VIEWS --
import logging

logger = logging.getLogger(__name__)


def send_testimony_review_notifications(testimony_id, admin_user_ids, review_url):
    testimony = Testimony.objects.filter(pk=testimony_id).first()
    if not testimony:
        return

    admin_users = list(User.objects.filter(pk__in=admin_user_ids))
    notifications = [
        Notification(
            user=admin_user,
            message=(
                f"{testimony.testimony_giver} submitted a testimony that needs review in the admin panel."
            ),
        )
        for admin_user in admin_users
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)

    admin_emails = [admin_user.email for admin_user in admin_users if admin_user.email]
    if admin_emails:
        send_mail(
            subject='Testimony review required',
            message=(
                f"{testimony.testimony_giver} submitted a new testimony that needs admin review.\n\n"
                f"Review it here: {review_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=True,
        )


def _build_home_context(testimony_form=None):
    today = date.today()
    video_id, video_error = get_latest_youtube_video()

    return {
        'semester_theme': SemesterTheme.objects.filter(is_active=True).first(),
        'slider_devotions': list(
            Devotion.objects.filter(is_published=True).order_by('-published_date')[:3]
        ),
        'recent_events': Event.objects.all().order_by('-start_date')[:3],
        'upcoming_events': Event.objects.filter(end_date__gte=today).order_by('start_date')[:3],
        'testimonies': Testimony.objects.filter(is_approved=True).order_by('-reviewed_at', '-id')[:3],
        'today': today,
        'current_date': today.strftime("%B %d, %Y"),
        'video_id': video_id,
        'playlist_id': settings.YOUTUBE_PLAYLIST_ID,
        'video_error': video_error,
        'testimony_form': testimony_form or TestimonySubmissionForm(),
    }


def devotion_list(request):
    all_devotions = Devotion.objects.filter(is_published=True).order_by('-published_date')
    return render(request, 'website/devotions.html', {'all_devotions': all_devotions})  #  devotions_list path


def devotion_detail(request, slug):
    devotion = get_object_or_404(Devotion, slug=slug, is_published=True)
    related_devotions = (
        Devotion.objects.filter(is_published=True)
        .exclude(id=devotion.id)
        .order_by('-published_date')[:3]
    )
    context = {'devotion': devotion, 'related_devotions': related_devotions}
    return render(request, 'website/devotions_detail.html', context)



#====================================
    #Index Views
#=====================================

def index(request):
    try:
        return render(request, 'website/index.html', _build_home_context())

    except Exception as e:
        logger.error("Error in index view: %s", str(e))
        return render(request, 'website/index.html', {
            'slider_devotions': [],
            'recent_events': [],
            'upcoming_events': [],
            'testimonies': [],
            'testimony_form': TestimonySubmissionForm(),
        })


@login_required
def submit_testimony(request):
    if request.method != 'POST':
        return redirect('website:home')

    form = TestimonySubmissionForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Please correct the errors below and submit your testimony again.')
        return render(request, 'website/index.html', _build_home_context(testimony_form=form))

    testimony = form.save(commit=False)
    full_name = (request.user.get_full_name() or '').strip()
    testimony.testimony_giver = full_name or request.user.username or request.user.email
    testimony.position = request.user.currentOccupation or ('Leader' if request.user.is_leader else 'Member')
    testimony.submitted_by = request.user
    testimony.is_approved = False
    testimony.save()

    admin_user_ids = list(
        User.objects.filter(Q(is_staff=True) | Q(role='developer'))
        .values_list('pk', flat=True)
        .distinct()
    )
    review_url = request.build_absolute_uri(reverse('admin:website_testimony_changelist'))
    schedule_notification_task(
        lambda testimony_id=testimony.pk, admin_ids=admin_user_ids, url=review_url: (
            send_testimony_review_notifications(testimony_id, admin_ids, url)
        )
    )

    messages.success(
        request,
        'Your testimony has been submitted and is waiting for admin approval before it appears on the site.',
    )
    return redirect('website:home')

def handler404(request, exception):
    context = {
        'exception': str(exception),
        'request_path': request.path,
    }
    return render(request, '404.html', context, status=404)

def events(request):
    """
    Main events page showing both upcoming and past events
    """
    try:
        today = date.today()
        
        # Upcoming or ongoing events (end_date is today or in the future)
        upcoming_events = Event.objects.filter(
            end_date__gte=today
        ).order_by('start_date')
        
        # Past events (end_date is before today)
        past_events = Event.objects.filter(
            end_date__lt=today
        ).order_by('-start_date')[:6]  # Limit to 6 most recent past events
        
        # Paginate upcoming events
        paginator = Paginator(upcoming_events, 6)
        page_number = request.GET.get('page')
        
        try:
            upcoming_events_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            upcoming_events_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page
            upcoming_events_page = paginator.page(paginator.num_pages)
        
        context = {
            'upcoming_events': upcoming_events_page,
            'past_events': past_events,
            'total_upcoming': upcoming_events.count(),  # Count before pagination
            'total_past': past_events.count(),
            'today': today,
        }
        
        return render(request, 'website/events.html', context)  # Changed template
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        # Return empty context on error
        return render(request, 'website/events.html', {  
            'upcoming_events': [],
            'past_events': [],
            'total_upcoming': 0,
            'total_past': 0,
            'today': date.today(),
        })

def event_detail(request, event_id):
    """
    Detail view for a specific event
    """
    try:
        event = get_object_or_404(Event, id=event_id)
        today = date.today()
        
        # Get related events (same venue or upcoming events, exclude current)
        related_events = Event.objects.filter(
            Q(event_venue=event.event_venue) | 
            Q(end_date__gte=today)
        ).exclude(id=event_id).distinct().order_by('start_date')[:3]
        
        context = {
            'event': event,
            'related_events': related_events,
            'is_upcoming': event.end_date >= today,
            'today': today,
        }
        
        return render(request, 'website/event_detail.html', context)  # Changed template
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('website:events')

def all_past_events(request):
    """
    View all past events in a paginated list
    """
    try:
        today = date.today()
        past_events = Event.objects.filter(
            end_date__lt=today
        ).order_by('-start_date')
        
        paginator = Paginator(past_events, 12)
        page_number = request.GET.get('page')
        
        try:
            events_page = paginator.page(page_number)
        except PageNotAnInteger:
            events_page = paginator.page(1)
        except EmptyPage:
            events_page = paginator.page(paginator.num_pages)
        
        context = {
            'upcoming_events': events_page,
            'total_upcoming': past_events.count(),
            'total_past': 0,
            'page_title': 'All Past Events',
            'today': today,
        }
        
        return render(request, 'website/events.html', context)  # Changed template
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('website:events')
    
    



class LeadershipView(TemplateView):
    template_name = 'website/Leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all exec years (ordered for dropdown)
        exec_years = Exec.objects.all().order_by('-id')
        
        # Determine selected year
        year_str = self.request.GET.get('year')
        if year_str:
            try:
                selected_exec = Exec.objects.filter(spiritual_year=year_str).first() #get(spiritual_year=year_str)
            except Exec.DoesNotExist:
                # If year not found, fallback to current year or first
                selected_exec = Exec.objects.filter(is_current=True).first()
                if not selected_exec:
                    selected_exec = exec_years.first()
        else:
            # No year parameter: use current year if set, else first
            selected_exec = Exec.objects.filter(is_current=True).first()
            if not selected_exec:
                selected_exec = exec_years.first()
        
        # Filter leaders by selected exec
        if selected_exec:
            leaders = Leader.objects.filter(exec_year=selected_exec)
        else:
            leaders = Leader.objects.none()
        
        # Pagination
        paginator = Paginator(leaders, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add to context
        context['page_obj'] = page_obj
        context['exec_years'] = exec_years
        context['selected_exec'] = selected_exec
        
        return context
    


class MinistriesView(TemplateView): #LoginRequiredWithMessageMixin
    template_name = 'website/Ministries.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'ministries': Ministry.objects.all(),
            'eteams': Eteam.objects.all(),
            'classes': Class.objects.all(),
            'committees': SpecialCommittee.objects.all(),
        })
        return context

class GalleryView(TemplateView):
    template_name = 'website/gallery.html'

    def get(self, request, *args, **kwargs):
        """Require login when accessing Google Drive source."""
        active_source = request.GET.get('source', 'local')
        if active_source == 'google-drive' and not request.user.is_authenticated:
            # Redirect anonymous users to login with a `next` back to the gallery
            login_url = reverse('website:login')
            next_url = request.get_full_path()
            return redirect(f"{login_url}?next={next_url}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        images = Image.objects.filter(image_to_show_on_website=True).order_by('-uploaded_at')
        paginator = Paginator(images, 9)
        page_number = self.request.GET.get('page')

        active_source = self.request.GET.get('source', 'local')
        active_folder_id = self.request.GET.get('folder', '')

        context.update({
            'page_obj': paginator.get_page(page_number),
            'active_source': active_source,
            'drive_enabled': getattr(settings, 'GOOGLE_DRIVE_ENABLED', False),
            'drive_folders': [],
            'drive_photos': [],
            'drive_error': None,
            'active_folder_id': active_folder_id,
            'active_folder_name': None,
            'breadcrumb_path': [],
            'drive_next_page_token': None,
        })

        if active_source == 'google-drive':
            if context['drive_enabled']:
                try:
                    # Always fetch folders (regardless of whether we're in a folder or root)
                    folder_id = active_folder_id or None
                    context['drive_folders'] = get_google_drive_folders(folder_id)
                    
                    # CRITICAL FIX: Only fetch photos when a folder is selected
                    # This prevents showing root-level photos
                    if folder_id:
                        # User is inside a folder - fetch photos from this folder
                        photos_payload = get_google_drive_photos(folder_id)
                        context['drive_photos'] = photos_payload.get('items', [])
                        context['drive_next_page_token'] = photos_payload.get('next_page_token')
                        
                        # Get folder info for breadcrumb
                        folder_info = get_file_info(folder_id)
                        context['active_folder_name'] = folder_info.get('name') if folder_info else None
                        context['breadcrumb_path'] = get_drive_folder_breadcrumb(
                            folder_id, 
                            getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', None)
                        )
                    else:
                        # User is at root - only show folders, NO photos
                        context['drive_photos'] = []
                        context['active_folder_name'] = None
                        context['breadcrumb_path'] = []
                        
                except ImproperlyConfigured as exc:
                    context['drive_error'] = str(exc)
                except Exception as e:
                    context['drive_error'] = "Unable to load Google Drive content. Please try again later."
                    logger.error(f"Google Drive error: {str(e)}")
            else:
                context['drive_error'] = "Google Drive integration is disabled."

        return context
    
def api_photos(request):
    """
    API endpoint for fetching photos with filtering and searching.
    Supports pagination, category filtering, and search functionality.
    """
    from django.db.models import Q
    
    # Get query parameters
    page = request.GET.get('page', 1)
    filter_type = request.GET.get('filter', '*')
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset
    photos = Image.objects.filter(image_to_show_on_website=True)
    
    # Apply category filter
    if filter_type != '*':
        photos = photos.filter(image_category=filter_type)
    
    # Apply search filter
    if search_query:
        photos = photos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(image_category__icontains=search_query)
        )
    
    # Order by upload date (newest first)
    photos = photos.order_by('-uploaded_at')
    
    # Paginate
    paginator = Paginator(photos, 9)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    
    # Serialize photos
    photos_data = []
    for photo in page_obj:
        photos_data.append({
            'id': photo.id,
            'url': photo.image.url,
            'thumb': photo.image.url,
            'title': photo.title or photo.get_image_category_display(),
            'category': photo.image_category,
            'date': photo.uploaded_at.strftime('%b %d, %Y'),
        })
    
    return JsonResponse({
        'photos': photos_data,
        'has_more': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
    })


@login_required
def download_drive_file_view(request):
    file_id = request.GET.get('id')
    if not file_id:
        return JsonResponse({'error': 'Missing file id'}, status=400)

    if not getattr(settings, 'GOOGLE_DRIVE_ENABLED', False):
        return JsonResponse({'error': 'Google Drive integration is disabled.'}, status=400)

    file_data = download_google_drive_file(file_id)
    if not file_data:
        return JsonResponse({'error': 'Unable to download the requested file.'}, status=500)

    preview_mode = request.GET.get('preview') in ['1', 'true', 'True']
    file_data['content'].seek(0)
    response = HttpResponse(
        file_data['content'].read(),
        content_type=file_data['mimeType'] or 'application/octet-stream'
    )
    disposition_type = 'inline' if preview_mode else 'attachment'
    response['Content-Disposition'] = f'{disposition_type}; filename="{file_data["name"]}"'
    return response


def debug_media_serve(request, path):
    """Temporary debug endpoint to serve files from MEDIA_ROOT for diagnosis.
    Access as `/media-files/<path>` (example: `/media-files/gallery/images.jpg`).
    Remove this in production.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(full_path):
        raise Http404("File not found")
    return FileResponse(open(full_path, 'rb'))


def registration(request):
    """
    Public self-registration is disabled.
    All new user accounts are created by User Manager members through the
    internal dashboard at /user-manager/create/.
    """
    messages.info(
        request,
        'Self-registration is not available. Please contact an administrator to create your account.'
    )
    return redirect('website:login')

def check_email(request):
    email = request.GET.get('email', '')
    exists = get_user_model().objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

def userlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please enter both email and password")
            return redirect('website:login')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.session.pop('next', None)
            # Redirect to profile completion if the user has not yet finished onboarding.
            if not user.completed and not user.is_superuser and not user.is_staff:
                return redirect('website:complete_registration')
            if next_url:
                return redirect(next_url)
            return redirect('website:home')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('website:login')

    # GET request - pass `next` from query params
    next_url = request.GET.get('next')
    return render(request, 'website/login.html', {'next': next_url})

def about(request):
    """Render the about page"""
    return render(request, 'website/about.html')
    
def constitution(request):      #TO RENDER CONSTITUTION.HTML
    return render(request, 'website/constitution.html')


def logout_view(request):
	logout(request)
	return redirect('website:login')
	

def privacyPolicy(request):
    return render(request, 'website/privacy-policy.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contact = Contact.objects.create(
        name=name,
        email=email,
        message=message)
        contact.save()
        messages.success(request, "Message received")
        return redirect('website:home')
    return render(request, 'website/contact.html')



class EditProfileView(LoginRequiredWithMessageMixin, TemplateView):
    template_name = 'website/edit_profile.html'
    
    def get_context_data(self, **kwargs):
        return {'user': self.request.user}
    
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            # Update basic info
            user.username = request.POST.get('username', user.username)
            user.full_name = request.POST.get('full_name', user.full_name)
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)
            user.homeCounty = request.POST.get('homeCounty', user.homeCounty)
            
            # Handle profile picture
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('website:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return self.render_to_response({'user': user})

class ProfileView(LoginRequiredWithMessageMixin, TemplateView):
    template_name = 'website/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'full_name': user.full_name,
            'email': user.email,
            'registrationNumber': user.registrationNumber,
            'phone': user.phone,
            'homeCounty': user.homeCounty,
            'change_password_form': kwargs.get('change_password_form') or ChangePasswordForm(user=user),
        })
        return context

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('website:profile')

        context = self.get_context_data(**kwargs)
        context['change_password_form'] = form
        return render(request, self.template_name, context)


class UserNotificationsView(LoginRequiredWithMessageMixin,TemplateView):
    template_name = 'website/notifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')
        return context


# ---------
# User Manager Dashboard adn the new code
# -----------

class UserManagerDashboardView(UserManagerMixin, TemplateView):
    
    #Central dashboard for User Manager group members
    template_name = 'website/user_manager/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()

        pending_users = User.objects.filter(completed=False).order_by('-date_joined')
        if search_query:
            pending_users = pending_users.filter(
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(registrationNumber__icontains=search_query)
            )

        paginator = Paginator(pending_users, 15)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        from django.utils import timezone as tz
        now = tz.now()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        context.update({
            'page_obj': page_obj,
            'search_query': search_query,
            'total_users': User.objects.count(),
            'new_this_month': User.objects.filter(date_joined__gte=first_of_month, completed=False).count(),
            'incomplete_profiles': pending_users.count() if not search_query else User.objects.filter(completed=False).count(),
            'create_form': OnboardUserForm(),
        })
        return context


class CreateUserView(UserManagerMixin, TemplateView):
   
    template_name = 'website/user_manager/create_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = OnboardUserForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OnboardUserForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'create_form': form})

        data = form.cleaned_data
        temp_password = generate_temp_password(12)
        username = OnboardUserForm._generate_username(data['email'])

        new_user = User.objects.create_user(
            username=username,
            email=data['email'],
            full_name=data['full_name'],
            registrationNumber=data.get('registrationNumber') or None,
            password=temp_password,
            is_active=True,
            completed=False,
            must_change_password=True,
            send_welcome_email=False,
        )

        # Send onboarding email with credentials and instructions.
        login_url = build_absolute_url(request, reverse('website:login'))
        complete_registration_url = build_complete_registration_link(request, new_user)
        try:
            send_html_email(
                subject='Welcome Your Account Has Been Created',
                to_email=new_user.email,
                template_name='website/emails/onboarding_email.html',
                context={
                    'user': new_user,
                    'temp_password': temp_password,
                    'login_url': login_url,
                    'action_url': complete_registration_url,
                },
            )
            messages.success(
                request,
                f'Account created for {new_user.full_name}. An onboarding email has been sent to {new_user.email}.'
            )
        except Exception:
            logger.exception('Failed to send onboarding email to %s', new_user.email)
            messages.warning(
                request,
                f'Account created for {new_user.full_name}, but the onboarding email could not be sent. '
                f'Please share the credentials manually.'
            )

        return redirect('website:user_manager_dashboard')


class BulkCreateUsersView(UserManagerMixin, TemplateView):
    template_name = 'website/user_manager/dashboard.html'

    def post(self, request, *args, **kwargs):
        import json
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

        rows = payload if isinstance(payload, list) else []
        if not rows:
            return JsonResponse({'error': 'No user rows provided.'}, status=400)

        login_url = build_absolute_url(request, reverse('website:login'))
        temp_password = getattr(settings, 'DEFAULT_TEMP_PASSWORD', 'student')

        results = []
        for i, row in enumerate(rows):
            full_name = (row.get('full_name') or '').strip()
            email = (row.get('email') or '').strip().lower()
            reg_no = (row.get('registrationNumber') or '').strip() or None

            if not full_name or not email:
                results.append({'row': i + 1, 'email': email or '—', 'status': 'skipped', 'reason': 'Missing name or email.'})
                continue

            if User.objects.filter(email=email).exists():
                results.append({'row': i + 1, 'email': email, 'status': 'skipped', 'reason': 'Email already registered.'})
                continue

            if reg_no and User.objects.filter(registrationNumber=reg_no).exists():
                results.append({'row': i + 1, 'email': email, 'status': 'skipped', 'reason': f'Reg number {reg_no} already in use.'})
                continue

            try:
                temp_password = generate_temp_password(12)
                username = OnboardUserForm._generate_username(email)
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    full_name=full_name,
                    registrationNumber=reg_no,
                    password=temp_password,
                    is_active=True,
                    completed=False,
                    must_change_password=True,
                    send_welcome_email=False,
                )
                try:
                    send_html_email(
                        subject='Welcome! Your EUNCCU Account Has Been Created',
                        to_email=new_user.email,
                        template_name='website/emails/onboarding_email.html',
                        context={
                            'user': new_user,
                            'temp_password': temp_password,
                            'login_url': login_url,
                            'action_url': build_complete_registration_link(request, new_user),
                        },
                    )
                    email_sent = True
                except Exception:
                    logger.exception('Bulk onboarding email failed for %s', new_user.email)
                    email_sent = False

                results.append({
                    'row': i + 1,
                    'email': email,
                    'full_name': full_name,
                    'status': 'created',
                    'email_sent': email_sent,
                })
            except Exception as exc:
                logger.exception('Bulk user creation failed for row %d (%s)', i + 1, email)
                results.append({'row': i + 1, 'email': email, 'status': 'error', 'reason': str(exc)})

        created = [r for r in results if r['status'] == 'created']
        return JsonResponse({'results': results, 'created_count': len(created), 'total': len(rows)})


# -----
# Complete Registration
# -----

class CompleteRegistrationView(TemplateView):
    """
    my notes---- to website manager
    ---
    it handles the firstlogin profile completion flow.

    Requires the user to be authenticated. Users who have already completed
    their profile are redirected to the home page immediately n not the cpmplete form
    After a successful submission the user's profile is marked complete/true and
    they are redirected to the home page.
    """
    template_name = 'website/complete_registration.html'

    def dispatch(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')

        if not request.user.is_authenticated:
            if uidb64 and token:
                try:
                    uid = force_str(urlsafe_base64_decode(uidb64))
                    user = User._default_manager.get(pk=uid)
                except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                    user = None

                if user and default_token_generator.check_token(user, token):
                    if user.is_active and not user.completed:
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return super().dispatch(request, *args, **kwargs)
                messages.error(
                    request,
                    'Your registration link is invalid or has expired. Please ask an administrator to resend your onboarding email.'
                )
                return redirect('website:login')

            messages.warning(request, 'Please sign in to access this page.')
            return redirect('website:login')

        if request.user.completed:
            return redirect('website:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CompleteRegistrationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CompleteRegistrationForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        data = form.cleaned_data
        user = request.user

        # Update profile fields.
        user.phone = data.get('phone') or user.phone
        user.homeCounty = data.get('homeCounty') or user.homeCounty
        user.userType = data.get('userType', user.userType)
        user.currentOccupation = data.get('currentOccupation') or user.currentOccupation
        user.workplace = data.get('workplace') or user.workplace

        year_of_study = data.get('yearOfStudy')
        if year_of_study:
            try:
                user.yearOfStudy = int(year_of_study)
            except (ValueError, TypeError):
                pass

        graduation_year = data.get('graduationYear')
        if graduation_year:
            user.graduationYear = graduation_year

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        # Set the new password.
        user.set_password(data['new_password'])

        # Mark the profile as complete.
        user.completed = True
        user.must_change_password = False
        user.save()

        # Reauthenticate so the session remains valid after the password change.
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        messages.success(request, 'Registration complete. Welcome to the platform!')
        return redirect('website:home')
