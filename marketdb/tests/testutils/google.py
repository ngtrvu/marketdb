import uuid

user_mock_json = {
    "gid": uuid.uuid4().hex,
    "display_name": "Developer Stag",
    "email": "dev@stag.dev",
    "email_verified": True,
}


class GGUser(object):
    uid = None

    def __init__(self, uid, user_data):
        self.uid = uid
        for k, v in user_data.items():
            setattr(self, k, v)

    def json(self):
        return self.__dict__


def mock_user():
    uid = uuid.uuid4()
    return GGUser(
        gid=uid,
        user_data={
            'gid': uid,
        }).json()
