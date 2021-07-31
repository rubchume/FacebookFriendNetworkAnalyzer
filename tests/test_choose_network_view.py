from datetime import datetime
from http import HTTPStatus
import os
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.test import Client, override_settings, TestCase

from core.models import ScanInstance


@override_settings(
    MEDIA_ROOT=os.path.join("tests", "helpers", "media")
)
class ChooseNetworkViewTests(TestCase):
    def tearDown(self) -> None:
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        for f in os.listdir(temp_dir):
            if f != ".gitignore":
                os.remove(os.path.join(temp_dir, f))

        temp_dir = os.path.join(settings.MEDIA_ROOT, "networks")
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

    def test_choose_network_view_is_up_and_running(self):
        # When
        response = Client().get("/choose_network")
        # Then
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertContains(response, "<title>Choose Network</title>")

    def test_shows_one_scan_instance(self):
        # Given
        file = mock.MagicMock(spec=File)
        file.name = "scan_results.json"
        ScanInstance.objects.create(
            user="Pepito",
            file=file
        )
        # When
        response = Client().get("/choose_network")
        # Then
        self.assertContains(response, "Pepito")

    def test_shows_multiple_scan_instances(self):
        # Given
        file1 = mock.MagicMock(spec=File)
        file1.name = "scan_results.json"
        ScanInstance.objects.create(
            user="Pepito",
            file=file1
        )
        file2 = mock.MagicMock(spec=File)
        file2.name = "other_scan_results.json"
        ScanInstance.objects.create(
            user="Jorgito",
            file=file2
        )
        # When
        response = Client().get("/choose_network")
        # Then
        self.assertContains(response, "Pepito")
        self.assertContains(response, "Jorgito")

    def test_only_show_last_instance_for_each_user(self):
        # Given
        file1 = mock.MagicMock(spec=File)
        file1.name = "scan_results.json"
        scan_instance1 = ScanInstance.objects.create(
            user="Pepito",
            file=file1
        )
        scan_instance1.datetime = datetime.strptime('2015-10-31', '%Y-%m-%d')
        scan_instance1.save()
        file2 = mock.MagicMock(spec=File)
        file2.name = "other_scan_results.json"
        scan_instance2 = ScanInstance.objects.create(
            user="Pepito",
            file=file2
        )
        scan_instance2.datetime = datetime.strptime('2015-10-30', '%Y-%m-%d')
        scan_instance2.save()
        # When
        response = Client().get("/choose_network")
        # Then
        self.assertContains(response, "Pepito (Oct. 31, 2015, midnight)")
        self.assertNotContains(response, "Pepito (Oct. 30, 2015, midnight)")
