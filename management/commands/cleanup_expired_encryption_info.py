from django.core.management.base import BaseCommand
from django.utils import timezone
from encryption_verification.models import EncryptionInfo

class Command(BaseCommand):
    help = 'Cleanup expired EncryptionInfo records'

    def handle(self, *args, **options):
        current_time = timezone.now()
        expired_records = EncryptionInfo.objects.filter(expiration_time__lt=current_time)
        expired_records.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {len(expired_records)} expired records.'))