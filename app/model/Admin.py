from flask_login import UserMixin


class Admin(UserMixin):
    def get_id(self):
        return "admin"
