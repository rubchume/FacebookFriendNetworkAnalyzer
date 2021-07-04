from unittest import TestCase

from src.friend import Friend


class FriendTests(TestCase):
    def test_transform_friend_info_to_json(self):
        # Given
        friend = Friend(
            user_id="123",
            name="Andrés",
            link="andrew.com",
            gender="MALE",
        )
        # When
        self.assertEqual(
            {'user_id': '123', 'name': 'Andrés', 'link': 'andrew.com', 'gender': 'MALE'},
            vars(friend)
        )

    def test_string_representation(self):

        self.assertEqual(
            repr(
                Friend(
                    user_id="123",
                    name="Andrés",
                    link="andrew.com",
                    gender="MALE",
                )
            ),
            "Friend(Andrés)"
        )

    def test_equality_of_friend_instances(self):
        self.assertEqual(
            Friend(user_id="123", name="Andrés", link="andrew.com", gender="MALE"),
            Friend(user_id="123", name="Andrés", link="andrew.com", gender="MALE")
        )
        self.assertNotEqual(
            Friend(user_id="123", name="Andrés", link="andrew.com", gender="MALE"),
            Friend(user_id="124", name="Jose", link="andrew.com", gender="MALE")
        )

    def test_raise_error_when_testing_equality_on_two_friends_with_same_id_but_different_other_fields(self):
        with self.assertRaises(RuntimeError):
            are_equal = Friend(
                user_id="123",
                name="Andrés",
                link="andrew.com",
                gender="MALE",
            ) == Friend(
                user_id="123",
                name="Jose",
                link="andrew.com",
                gender="MALE",
            )
            self.assertIsNone(are_equal)
