from db import db

class BlogModel(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(40))
    body = db.Column(db.String(1000))

    def __init__(self, title, author, body):
        self.title = title
        self.author = author
        self.body = body
    
    @classmethod
    def get_all_blogs(cls):
        return cls.query.all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_blog_by_id(cls,id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_blog_by_author(cls,author):
        return cls.query.filter_by(author=author).all()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return {
            "title": self.title,
            "author": self.author,
            "body": self.body
        }