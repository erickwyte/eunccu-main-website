from django.contrib import admin
from django import forms
from .models import *
from django.utils.html import format_html
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from .utils import get_latest_youtube_video, schedule_notification_task
from .forms import CustomUserCreationForm
from .permissions import USER_MANAGER_GROUP, ensure_user_manager_group_exists
import logging
from django.http import HttpResponse
from django.template.response import TemplateResponse
import csv
from django.utils import timezone

class BulkEmailForm(forms.Form):
    """Plain form used on the dedicated 'send email' confirmation page.

    Deliberately NOT a subclass of admin.helpers.ActionForm: extending that
    form was what caused the admin user list to crash (KeyError: 'action')
    whenever Django rebuilt the changelist's action-choices field. Keeping
    this as an independent form removes that failure mode entirely.
    """
    subject = forms.CharField(
        required=True,
        label='Email subject',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
        initial='Message from EUNCCU',
    )
    message = forms.CharField(
        required=True,
        label='Email message',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your message...'}),
        initial='Hello, this is an important update. Please visit the provided link for more details.',
    )

    def clean_message(self):
        return self.cleaned_data['message'].strip()

    def clean_subject(self):
        return self.cleaned_data['subject'].strip()

    
# --- NEW IMPORTS FOR PDF GENERATION ---
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from io import BytesIO
# --------------------------------------

from .forms import ContactMessageReplyForm

# Set up logging
logger = logging.getLogger(__name__)


class TestimonyAdminForm(forms.ModelForm):
    image = forms.ImageField(required=True)

    class Meta:
        model = Testimony
        fields = '__all__'


def send_testimony_approval_notification(testimony_id):
    testimony = Testimony.objects.select_related('submitted_by').filter(pk=testimony_id).first()
    if testimony and testimony.submitted_by:
        Notification.objects.create(
            user=testimony.submitted_by,
            message='Your testimony has been approved and is now visible on the website.',
        )


@admin.action(description='Assign selected users to User Manager')
def assign_to_user_manager(modeladmin, request, queryset):
    group = ensure_user_manager_group_exists()
    updated = 0
    for user in queryset:
        if not user.groups.filter(pk=group.pk).exists():
            user.groups.add(group)
            updated += 1

    if updated:
        modeladmin.message_user(request, f'{updated} user(s) assigned to {USER_MANAGER_GROUP}.', level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, 'Selected users were already in the User Manager group.', level=messages.INFO)

# Define the county to E-Team mapping with multiple possible variations
COUNTY_TO_ETEAM = {
    # WESO
    'bungoma': 'WESO', 'busia': 'WESO', 'kakamega': 'WESO', 'vihiga': 'WESO',
    # NET
    'siaya': 'NET', 'kisumu': 'NET', 'homa bay': 'NET', 'homabay': 'NET', 'nyamira': 'NET', 'kisii': 'NET', 'migori': 'NET',
    # UET
    'marsabit': 'UET', 'mandera': 'UET', 'wajir': 'UET', 'garissa': 'UET', 'machakos': 'UET', 
    'taita taveta': 'UET', 'taita-taveta': 'UET', 'taitataveta': 'UET',
    'makueni': 'UET', 'kitui': 'UET', 
    'tana river': 'UET', 'tanariver': 'UET', 'tana-river': 'UET',
    'mombasa': 'UET', 'lamu': 'UET', 'kwale': 'UET', 'kilifi': 'UET', 'malindi': 'UET',
    # CET
    'nyandarua': 'CET', 'nyeri': 'CET', 'kirinyaga': 'CET', 'kirinyaga': 'CET',
    'muranga': 'CET', 'murang a': 'CET', 'muranga': 'CET', "murang'a": 'CET',
    'kiambu': 'CET', 'nairobi': 'CET',
    # MUBET
    'isiolo': 'MUBET', 'meru': 'MUBET', 
    'tharaka nithi': 'MUBET', 'tharaka-nithi': 'MUBET', 'tharakanithi': 'MUBET',
    # RIVET
    'turkana': 'RIVET', 'west pokot': 'RIVET', 'west-pokot': 'RIVET', 'westpokot': 'RIVET',
    'samburu': 'RIVET', 'baringo': 'RIVET', 'laikipia': 'RIVET', 'narok': 'RIVET', 'nakuru': 'RIVET', 
    'kajiado': 'RIVET', 'kajiado': 'RIVET',
    'trans nzoia': 'RIVET', 'trans-nzoia': 'RIVET', 'transnzoia': 'RIVET',
    'nandi': 'RIVET', 'bomet': 'RIVET', 'kericho': 'RIVET', 
    'uasin gishu': 'RIVET', 'uasin-gishu': 'RIVET', 'uasingishu': 'RIVET',
    'elgeyo marakwet': 'RIVET', 'elgeyo-marakwet': 'RIVET', 'elgeyomarakwet': 'RIVET',
    # EMUSETA
    'embu': 'EMUSETA'
}

