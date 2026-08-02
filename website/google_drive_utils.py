"""
Google Drive Integration Utilities
Handles authentication, fetching photos, and downloading files from Google Drive
"""

import logging
import os
import io

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)
GOOGLE_DRIVE_METADATA_CACHE_TIMEOUT = 10 * 60


def _resolve_service_account_file(path):
    if not path:
        return None
    if os.path.isabs(path):
        return path
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        return os.path.join(base_dir, path)
    return path


def get_google_drive_service():
    """
    Initialize and return a Google Drive API service instance.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        raise ImproperlyConfigured(
            "Google API client not installed. "
            "Run: pip install google-api-python-client google-auth google-auth-httplib2"
        )

    if not getattr(settings, 'GOOGLE_DRIVE_ENABLED', False):
        logger.warning("Google Drive integration is disabled")
        return None

    folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', '')
    if not folder_id:
        raise ImproperlyConfigured("GOOGLE_DRIVE_FOLDER_ID is not set")

    service_account_file = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', '')
    service_account_file = _resolve_service_account_file(service_account_file)

    if not service_account_file or not os.path.exists(service_account_file):
        raise ImproperlyConfigured(
            f"Service account key file not found at {service_account_file}"
        )

    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive service: {str(e)}")
        raise ImproperlyConfigured(f"Google Drive authentication failed: {str(e)}")


def _collect_drive_folder_descendants(service, folder_id):
    """Collect all descendant folder IDs beneath a Drive folder."""
    if not folder_id:
        return []

    descendant_ids = []
    queue = [folder_id]

    while queue:
        current_folder_id = queue.pop(0)
        page_token = None

        while True:
            response = service.files().list(
                q=f"'{current_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageSize=100,
                pageToken=page_token,
            ).execute()

            for folder in response.get('files', []):
                folder_id = folder['id']
                descendant_ids.append(folder_id)
                queue.append(folder_id)

            page_token = response.get('nextPageToken')
            if not page_token:
                break

    return descendant_ids


def _build_drive_parents_query(folder_ids):
    if not folder_ids:
        return ''
    if len(folder_ids) == 1:
        return f"'{folder_ids[0]}' in parents"
    return ' or '.join([f"'{folder_id}' in parents" for folder_id in folder_ids])


def get_google_drive_photos(folder_id=None, page_size=100, page_token=None):
    """
    Fetch photos from the specified Google Drive folder only (no nested subfolders).
    """
    service = get_google_drive_service()
    if not service:
        return {'items': [], 'next_page_token': None}

    if not folder_id:
        folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', '')

    cache_key = f"google_drive_photos:{folder_id}:{page_size}:{page_token or 'root'}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"

        photos = []
        current_page_token = page_token

        while True:
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, thumbnailLink, webContentLink)',
                pageSize=page_size,
                orderBy='modifiedTime desc',
                pageToken=current_page_token,
            ).execute()

            for file in results.get('files', []):
                photos.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mimeType': file['mimeType'],
                    'size': int(file.get('size', 0)) if file.get('size') else 0,
                    'createdTime': file.get('createdTime'),
                    'modifiedTime': file.get('modifiedTime'),
                    'thumbnail': file.get('thumbnailLink', ''),
                    'preview_url': file.get('thumbnailLink', ''),
                    'download_url': None,
                })

            current_page_token = results.get('nextPageToken')
            if not current_page_token:
                break

        payload = {
            'items': photos,
            'next_page_token': None,
        }
        cache.set(cache_key, payload, GOOGLE_DRIVE_METADATA_CACHE_TIMEOUT)
        return payload
    except Exception as e:
        logger.error(f"Error fetching photos from Google Drive: {str(e)}")
        return {'items': [], 'next_page_token': None}


def _count_drive_folder_children(service, folder_id):
    """Count direct child folders and direct image files for a given folder."""
    folder_count = 0
    file_count = 0
    page_token = None

    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            spaces='drive',
            fields='nextPageToken, files(id, mimeType)',
            pageSize=100,
            pageToken=page_token,
        ).execute()

        for item in results.get('files', []):
            if item.get('mimeType') == 'application/vnd.google-apps.folder':
                folder_count += 1
            elif item.get('mimeType', '').startswith('image/'):
                file_count += 1

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return folder_count, file_count


def get_google_drive_folders(folder_id=None, page_size=50):
    """
    Fetch folders from a Google Drive folder and include direct child counts.
    """
    service = get_google_drive_service()
    if not service:
        return []

    if not folder_id:
        folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', '')

    cache_key = f"google_drive_folders:{folder_id}:{page_size}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)',
            pageSize=page_size
        ).execute()

        folders = []
        for file in results.get('files', []):
            folder_count, file_count = _count_drive_folder_children(service, file['id'])
            folders.append({
                'id': file['id'],
                'name': file['name'],
                'type': 'folder',
                'thumbnail': 'https://cdn-icons-png.flaticon.com/512/716/716784.png',
                'folder_count': folder_count,
                'file_count': file_count,
            })

        cache.set(cache_key, folders, GOOGLE_DRIVE_METADATA_CACHE_TIMEOUT)
        return folders
    except Exception as e:
        logger.error(f"Error fetching folders from Google Drive: {str(e)}")
        return []


def download_google_drive_file(file_id):
    """
    Download a file from Google Drive.
    """
    service = get_google_drive_service()
    if not service:
        return None

    try:
        file_metadata = service.files().get(
            fileId=file_id,
            fields='name, mimeType'
        ).execute()

        from googleapiclient.http import MediaIoBaseDownload

        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file_content.seek(0)
        return {
            'content': file_content,
            'name': file_metadata['name'],
            'mimeType': file_metadata['mimeType']
        }
    except Exception as e:
        logger.error(f"Error downloading file {file_id} from Google Drive: {str(e)}")
        return None


def get_file_info(file_id):
    """
    Get metadata for a specific file in Google Drive.
    """
    service = get_google_drive_service()
    if not service:
        return None

    try:
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, size, createdTime, modifiedTime, parents'
        ).execute()
        return file_metadata
    except Exception as e:
        logger.error(f"Error fetching file info for {file_id}: {str(e)}")
        return None


def get_drive_folder_breadcrumb(folder_id, root_folder_id=None):
    """Return breadcrumb path from root folder to the current folder."""
    service = get_google_drive_service()
    if not service or not folder_id:
        return []

    path = []
    current_folder_id = folder_id
    visited = set()

    while current_folder_id and current_folder_id not in visited:
        visited.add(current_folder_id)
        try:
            metadata = service.files().get(
                fileId=current_folder_id,
                fields='id, name, parents'
            ).execute()
        except Exception as e:
            logger.error(f"Error fetching breadcrumb metadata for {current_folder_id}: {str(e)}")
            break

        path.append({'id': metadata['id'], 'name': metadata.get('name', 'Folder')})

        if root_folder_id and current_folder_id == root_folder_id:
            break

        parents = metadata.get('parents') or []
        if not parents:
            break

        parent_id = parents[0]
        if root_folder_id and parent_id == root_folder_id:
            try:
                root_metadata = service.files().get(
                    fileId=parent_id,
                    fields='id, name'
                ).execute()
                path.append({'id': root_metadata['id'], 'name': root_metadata.get('name', 'Drive')})
            except Exception as e:
                logger.error(f"Error fetching root breadcrumb metadata for {parent_id}: {str(e)}")
            break

        current_folder_id = parent_id

    return list(reversed(path))
