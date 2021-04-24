from app import app
from db import db

db.init_app(app)

@app.before_first_request   #This method will run before the first request is sent 
def create_tables():
    db.create_all() 