def get_eteam(county_name):
    """
    SUPER robust function to get the E-Team for any county variation
    """
    if not county_name:
        return 'No County'
    
    # Extreme normalization: remove everything except letters and spaces, then lowercase
    import re
    normalized_county = re.sub(r'[^a-zA-Z\s]', '', county_name)  # Remove all non-letter, non-space characters
    normalized_county = normalized_county.strip().lower().replace('  ', ' ').replace('  ', ' ')
    
    # Try exact match first
    if normalized_county in COUNTY_TO_ETEAM:
        return COUNTY_TO_ETEAM[normalized_county]
    
    # Try with spaces removed (for cases like "TaitaTaveta")
    no_spaces = normalized_county.replace(' ', '')
    if no_spaces in COUNTY_TO_ETEAM:
        return COUNTY_TO_ETEAM[no_spaces]
    
    # Try common variations
    variations = [
        normalized_county,
        normalized_county.replace(' ', '-'),
        normalized_county.replace('-', ' '),
        normalized_county.replace("'", ""),
        normalized_county.replace("'", " "),
    ]
    
    for variation in variations:
        if variation in COUNTY_TO_ETEAM:
            return COUNTY_TO_ETEAM[variation]
    
    # Final fallback: try partial matching
    for key in COUNTY_TO_ETEAM.keys():
        if normalized_county in key or key in normalized_county:
            return COUNTY_TO_ETEAM[key]
    
    # If all else fails, return with the original name for debugging
    return f'Unknown County: {county_name}'

def export_users_to_csv(modeladmin, request, queryset):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_list_with_eteams.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the headers to the CSV file
    writer.writerow([
        'Full Name',
        'Email',
        'Phone Number',
        'County',
        'E-Team',  # New column for the E-Team
    ])

    # Loop through each selected user and write their data
    for user in queryset:
        writer.writerow([
            user.get_full_name(),  # Uses your custom method
            user.email,
            user.phone,
            user.homeCounty,
            get_eteam(user.homeCounty),  # Use the helper function to get the E-Team
        ])

    return response

# Add a short description for the action in the admin dropdown
export_users_to_csv.short_description = "Export selected users to CSV (with E-Teams)"

