import os
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.test import override_settings, TestCase

from core.models import ScanInstance


@override_settings(
    MEDIA_ROOT=os.path.join("tests", "helpers", "media")
)
class CleanInstancesCommandTests(TestCase):
    def tearDown(self) -> None:
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        for f in os.listdir(temp_dir):
            if f != ".gitignore":
                os.remove(os.path.join(temp_dir, f))

        temp_dir = os.path.join(settings.MEDIA_ROOT, "networks")
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

    def test_delete_scan_instances_with_missing_file(self):
        # Given
        file1 = mock.MagicMock(spec=File)
        file1.name = "scan_results.json"
        ScanInstance.objects.create(
            user="Pepito",
            file=file1,
        )
        file2 = mock.MagicMock(spec=File)
        file2.name = "other_results.json"
        ScanInstance.objects.create(
            user="Jorgito",
            file=file2
        )
        Path(settings.MEDIA_ROOT).joinpath("networks").joinpath(file2.name).unlink()
        # When
        call_command("delete_scan_instances_with_missing_file")
        # Then
        self.assertEqual(1, len(ScanInstance.objects.all()))
        instance = ScanInstance.objects.all()[0]
        self.assertEqual("Pepito", instance.user)
