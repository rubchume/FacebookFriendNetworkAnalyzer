import os
from unittest import mock

from django.conf import settings
from django.test import override_settings, TestCase

from core.models import ScanInstance
from core.views import scan_facebook_friend_network


@override_settings(
    MEDIA_ROOT=os.path.join("tests", "helpers", "media")
)
class ScanViewTests(TestCase):
    def tearDown(self) -> None:
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        for f in os.listdir(temp_dir):
            if f != ".gitignore":
                os.remove(os.path.join(temp_dir, f))

        temp_dir = os.path.join(settings.MEDIA_ROOT, "networks")
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

    @mock.patch("os.remove")
    @mock.patch("core.views.FacebookFriendNetworkScanner")
    def test_scan_network_saves_file_to_model(self, _, __):
        # Given
        with open(os.path.join(settings.MEDIA_ROOT, "temp", "network_pedro.json"), "w") as file:
            file.write("nothing")
        # When
        scan_facebook_friend_network.now("pedro", "password")
        # Then
        self.assertEqual(1, len(ScanInstance.objects.all()))
        scan_instance = ScanInstance.objects.get(user="pedro")
        self.assertEqual(
            os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, "networks", "pedro.json"),
            scan_instance.file.path
        )