def export_users_to_pdf(modeladmin, request, queryset):
    # Create an HTTP Response object with PDF headers.
    response = HttpResponse(content_type='application/pdf')
    # Create a filename with a timestamp
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition'] = f'attachment; filename="eteam_members_directory_{date_str}.pdf"'

    # Create a buffer for the PDF data
    buffer = BytesIO()
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    # This is the container we will build the PDF content into
    elements = []

    # Define PDF Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=14, spaceAfter=20))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, fontSize=10))
    styles.add(ParagraphStyle(name='TableHeader', alignment=TA_LEFT, fontSize=10, fontName='Helvetica-Bold'))
    title_style = styles['Heading1']
    team_header_style = styles['Heading2']

    # 1. Add a Title to the PDF
    title_text = "E-TEAM MEMBERS DIRECTORY"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Add generation date
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(date_text, styles['Left']))
    elements.append(Spacer(1, 0.5 * inch))

    # 2. ORGANIZE THE DATA: Group users by their E-Team
    teams_dict = {}
    for user in queryset:
        team_name = get_eteam(user.homeCounty)
        if team_name not in teams_dict:
            teams_dict[team_name] = []
        teams_dict[team_name].append(user)

    # 3. BUILD THE PDF CONTENT WITH TABLES
    for team_name, user_list in teams_dict.items():
        # Add a header for the E-Team section
        elements.append(Paragraph(team_name, team_header_style))
        elements.append(Spacer(1, 0.2 * inch))

        if not user_list:
            elements.append(Paragraph("No members in this team", styles['Left']))
            elements.append(Spacer(1, 0.3 * inch))
            continue

        # Create table data
        table_data = []
        # Add table headers
        table_data.append(['Name', 'Phone Number', 'Email', 'County'])
        
        # Add user data rows
        for user in user_list:
            table_data.append([
                user.get_full_name(),
                user.phone,
                user.email,
                user.homeCounty if user.homeCounty else 'N/A'
            ])

        # Create the table
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 2.5*inch, 1.5*inch])
        
        # Add style to the table
        table.setStyle(TableStyle([
            # Header row style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c8e22')),  # Nice blue background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows style
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F2F2F2'), colors.white]),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D9D9D9')),
            
            # Header bottom border
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2F528F')),
        ]))
        
        # Add the table to the elements
        elements.append(table)
        elements.append(Spacer(1, 0.4 * inch))

        # Add member count for this team
        member_count = len(user_list)
        count_text = f"Total members: {member_count}"
        elements.append(Paragraph(count_text, styles['Left']))
        
        # Add a page break after each team's section
        elements.append(PageBreak())

    # Generate the PDF by building the elements
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

export_users_to_pdf.short_description = "Export selected users to PDF (Grouped by E-Team with Tables)"

def export_all_users_to_pdf(modeladmin, request, queryset):
    """
    Export selected users to a single general PDF (no E-Team grouping).
    """
    from datetime import datetime
    response = HttpResponse(content_type='application/pdf')
    date_str = datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition'] = f'attachment; filename="all_members_directory_{date_str}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    elements = []

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=14, spaceAfter=20))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, fontSize=10))
    styles.add(ParagraphStyle(name='TableHeader', alignment=TA_LEFT, fontSize=10, fontName='Helvetica-Bold'))
    title_style = styles['Heading1']

    # Title and metadata
    title_text = "EUNCCU GENERAL MEMBERS DIRECTORY"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 0.25 * inch))

    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(date_text, styles['Left']))
    elements.append(Spacer(1, 0.5 * inch))

    # --- Create one big general table ---
    table_data = [['Name', 'Phone Number', 'Email', 'County', 'E-Team']]

    for user in queryset:
        table_data.append([
            user.get_full_name(),
            user.phone or 'N/A',
            user.email or 'N/A',
            user.homeCounty or 'N/A',
            get_eteam(user.homeCounty),
        ])

    # Create and style table
    table = Table(table_data, colWidths=[2*inch, 1.5*inch, 2.5*inch, 1.2*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c8e22')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F2F2F2'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D9D9D9')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c8e22')),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # Add total member count
    count_text = f"Total members listed: {queryset.count()}"
    elements.append(Paragraph(count_text, styles['Left']))

    # Build the PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

# Label for the admin dropdown
export_all_users_to_pdf.short_description = "Export selected users to General PDF (All Members)"


