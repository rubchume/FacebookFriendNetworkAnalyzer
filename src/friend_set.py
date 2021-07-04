from typing import List

from src.friend import Friend


class FriendSet(object):
    def __init__(self, friends: List[Friend]):
        self.friends = friends

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.friends):
            friend = self.friends[self.i]
            self.i += 1
            return friend

        raise StopIteration

    def __getitem__(self, item):
        return self.friends[item]

    def __getattr__(self, attr):
        try:
            return [getattr(friend, attr) for friend in self.friends]
        except AttributeError:
            raise AttributeError(f"'FriendSet' object has no attribute '{attr}'")

    def __repr__(self):
        return "FriendSet:\n" + "\n".join(
            [repr(friend) for friend in self.friends]
        )

    def __eq__(self, other):
        if len(self.friends) != len(other.friends):
            return False

        for friend, friend_other in zip(self.friends, other.friends):
            if friend != friend_other:
                return False

        return True

    def filter(self, **filter_attributes):
        for friend in self.friends:
            friend_attributes = vars(friend)
            friend_relevant_attributes = {
                key: value
                for key, value in friend_attributes.items()
                if key in filter_attributes
            }
            if friend_relevant_attributes == filter_attributes:
                return friend

        raise ValueError("There is no friend with those attributes")
