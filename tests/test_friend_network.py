from unittest import TestCase

import pandas as pd
from pandas._testing import assert_series_equal

from src.friend_network import FriendNetwork
from src.friend import Friend
from src.friend_set import FriendSet


class FacebookFriendNetworkTests(TestCase):
    def test_create_load_network_from_file(self):
        # Given
        ffn = FriendNetwork()
        # When
        ffn.load_network("tests/helpers/network_example.json")
        # Then
        self.assertEqual(
            FriendSet([
                Friend(user_id="123", name="Ruf", link="ruf.com", gender="MALE"),
                Friend(user_id="456", name="Pau", link="pau.com", gender="MALE"),
            ]),
            ffn.friends
        )
        self.assertEqual(
            {
                "123": FriendSet([Friend(user_id="456", name="Pau", link="pau.com", gender="MALE")]),
                "456": FriendSet([Friend(user_id="123", name="Ruf", link="ruf.com", gender="MALE")]),
            },
            ffn.common_friends
        )

    def test_get_node_to_community_mapping(self):
        # Given
        communities = [
            {"1", "3", "5", "7"},
            {"2", "4", "6", "9"},
        ]
        ffn = FriendNetwork(
            friends=FriendSet([
                Friend(user_id="1"),
                Friend(user_id="2"),
                Friend(user_id="3"),
                Friend(user_id="4"),
                Friend(user_id="5"),
                Friend(user_id="6"),
                Friend(user_id="7"),
                Friend(user_id="8"),
                Friend(user_id="9"),
            ]),
            common_friends={},
        )
        # When
        community_mapping = ffn.get_node_to_community_mapping(communities)
        # Then
        assert_series_equal(
            pd.Series([1, 2, 1, 2, 1, 2, 1, 0, 2], index=["1", "2", "3", "4", "5", "6", "7", "8", "9"]),
            community_mapping
        )
