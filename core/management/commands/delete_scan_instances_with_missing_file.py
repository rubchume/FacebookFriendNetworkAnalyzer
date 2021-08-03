from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from core.models import ScanInstance


class Command(BaseCommand):
    help = 'Deletes all scan instances with missing files'

    def handle(self, *args, **options):
        for scan in ScanInstance.objects.all():
            self.stdout.write("Scan:")
            self.stdout.write(f" user: {scan.user}")
            if not scan.file:
                self.stdout.write(" Removing")
                scan.delete()

            media_path = Path(settings.MEDIA_ROOT)
            file_path = media_path.joinpath(scan.file.name)

            if not file_path.exists():
                self.stdout.write(" Removing")
                scan.delete()

        self.stdout.write(self.style.SUCCESS("Successfully deleted scan instances with missing files"))
