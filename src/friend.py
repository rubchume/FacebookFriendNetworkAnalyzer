class Friend(object):
    def __init__(self, user_id=None, name=None, link=None, gender=None):
        self.user_id = user_id
        self.name = name
        self.link = link
        self.gender = gender

    def __repr__(self):
        return f"Friend({self.name})"

    def __eq__(self, other):
        if self.user_id == other.user_id:
            if self.name == other.name and self.link == other.link:
                return True
            raise RuntimeError("Incoherent data. Two friends with same Id cannot have different name or link")

        return False
