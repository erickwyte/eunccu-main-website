from django.core.management.base import BaseCommand
from website.utils import test_youtube_playlist

class Command(BaseCommand):
    help = 'Test the YouTube playlist video fetching functionality'

    def handle(self, *args, **options):
        self.stdout.write('Starting YouTube playlist test...')
        
        if test_youtube_playlist():
            self.stdout.write(self.style.SUCCESS('✅ YouTube playlist test completed successfully'))
        else:
            self.stdout.write(self.style.ERROR('❌ YouTube playlist test failed')) 