# --- Now define your admin classes ---
class ContactAdmin(admin.ModelAdmin):
    form = ContactMessageReplyForm
    list_display = ('name', 'email', 'created_at', 'replied_status')
    readonly_fields = ('name', 'email', 'message')

    def save_model(self, request, obj, form, change):
        # If there's a reply, send it as an email
        if form.cleaned_data.get('reply'):
            try:
                send_mail(
                    subject=f"Re: Reply from Egerton CU",
                    message=form.cleaned_data['reply'],
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
                messages.success(request, f"Reply sent to {obj.email}")
                obj.reply = form.cleaned_data['reply']
                obj.replied = True
            except Exception as e:
                messages.error(request, f"Failed to send reply: {e}")
        super().save_model(request, obj, form, change)

    def replied_status(self, obj):
        if obj.replied:
            return format_html('<span style="color: green;" title="Replied">✔️</span>')
        else:
            return format_html('<span style="color: red;" title="Not Replied">❌</span>')

    replied_status.short_description = "Replied"

@admin.action(description='Refresh YouTube Video Cache')
def refresh_youtube_cache(modeladmin, request, queryset):
    """
    Admin action to manually refresh the YouTube video cache.
    Implementation moved here from views.py.
    """
    try:
        logger.info("Starting manual YouTube video cache refresh")
        
        # Clear the existing cache
        cache.delete('latest_youtube_video')
        logger.info("Cleared existing YouTube video cache")
        
        # Fetch new video data
        video_id, error = get_latest_youtube_video()
        
        if error:
            logger.error(f"Error refreshing YouTube cache: {error}")
            messages.error(request, f"Error refreshing cache: {error}")
        else:
            logger.info(f"Successfully refreshed YouTube cache with video ID: {video_id}")
            messages.success(request, "YouTube video cache refreshed successfully")
    except Exception as e:
        logger.exception("Unexpected error while refreshing YouTube cache")
        messages.error(request, f"Error refreshing cache: {str(e)}")

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_name',
        'start_date',
        'start_time',
        'end_date',
        'end_time',
        'event_venue',
        'ongoing',
    )
    list_filter = ('start_date', 'end_date', 'start_time', 'end_time')
    search_fields = ('event_name', 'event_venue', 'event_description')
    
    def colored_status(self, obj):
        if obj.end_date < timezone.now().date():
            color = 'gray'
            label = 'Past'
        else:
            color = 'green'
            label = 'Upcoming'
        return format_html('<b style="color: {};">{}</b>', color, label)
    
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'end_date'

    

@admin.action(description='Send email to selected users')
def send_email_to_selected_users(modeladmin, request, queryset):
    """Bulk-email the selected users.

    Two-step flow (same pattern Django's built-in 'delete_selected' uses):
      1. First pass (no confirmation yet): show a compose page with the
         recipient list, a subject field, and a message field.
      2. Second pass (form submitted on that page): actually send the email.

    This intermediate page is also what lets us show the user exactly who
    will receive the email and who will be skipped (missing email address)
    before anything is sent.
    """
    opts = modeladmin.model._meta

    recipients = [u for u in queryset if u.email]
    excluded = [u for u in queryset if not u.email]

    if not recipients:
        modeladmin.message_user(
            request,
            'None of the selected users have an email address on file.',
            level=messages.WARNING,
        )
        return None

    if request.POST.get('send_email_confirm') == 'yes':
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            recipient_list = [u.email for u in recipients]

            email = EmailMessage(subject=subject, body=message, from_email=from_email, bcc=recipient_list)
            email.content_subtype = 'html'
            try:
                email.send(fail_silently=False)
                modeladmin.message_user(
                    request,
                    f'Email sent to {len(recipient_list)} user{"s" if len(recipient_list) != 1 else ""}.',
                    level=messages.SUCCESS,
                )
            except Exception as e:
                logger.exception('Failed to send bulk email to selected users')
                modeladmin.message_user(request, f'Failed to send email: {e}', level=messages.ERROR)
            return None
        # Invalid form (e.g. blank subject/message) - fall through and
        # redisplay the compose page with the entered values and errors.
    else:
        form = BulkEmailForm()

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': 'Send email to selected users',
        'queryset': recipients,
        'excluded': excluded,
        'opts': opts,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'form': form,
        'media': modeladmin.media,
    }
    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(request, 'admin/send_email_confirmation.html', context)


