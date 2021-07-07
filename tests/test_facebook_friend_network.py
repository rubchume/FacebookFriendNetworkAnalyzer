from unittest import TestCase

from src.friend import Friend
from src.friend_network import FriendNetwork
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
            ffn.mutual_friends
        )
