import importlib
import os
import sys
import unittest
from unittest.mock import patch


class SettingsConfigWhitespaceTests(unittest.TestCase):
    def test_config_values_are_trimmed(self):
        env = {
            'SECRET_KEY': ' secret-key ',
            'DATABASE_NAME': ' db_name ',
            'DATABASE_USER': ' db_user ',
            'DATABASE_PASSWORD': ' db_password ',
            'DATABASE_HOST': ' localhost ',
            'DATABASE_PORT': '5432',
            'EMAIL_HOST_USER': ' no-reply@example.com ',
            'EMAIL_HOST_PASSWORD': ' password ',
            'NOTIFICATION_DELAY_SECONDS': '60',
            'SITE_URL': ' https://example.com ',
            'YOUTUBE_API_KEY': ' api-key ',
            'YOUTUBE_PLAYLIST_ID': ' playlist ',
            'YOUTUBE_REGION_CODE': ' KE ',
            'GOOGLE_DRIVE_ENABLED': 'True',
            'GOOGLE_DRIVE_FOLDER_ID': ' folder ',
            'GOOGLE_SERVICE_ACCOUNT_FILE': ' service.json ',
            'DEFAULT_TEMP_PASSWORD': ' temp ',
        }

        with patch.dict(os.environ, env, clear=False):
            sys.modules.pop('union.settings', None)
            settings = importlib.import_module('union.settings')

        self.assertEqual(settings.SECRET_KEY, 'secret-key')
        self.assertEqual(settings.DATABASES['default']['NAME'], 'db_name')
        self.assertEqual(settings.DATABASES['default']['USER'], 'db_user')
        self.assertEqual(settings.DATABASES['default']['PASSWORD'], 'db_password')
        self.assertEqual(settings.DATABASES['default']['HOST'], 'localhost')
        self.assertEqual(settings.DATABASES['default']['PORT'], 5432)
        self.assertEqual(settings.EMAIL_HOST_USER, 'no-reply@example.com')
        self.assertEqual(settings.EMAIL_HOST_PASSWORD, 'password')
        self.assertEqual(settings.SITE_URL, 'https://example.com')

    def test_get_config_value_does_not_send_cast_none(self):
        import union.settings as settings
        mock_config = unittest.mock.Mock(return_value='secret')

        with patch.object(settings, 'config', mock_config):
            value = settings.get_config_value('SECRET_KEY')

        self.assertEqual(value, 'secret')
        mock_config.assert_called_once_with('SECRET_KEY', default=None)

    def test_get_config_value_forwards_cast_when_present(self):
        import union.settings as settings
        mock_config = unittest.mock.Mock(return_value=42)

        with patch.object(settings, 'config', mock_config):
            value = settings.get_config_value('DATABASE_PORT', cast=int)

        self.assertEqual(value, 42)
        mock_config.assert_called_once_with('DATABASE_PORT', default=None, cast=int)


if __name__ == '__main__':
    unittest.main()
