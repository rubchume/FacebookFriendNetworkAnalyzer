import json
import urllib

from src.facebook_friend_network_scanner import FacebookFriendNetworkScanner
from src.friend import Friend


class FacebookFriendNetworkGraphQLScanner(FacebookFriendNetworkScanner):
    def __init__(self, user, password):
        super().__init__(user, password)

    def scan_network(self):
        self.read_all_friends_from_graphql_api()

        for i, friend in enumerate(self.friends, start=1):
            print(f"Reading mutual friends with {friend.name}. ({i} of {len(self.friends)})")
            self.read_mutual_friends_from_graphql_api(friend.user_id)
            print(f"  Number of mutual friends: {len(self.mutual_friends[friend.user_id])}")

    def read_mutual_friends_from_graphql_api(self, friend_id):
        self.mutual_friends[friend_id] = []
        self._mutual_friends_list_page_info[friend_id] = dict(has_next_page=True, end_cursor=None)

        while self._mutual_friends_list_page_info[friend_id]["has_next_page"]:
            self._read_next_batch_of_mutual_friends(friend_id)

    def _read_next_batch_of_mutual_friends(self, friend_id):
        api_info = self._get_next_batch_of_mutual_friends_api_info(friend_id)
        api_info_dict = json.loads(api_info)

        self.mutual_friends[friend_id] += self._mutual_friends_api_info_to_friend_list(api_info_dict)
        self._mutual_friends_list_page_info[friend_id] = (
            api_info_dict["data"]["profile_list"]["list_items"]["page_info"]
        )

    def _get_next_batch_of_mutual_friends_api_info(self, friend_id):
        url = 'https://www.facebook.com/api/graphql/'
        headers = {
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-fb-friendly-name": "CometProfileListDialogQuery",
            "referrer": "https://www.facebook.com/friends/list",
            "referrerPolicy": "strict-origin-when-cross-origin",
        }

        cursor = self._mutual_friends_list_page_info[friend_id]["end_cursor"]
        is_first_request = cursor is None

        response = self.session.post(
            url,
            headers=headers,
            data=urllib.parse.urlencode(
                {
                    "fb_dtsg": self._fb_dtsg_token,
                    "fb_api_req_friendly_name": (
                        "CometProfileListDialogQuery" if is_first_request
                        else "CometProfileListDialogListRefetchQuery"
                    ),
                    "variables": json.dumps(
                        {key: value for key, value in {
                            "listType": "MUTUAL_FRIENDS",
                            "sourceID": friend_id,
                            "scale": 1 if is_first_request else 1.5,
                            "cursor": cursor,
                            "count": None if is_first_request else 10,
                        }.items() if value}
                    ).replace(" ", ""),
                    "doc_id": (
                        self.DOC_IDS["mutual_friends_page_1"] if is_first_request
                        else self.DOC_IDS["mutual_friends_next_pages"]
                    )
                }
            )
        )

        return response.content

    @staticmethod
    def _mutual_friends_api_info_to_friend_list(api_info: dict):
        friend_objects = api_info["data"]["profile_list"]["list_items"]["edges"]
        return [
            Friend(
                user_id=str(friend["node"]["id"]),
                name=friend['node']['name'],
                link=friend['node']['url'],
            )
            for friend in friend_objects
            if friend["node"]["__typename"] == "User"
        ]
