from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager, db

class User(UserMixin):
    def __init__(self, user_id, email, username, is_admin=False):
        self.id = user_id
        self.email = email
        self.username = username
        self.is_admin = is_admin

    @staticmethod
    def get_by_id(user_id):
        user_ref = db.collection('users').document(user_id).get()
        if user_ref.exists:
            data = user_ref.to_dict()
            return User(user_id, data['email'], data['username'], data.get('is_admin', False))
        return None

    @staticmethod
    def get_by_email(email):
        users = db.collection('users').where('email', '==', email).limit(1).get()
        for u in users:
            data = u.to_dict()
            return User(u.id, data['email'], data['username'], data.get('is_admin', False))
        return None

    def verify_password(self, password):
        user_ref = db.collection('users').document(self.id).get()
        if user_ref.exists:
            return check_password_hash(user_ref.to_dict()['password_hash'], password)
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
