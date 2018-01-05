import firebase_admin
from firebase_admin import auth, credentials
from employee_management.settings import FIREBASE_CREDENTIAL_JSON

DEFAULT_APP = firebase_admin.initialize_app(credentials.Certificate(FIREBASE_CREDENTIAL_JSON))


class FirebaseField(object):
    def __init__(self, *args, **kwargs):
        self.firebase_app = kwargs['app'] if 'app' in kwargs else DEFAULT_APP

    def create_firebase_user(self, *args, **kwargs):
        uid = kwargs['uid'] if 'uid' in kwargs else 'mk1'

        try:
            new_user = auth.get_user(uid)
        except auth.AuthError:
            # auth.create_user(uid='root', display_name='RoOt', password='r@123456', phone_number='+910000000000', email='root@quixom.com', disabled=False)
            new_user = auth.create_user(uid='mk3', display_name='Mark II', password='r@123456', phone_number=1111222333)
        access_token = auth.create_custom_token(new_user.uid, developer_claims=None, app=None)
        return new_user, access_token
