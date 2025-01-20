from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, String, Integer
from flask_login import UserMixin
from flask_login import LoginManager


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def get_default_datetime():
    return datetime.utcnow() + timedelta(hours=8)

def datetime_to_str(dt, format='%Y-%m-%d %H:%M:%S'):
    """Convert a datetime object to a string."""
    return dt.strftime(format)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)

    def get_id(self):
        """返回用户ID的字符串表示，满足Flask-Login的要求。"""
        return str(self.id)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
