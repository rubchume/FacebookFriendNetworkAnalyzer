import json
import os
from unittest import mock, TestCase

import requests_mock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from src.facebook_friend_network_scanner import FacebookFriendNetworkScanner
from src.friend import Friend


@mock.patch.object(FacebookFriendNetworkScanner, "_log_into_facebook", return_value=None)
class FacebookFriendNetworkScannerTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("tests/helpers/facebook_friend_list_page.html", "r") as friend_list_page:
            cls.html = friend_list_page.read()

        FacebookFriendNetworkScanner.TIME_TO_LOGIN = 0

    def setUp(self):
        self.driver_creation_patcher = mock.patch('src.facebook_friend_network_scanner.webdriver')
        self.driver_creation_mock = self.driver_creation_patcher.start()
        driver_mock = mock.MagicMock()
        self.driver_creation_mock.Chrome.return_value = driver_mock
        driver_mock.get.return_value = self.html
        driver_mock.page_source = self.html
        self.driver_mock = driver_mock

    def test_create_facebook_friend_network(self, _):
        # When
        FacebookFriendNetworkScanner("username", "password")
        # Then
        self.driver_mock.get.assert_called_once_with("https://www.facebook.com/friends/list")

    def test_save_network_to_files(self, _):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        ffn.friends = [
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ]
        ffn.mutual_friends["111"] = [
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
        ]
        ffn.mutual_friends["444"] = [
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com"),
        ]
        # When
        ffn.save_network("tests/helpers/output_file.json")
        # Then
        with open("tests/helpers/output_file.json", "r") as file:
            saved_data = json.load(file)

        self.assertEqual(
            dict(
                friend_list=[
                    dict(user_id="111", name="Pedro", link="pedro.com", gender=None),
                    dict(user_id="222", name="Rufus", link="rufusbajista.com", gender=None),
                    dict(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
                    dict(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com", gender=None),
                ],
                mutual_friends={
                    "111": [
                        dict(user_id="222", name="Rufus", link="rufusbajista.com", gender=None)
                    ],
                    "444": [
                        dict(user_id="222", name="Rufus", link="rufusbajista.com", gender=None),
                        dict(user_id="333", name="Juni", link="juni.com", gender=None),
                    ]
                }
            ),
            saved_data
        )
        # Finally
        os.remove("tests/helpers/output_file.json")

    def test_infer_user_id_from_profile_link_if_mutual_friend_user_id_is_missing(self, _):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        ffn.friends = [
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ]
        ffn.mutual_friends["111"] = [
            Friend(name="Rufus", link="rufusbajista.com"),
        ]
        ffn.mutual_friends["444"] = [
            Friend(name="Rufus", link="rufusbajista.com"),
            Friend(name="Juni", link="juni.com"),
        ]
        # When
        ffn.infer_missing_user_ids_from_profile_link()
        ffn.save_network("tests/helpers/output_file.json")
        # Then
        self.assertEqual(
            [Friend(user_id="222", name="Rufus", link="rufusbajista.com")],
            ffn.mutual_friends["111"]
        )
        self.assertEqual(
            [
                Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
                Friend(user_id="333", name="Juni", link="juni.com"),
            ],
            ffn.mutual_friends["444"]
        )

    @mock.patch.object(FacebookFriendNetworkScanner, "_mutual_friends_page_is_loading", return_value=False)
    @mock.patch.object(
        FacebookFriendNetworkScanner,
        "_get_mutual_friends_from_mutual_friends_html",
        return_value=[Friend(user_id="111", name="Pedro", link="pedro.com")]
    )
    def test_read_mutual_friends_from_friend_profile(self, _, __, ___):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        ffn.friends = [
            Friend(user_id="111", name="Pedro", link="pedro.com"),
            Friend(user_id="222", name="Rufus", link="rufusbajista.com"),
            Friend(user_id="333", name="Juni", link="juni.com", gender="FEMALE"),
            Friend(user_id="444", name="AleyDani", link="dosecuatorianosymedio.com"),
        ]
        # When
        ffn.read_mutual_friends_from_friend_profile("333")
        # Then
        self.assertEqual(2, self.driver_mock.get.call_count)
        self.assertEqual(
            mock.call("juni.com/friends_mutual"),
            self.driver_mock.get.call_args
        )
        self.assertEqual(
            [Friend(user_id="111", name="Pedro", link="pedro.com")],
            ffn.mutual_friends["333"]
        )

    def test_get_common_friends_from_html_cards(self, _):
        # Given
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # if os.environ.get("GITLAB_CI", None) is not None:
        #     chrome_driver_path = os.path.join(os.getcwd(), "chromedriver_linux")
        # else:
        #     chrome_driver_path = "chromedriver"
        # driver = webdriver.Chrome(os.path.join(os.getcwd(), chrome_driver_path), options=chrome_options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get('file:///' + os.getcwd() + '/tests/helpers/common_friends_page.html')
        # When
        friends = FacebookFriendNetworkScanner._get_mutual_friends_from_mutual_friends_html(driver)
        # Then
        self.assertEqual(
            [
                Friend(name="Ana Giral", link="https://www.facebook.com/ana.girbesalborch"),
                Friend(name="Borja Canet Rodriguez", link="https://www.facebook.com/borja.tuby"),
                Friend(name="Damaris Pelaez", link="https://www.facebook.com/damaris.pelaez.75"),
                Friend(name="Dieguine Waisrub", link="https://www.facebook.com/Di3LuX11"),
            ],
            friends[:4]
        )

    def test_get_mutual_friends_link(self, _):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        ffn.friends = [
            Friend(user_id="222", name="Andrew", link="http://www.facebook.com/andrew"),
            Friend(user_id="12345", name="Elena", link="https://www.facebook.com/profile.php?id=12342346"),
        ]
        # Then
        self.assertEqual(
            "http://www.facebook.com/andrew/friends_mutual",
            ffn._get_mutual_friends_link("222")
        )
        self.assertEqual(
            "https://www.facebook.com/profile.php?id=12342346&sk=friends_mutual",
            ffn._get_mutual_friends_link("12345")
        )

    @mock.patch.object(FacebookFriendNetworkScanner, "_mutual_friends_page_is_loading", side_effect=[True, False])
    def test_wait_until_all_mutual_friends_are_loaded(self, _, __):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        # When
        ffn._wait_until_all_mutual_friends_are_loaded()
        # Then
        self.driver_mock.find_element_by_xpath.assert_called_once_with("//body")
        element = self.driver_mock.find_element_by_xpath("//body")
        element.send_keys.assert_called_once_with(Keys.END)

    def test_detect_loading_page(self, _):
        # Given
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # if os.environ.get("GITLAB_CI", None) is not None:
        #     chrome_driver_path = os.path.join(os.getcwd(), "chromedriver_linux")
        # else:
        #     chrome_driver_path = "chromedriver"
        # driver = webdriver.Chrome(chrome_driver_path, options=chrome_options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # When
        driver.get('file:///' + os.getcwd() + '/tests/helpers/common_friends_page.html')
        # Then
        self.assertFalse(
            FacebookFriendNetworkScanner._mutual_friends_page_is_loading_from_html(driver)
        )

        # When
        driver.get('file:///' + os.getcwd() + '/tests/helpers/mutual_friends_loading_page.html')
        # Then
        self.assertTrue(
            FacebookFriendNetworkScanner._mutual_friends_page_is_loading_from_html(driver)
        )

    @mock.patch.object(FacebookFriendNetworkScanner, "_mutual_friends_page_is_loading_from_html")
    def test_detect_loading_page_calls_static_method(self, m, _):
        # When
        FacebookFriendNetworkScanner("username", "password")._mutual_friends_page_is_loading()
        # Then
        m.assert_called_once_with(self.driver_mock)

    @requests_mock.Mocker()
    def test_get_one_page_of_common_friends(self, _, req_mock):
        # Given
        expected_friends = [
            Friend(
                user_id="111",
                name="Pedro",
                link="pedro.com",
                gender="MALE",
            ),
            Friend(
                user_id="222",
                name="Rufus",
                link="rufusbajista.com",
                gender="MALE"
            ),
        ]

        req_mock.post(
            "https://www.facebook.com/api/graphql/",
            json=dict(
                data=dict(
                    viewer=dict(
                        all_friends=dict(
                            edges=[
                                dict(
                                    node=dict(
                                        id="111",
                                        name="Pedro",
                                        url="pedro.com",
                                        gender="MALE",
                                        __typename="User",
                                    ),
                                ),
                                dict(
                                    node=dict(
                                        id="222",
                                        name="Rufus",
                                        url="rufusbajista.com",
                                        gender="MALE",
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

        ffn = FacebookFriendNetworkScanner("username", "password")
        # When
        ffn.read_all_friends_from_graphql_api()
        # Then
        self.assertEqual(
            expected_friends,
            ffn.friends
        )

    @mock.patch(
        "src.facebook_friend_network_scanner.FacebookFriendNetworkScanner.read_mutual_friends_from_friend_profile",
        autospec=True
    )
    @mock.patch.object(FacebookFriendNetworkScanner, "read_all_friends_from_graphql_api")
    def test_scan_network(self, read_all_friends, read_mutual_friends, _):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
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

    @mock.patch(
        "src.facebook_friend_network_scanner.FacebookFriendNetworkScanner.read_mutual_friends_from_friend_profile",
        autospec=True
    )
    @mock.patch.object(FacebookFriendNetworkScanner, "read_all_friends_from_graphql_api")
    def test_scan_network_notifies_log_messages_to_input_function(self, read_all_friends, read_mutual_friends, _):
        # Given
        ffn = FacebookFriendNetworkScanner("username", "password")
        notify = mock.MagicMock()
        # When
        ffn.scan_network(notify)
        # Then
        self.assertLess(0, notify.call_count)
