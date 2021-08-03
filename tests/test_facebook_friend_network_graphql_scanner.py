import json
from unittest import mock, TestCase
import urllib

import requests_mock

from src.facebook_friend_network_graphql_scanner import FacebookFriendNetworkGraphQLScanner
from src.friend import Friend


@mock.patch.object(FacebookFriendNetworkGraphQLScanner, "_log_into_facebook", return_value=None)
class FacebookFriendNetworkGraphQLScannerTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("tests/helpers/facebook_friend_list_page.html", "r") as friend_list_page:
            cls.html = friend_list_page.read()

        FacebookFriendNetworkGraphQLScanner.TIME_TO_LOGIN = 0

    def setUp(self):
        self.driver_creation_patcher = mock.patch('src.facebook_friend_network_scanner.webdriver')
        self.driver_creation_mock = self.driver_creation_patcher.start()
        driver_mock = mock.MagicMock()
        self.driver_creation_mock.Chrome.return_value = driver_mock
        driver_mock.get.return_value = self.html
        driver_mock.page_source = self.html
        self.driver_mock = driver_mock

        mock.patch("src.facebook_friend_network_scanner.ChromeDriverManager").start()

    @requests_mock.Mocker()
    def test_get_one_page_of_common_friends(self, _, req_mock):
        # Given
        expected_friends = [
            Friend(
                user_id="111",
                name="Pedro",
                link="pedro.com",
            ),
            Friend(
                user_id="222",
                name="Rufus",
                link="rufusbajista.com",
            ),
        ]

        req_mock.post(
            "https://www.facebook.com/api/graphql/",
            json=dict(
                data=dict(
                    profile_list=dict(
                        list_items=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        id="111",
                                        name="Pedro",
                                        url="pedro.com",
                                        __typename="User",
                                    ),
                                ),
                                dict(
                                    node=dict(
                                        id="222",
                                        name="Rufus",
                                        url="rufusbajista.com",
                                        __typename="User",
                                    ),
                                ),
                            ],
                            page_info=dict(has_next_page=False, end_cursor=None),
                        )
                    )
                )
            )
        )

        ffn = FacebookFriendNetworkGraphQLScanner("username", "password")
        # When
        ffn.read_mutual_friends_from_graphql_api("12345")
        # Then
        self.assertEqual(
            expected_friends,
            ffn.mutual_friends["12345"]
        )

    @requests_mock.Mocker()
    def test_get_many_pages_of_common_friends(self, _, req_mock):
        # Given
        expected_friends = [
            Friend(
                user_id="111",
                name="Pedro",
                link="pedro.com",
            ),
            Friend(
                user_id="222",
                name="Rufus",
                link="rufusbajista.com",
            ),
            Friend(
                user_id="333",
                name="Juni",
                link="juni.com",
            ),
            Friend(
                user_id="444",
                name="AleyDani",
                link="dosecuatorianosymedio.com",
            ),
        ]

        def is_first_call(request):
            return req_mock.call_count == 1

        req_mock.post(
            "https://www.facebook.com/api/graphql/",
            json=dict(
                data=dict(
                    profile_list=dict(
                        list_items=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        id="111",
                                        name="Pedro",
                                        url="pedro.com",
                                        __typename="User",
                                    ),
                                ),
                                dict(
                                    node=dict(
                                        id="222",
                                        name="Rufus",
                                        url="rufusbajista.com",
                                        __typename="User",
                                    ),
                                ),
                            ],
                            page_info=dict(has_next_page=True, end_cursor="asdf"),
                        )
                    )
                )
            ),
            additional_matcher=is_first_call
        )

        def is_second_call(request):
            return req_mock.call_count > 1

        req_mock.post(
            "https://www.facebook.com/api/graphql/",
            json=dict(
                data=dict(
                    profile_list=dict(
                        list_items=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        id="333",
                                        name="Juni",
                                        url="juni.com",
                                        __typename="User",
                                    ),
                                ),
                                dict(
                                    node=dict(
                                        id="444",
                                        name="AleyDani",
                                        url="dosecuatorianosymedio.com",
                                        __typename="User",
                                    ),
                                ),
                            ],
                            page_info=dict(has_next_page=False, end_cursor=None),
                        )
                    )
                )
            ),
            additional_matcher=is_second_call
        )

        ffn = FacebookFriendNetworkGraphQLScanner("username", "password")
        # When
        ffn.read_mutual_friends_from_graphql_api("12345")
        # Then
        self.assertEqual(
            expected_friends,
            ffn.mutual_friends["12345"]
        )
        post_data_first_page = urllib.parse.parse_qs(req_mock.request_history[0].text)
        self.assertEqual(
            "CometProfileListDialogQuery",
            post_data_first_page["fb_api_req_friendly_name"][0]
        )
        variables = json.loads(post_data_first_page["variables"][0])
        self.assertEqual(
            {'listType': 'MUTUAL_FRIENDS', 'sourceID': '12345', 'scale': 1},
            variables
        )
        post_data_second_page = urllib.parse.parse_qs(req_mock.request_history[1].text)
        self.assertEqual(
            "CometProfileListDialogListRefetchQuery",
            post_data_second_page["fb_api_req_friendly_name"][0]
        )
        variables = json.loads(post_data_second_page["variables"][0])
        self.assertEqual(
            {
                "count": 10,
                "cursor": "asdf",
                "listType": "MUTUAL_FRIENDS",
                "scale": 1.5,
                "sourceID": "12345"
            },
            variables
        )

    @mock.patch(
        "src.facebook_friend_network_graphql_scanner"
        ".FacebookFriendNetworkGraphQLScanner.read_mutual_friends_from_graphql_api",
        autospec=True
    )
    @mock.patch.object(FacebookFriendNetworkGraphQLScanner, "read_all_friends_from_graphql_api")
    def test_scan_network(self, read_all_friends, read_mutual_friends, _):
        # Given
        ffn = FacebookFriendNetworkGraphQLScanner("username", "password")
        ffn.friends = [
            Friend(user_id="222", name="Andrew", link="http://www.facebook.com/andrew"),
            Friend(user_id="12345", name="Elena", link="https://www.facebook.com/profile.php?id=12342346"),
        ]

        def read_mutual_friends_function(obj, user_id):
            obj.mutual_friends[user_id] = [Friend(user_id="111", name="Pedro", link="iampedro.com")]

        read_mutual_friends.side_effect = read_mutual_friends_function

        # When
        ffn.scan_network()
        # Then
        read_all_friends.assert_called_once()
        self.assertEqual(2, read_mutual_friends.call_count)
        self.assertEqual(
            [
                mock.call(ffn, "222"), mock.call(ffn, "12345")
            ],
            read_mutual_friends.call_args_list
        )
