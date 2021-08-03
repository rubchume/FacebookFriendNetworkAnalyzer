import os
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.test import Client, override_settings, TestCase

from core.models import ScanInstance
from src.friend_network import FriendNetwork


@override_settings(
    MEDIA_ROOT=os.path.join("tests", "helpers", "media")
)
class AnalysisViewTests(TestCase):
    def tearDown(self) -> None:
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        for f in os.listdir(temp_dir):
            if f != ".gitignore":
                os.remove(os.path.join(temp_dir, f))

        temp_dir = os.path.join(settings.MEDIA_ROOT, "networks")
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

    @mock.patch("plotly.offline.plot")
    @mock.patch.object(FriendNetwork, "draw_graph_plotly")
    @mock.patch.object(FriendNetwork, "filter_biggest_component")
    @mock.patch.object(FriendNetwork, "load_network")
    def test_load_network_for_user(
            self, load_network, filter_biggest_component, draw_graph_plotly, plot
    ):
        # Given
        file = mock.MagicMock(spec=File)
        file.name = "pepito_network.json"
        instance = ScanInstance.objects.create(
            user="pepito",
            file=file
        )
        # When
        Client().get(f"/analysis/{instance.pk}")
        # Then
        load_network.assert_called_once_with(
            str(Path("tests/helpers/media/networks/pepito_network.json"))
        )
        filter_biggest_component.assert_called_once()
        draw_graph_plotly.assert_called_once()
        plot.assert_called_once()
