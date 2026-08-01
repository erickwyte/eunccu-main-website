# website/utils.py
import logging
import threading
from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import close_old_connections, transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string

def send_html_email(subject, to_email, template_name, context):
    html_content = render_to_string(template_name, context)
    plain_text = (
        f"Subject: {subject}\n\n"
        "This email contains HTML content. Please open it in an email client that supports HTML.\n\n"
        f"If you cannot view this email, please contact us at {settings.DEFAULT_FROM_EMAIL}."
    )
    msg = EmailMultiAlternatives(subject, plain_text, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def _run_deferred_task(task):
    logger = logging.getLogger(__name__)
    try:
        close_old_connections()
        task()
    except Exception:
        logger.exception("Deferred notification task failed")
    finally:
        close_old_connections()


def schedule_notification_task(task, delay_seconds=None):
    delay = (
        settings.NOTIFICATION_DELAY_SECONDS
        if delay_seconds is None
        else delay_seconds
    )

    def start_task():
        if delay <= 0:
            _run_deferred_task(task)
            return

        timer = threading.Timer(delay, _run_deferred_task, args=(task,))
        timer.daemon = True
        timer.start()

    transaction.on_commit(start_task)

class LoginRequiredWithMessageMixin(LoginRequiredMixin):
    """Universal mixin for all protected views"""
    login_message = "Please sign in to access this page."
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, self.login_message)
            # Store the FULL requested path (including query parameters)
            request.session['next'] = request.get_full_path()
            return redirect(self.get_login_url())
        return super().dispatch(request, *args, **kwargs)
        
def _region_allows_video(content_details, region_code):
    region = content_details.get('regionRestriction', {}) if content_details else {}
    allowed = region.get('allowed')
    blocked = region.get('blocked')
    if isinstance(allowed, list):
        return region_code in allowed
    if isinstance(blocked, list):
        return region_code not in blocked
    return True


def get_latest_youtube_video():
    """
    Fetches the latest embeddable public video from the configured YouTube playlist.
    Caches results for 4 hours to reduce API calls.

    Returns:
        tuple: (video_id, error_message)
    """
    logger = logging.getLogger(__name__)
    api_key = settings.YOUTUBE_API_KEY
    playlist_id = settings.YOUTUBE_PLAYLIST_ID
    region_code = getattr(settings, 'YOUTUBE_REGION_CODE', 'KE')

    cache_key = f"latest_youtube_video:{playlist_id or 'missing'}"
    cache_timeout = 4 * 60 * 60  # 6 hours

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data.get('video_id'), cached_data.get('error')

    if not api_key or not playlist_id:
        error_msg = "YouTube API credentials not configured"
        cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
        logger.warning("YouTube API credentials missing")
        return None, error_msg

    try:
        playlist_response = requests.get(
            'https://www.googleapis.com/youtube/v3/playlistItems',
            params={
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': 20,
                'key': api_key,
            },
            timeout=10,
        )

        if playlist_response.status_code != 200:
            error_msg = f"YouTube API returned status code {playlist_response.status_code}"
            cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
            logger.error("YouTube playlist API error: %s", playlist_response.text)
            return None, error_msg

        playlist_items = playlist_response.json().get('items') or []
        if not playlist_items:
            error_msg = "No videos found in the playlist"
            cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
            logger.warning("YouTube playlist is empty")
            return None, error_msg

        candidates = []
        for item in playlist_items:
            snippet = item.get('snippet', {})
            resource = snippet.get('resourceId', {})
            video_id = resource.get('videoId')
            if video_id:
                candidates.append((video_id, snippet))

        if not candidates:
            error_msg = "Video IDs not found in playlist response"
            cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
            logger.error("Playlist response missing video IDs")
            return None, error_msg

        candidate_ids = [video_id for video_id, _ in candidates]
        videos_response = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            params={
                'part': 'status,contentDetails',
                'id': ','.join(candidate_ids),
                'key': api_key,
            },
            timeout=10,
        )

        if videos_response.status_code != 200:
            error_msg = f"YouTube API returned status code {videos_response.status_code}"
            cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
            logger.error("YouTube videos API error: %s", videos_response.text)
            return None, error_msg

        status_items = videos_response.json().get('items') or []
        status_map = {
            item.get('id'): {
                'status': item.get('status', {}),
                'contentDetails': item.get('contentDetails', {}),
            }
            for item in status_items
        }

        chosen_id = None
        chosen_snippet = None
        for candidate_id, candidate_snippet in candidates:
            info = status_map.get(candidate_id, {})
            status = info.get('status', {})
            content_details = info.get('contentDetails', {})

            if (
                status.get('privacyStatus') == 'public'
                and status.get('embeddable')
                and _region_allows_video(content_details, region_code)
            ):
                chosen_id = candidate_id
                chosen_snippet = candidate_snippet
                break

        if not chosen_id:
            error_msg = "No embeddable public videos found in playlist"
            cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
            logger.warning("No embeddable public videos found in playlist")
            return None, error_msg

        cache.set(
            cache_key,
            {
                'video_id': chosen_id,
                'error': None,
                'title': chosen_snippet.get('title') if chosen_snippet else None,
                'description': chosen_snippet.get('description') if chosen_snippet else None,
                'published_at': chosen_snippet.get('publishedAt') if chosen_snippet else None,
                'fetched_at': datetime.now().isoformat(),
            },
            cache_timeout,
        )

        return chosen_id, None

    except requests.exceptions.Timeout:
        error_msg = "Request to YouTube API timed out"
        cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
        logger.warning("YouTube API request timed out")
        return None, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching YouTube video: {str(e)}"
        cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
        logger.exception("YouTube API request failed")
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        cache.set(cache_key, {'video_id': None, 'error': error_msg}, cache_timeout)
        logger.exception("Unexpected error fetching YouTube video")
        return None, error_msg


def test_youtube_playlist():
    """
    Smoke test to verify YouTube playlist video fetching.
    """
    video_id, error = get_latest_youtube_video()
    if error:
        print(f"\n❌ YouTube playlist test failed: {error}")
        return False
    print(f"\n✅ YouTube playlist test succeeded. Video ID: {video_id}")
    return True
