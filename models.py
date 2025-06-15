from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.email = user_data['email']
        self.phone = user_data.get('phone', '')
        self.role = user_data.get('role', 'user')
        self.created_at = user_data.get('created_at', '') 