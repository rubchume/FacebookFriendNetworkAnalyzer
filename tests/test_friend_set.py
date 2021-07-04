from unittest import TestCase

from src.friend import Friend
from src.friend_set import FriendSet


class FriendSetTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.friends_set = FriendSet([
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ])

    def test_friend_set_filters_friends_by_user_id(self):
        # When
        self.assertEqual(
            self.friends_set.filter(user_id="333"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE")
        )

    def test_friend_set_filters_by_name(self):
        # When
        self.assertEqual(
            self.friends_set.filter(name="AleyDani"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com")
        )

    def test_friend_set_raises_error_if_the_requested_friend_does_not_exist(self):
        # When
        self.assertRaises(
            ValueError,
            self.friends_set.filter,
            name="Jorge",
        )

    def test_iterate_through_friend_set_just_iterates_trough_friends(self):
        self.assertEqual(
            list(self.friends_set),
            self.friends_set.friends
        )

    def test_get_list_of_friends_attributes(self):
        # When
        links = self.friends_set.link
        # Then
        self.assertEqual(
            ["pedro.com", "rufusbajista.com", "juni.com", "dosecuatorianosymedio.com"],
            links
        )

    def test_get_list_of_non_existent_attribute_raises_attribute_error(self):
        self.assertRaises(
            AttributeError,
            getattr,
            self.friends_set,
            "non_existent_attribute"
        )

    def test_get_friend_by_index(self):
        self.assertEqual(
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            self.friends_set[1]
        )

    def test_representation(self):
        self.assertEqual(
            "FriendSet:\n"
            "Friend(Pedro)\n"
            "Friend(Rufus)\n"
            "Friend(Juni)\n"
            "Friend(AleyDani)",
            repr(self.friends_set)
        )

    def test_equality(self):
        # Given
        friend_set_equal = FriendSet([
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ])
        friend_set_different = FriendSet([
            Friend(user_id="1000", name="Juni", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ])
        friend_set_different_length = FriendSet([
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
        ])
        # Then
        self.assertEqual(friend_set_equal, self.friends_set)
        self.assertNotEqual(friend_set_different, self.friends_set)
        self.assertNotEqual(friend_set_different_length, self.friends_set)