# --- SINGLE, COMBINED CustomUserAdmin CLASS ---
class UserManagerFilter(admin.SimpleListFilter):
    title = 'User Manager status'
    parameter_name = 'user_manager'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'User Manager'),
            ('no', 'Not User Manager'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(groups__name=USER_MANAGER_GROUP)
        if self.value() == 'no':
            return queryset.exclude(groups__name=USER_MANAGER_GROUP)
        return queryset


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'get_full_name', 'phone', 'role', 'userType', 'is_user_manager', 'is_staff')
    list_filter = ('role', 'userType', 'groups', UserManagerFilter, 'is_staff', 'is_superuser', 'yearOfStudy', 'date_joined', 'homeCounty')
    search_fields = ('username', 'email', 'full_name', 'homeCounty')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'profile_picture', 'homeCounty')}),
        ('Academic Info', {'fields': ('registrationNumber', 'userType', 'yearOfStudy', 'graduationYear')}),
        ('Professional Info', {'fields': ('currentOccupation', 'workplace')}),
        ('Permissions', {
            'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'registrationNumber', 'homeCounty', 'userType', 'yearOfStudy', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    # ADD THE CUSTOM ACTIONS HERE
    actions = [
        refresh_youtube_cache,
        export_users_to_csv,
        export_users_to_pdf,       # Existing grouped-by-E-Team version
        export_all_users_to_pdf,   # New general all-members version
        send_email_to_selected_users,
        assign_to_user_manager,
    ]

    # Helper method for list display
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def is_user_manager(self, obj):
        return obj.groups.filter(name=USER_MANAGER_GROUP).exists()
    is_user_manager.boolean = True
    is_user_manager.short_description = 'User Manager'

    
    #-----Devotions page imports----
class DevotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'written_by', 'published_date', 'is_published')
    list_filter = ('is_published', 'published_date', 'written_by')
    search_fields = ('title', 'content', 'written_by')
    prepopulated_fields = {'slug': ('title',)}
    
    
@admin.action(description='Approve selected testimonies')
def approve_testimonies(modeladmin, request, queryset):
    approved_count = 0

    for testimony in queryset:
        if testimony.is_approved:
            continue

        testimony.is_approved = True
        testimony.reviewed_at = timezone.now()
        testimony.save(update_fields=['is_approved', 'reviewed_at'])
        approved_count += 1

        if testimony.submitted_by:
            schedule_notification_task(
                lambda testimony_id=testimony.pk: send_testimony_approval_notification(testimony_id)
            )

    if approved_count:
        messages.success(request, f'{approved_count} testimonies approved successfully.')
        return

    messages.info(request, 'The selected testimonies were already approved.')


class TestimonyAdmin(admin.ModelAdmin):
    form = TestimonyAdminForm
    changeform_format = 'horizontal_tabs'
    list_display = (
        'testimony_giver',
        'position',
        'submitted_by',
        'is_approved',
        'submitted_at',
        'reviewed_at',
    )
    list_filter = ('is_approved', 'submitted_at', 'reviewed_at')
    search_fields = ('testimony_giver', 'position', 'testimony', 'submitted_by__email')
    readonly_fields = ('submitted_by', 'submitted_at', 'reviewed_at')
    actions = [approve_testimonies]

    fieldsets = (
        ('Submission', {
            'classes': ('tab',),
            'fields': ('testimony_giver', 'position', 'testimony', 'image'),
        }),
        ('Review', {
            'classes': ('tab',),
            'fields': ('submitted_by', 'is_approved', 'submitted_at', 'reviewed_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        was_approved = False
        if change and obj.pk:
            previous = Testimony.objects.get(pk=obj.pk)
            was_approved = previous.is_approved

        approving_now = obj.is_approved and not was_approved
        if approving_now and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

        if approving_now and obj.submitted_by:
            schedule_notification_task(
                lambda testimony_id=obj.pk: send_testimony_approval_notification(testimony_id)
            )


class ExecAdmin(admin.ModelAdmin):
    list_display = ('spiritual_year', 'is_current')
    list_editable = ('is_current',) 

    
class SpecialCommitteeAdmin(admin.ModelAdmin):
    list_display = ('committee_name', 'committee_chair')
    search_fields = ('committee_name',)

class SemesterThemeAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'spiritual_year', 'semester_number')
    
    
# Register all admin classes
admin.site.register(SemesterTheme, SemesterThemeAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Ministry)
admin.site.register(Eteam)
admin.site.register(Class)
admin.site.register(Exec, ExecAdmin)
admin.site.register(Leader)
admin.site.register(Testimony, TestimonyAdmin)
admin.site.register(Image)
admin.site.register(PasswordReset)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Devotion, DevotionAdmin)
admin.site.register(SpecialCommittee, SpecialCommitteeAdmin)
admin.site.register(Notification)
