from db import db
from werkzeug.security import generate_password_hash

class UserModel(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self,first_name, last_name, username, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
    
    @classmethod
    def find_by_username(cls,username):
        return cls.query.filter_by(username=username).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()