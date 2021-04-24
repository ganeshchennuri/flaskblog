import os
from flask import Flask, render_template, redirect, request, flash, session
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import check_password_hash
import random
import string
from models.user import UserModel
from models.blogs import BlogModel

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

#Loading db config from db.yaml file
# db = yaml.safe_load(open('db.yaml','r'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///flaskblog.db').replace('postgres://', 'postgresql://')  # trying to fetch environment varibale "DATABASE_URL", set to sqlite if not found
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False    #SQLAlchemy already have modification tracker,turning off FlaskSQLAlchemy event tracker to save resources

random_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(25))
app.secret_key = random_string

'''
@app.before_first_request
def create_tables():
    db.create_all()
'''

@app.route('/', methods = ['GET'])
def index():
    blogs = BlogModel.get_all_blogs()
    if blogs != None:
        return render_template('index.html',blogs=blogs)
    return render_template('index.html',blogs=None)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        #saving from details into variable (type <class 'werkzeug.datastructures.ImmutableMultiDict'>)
        user_details = request.form

        #password and confirm password not match return register page
        if user_details['password'] != user_details['confirm_password']:
            #flash message on top
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
        user = UserModel(user_details['first_name'], user_details['last_name'], user_details['username'], user_details['email'], user_details['password'])
        # try:
        user.save_to_db()
        #Flash message for successful registration
        flash('!Registration Successful Please login', 'success')
        # except:
        #     flash("Something happened from server side.", "danger")
        #redirecting to login Page
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        #saving form deatils into variable
        login_creds = request.form
        if login_creds['username']!='' and login_creds['password']!='':
            user = UserModel.find_by_username(login_creds['username'])
            if user and check_password_hash(user.password,login_creds['password']):
                #Creating session Variables
                session['login'] = True
                session['first_name'] = user.first_name
                session['last_name'] = user.last_name
                flash('Welcome '+str(session['first_name'])+', Login Successful','success')
                return redirect('/')
            else:
                flash("Enter correct Login Credentials. Try Again.", "danger")
                return render_template('login.html')
        flash("Username/Password cannot be empty","danger")
    return render_template('login.html')

@app.route('/write-blog',methods=['GET','POST'])
def writeblog():
    if request.method == 'POST':
        #saving form details into variables and Inserting into DB
        title = request.form['title']
        body = request.form['body']
        author = session['first_name']+" "+session['last_name']

        blog = BlogModel(title, author, body)
        blog.save_to_db()

        flash("Blog Posted Successfully","success")
        return redirect("/")
    return render_template('write-blog.html')

@app.route('/blogs/<int:id>')
def blogs(id):
    blog = BlogModel.get_blog_by_id(id)
    if blog:
        return render_template('blogs.html',blog=blog)
    return "<h1>Blog Not Found</h1>"

@app.route('/myblogs')
def my_blogs():
    author = session['first_name']+" "+session['last_name']
    my_blogs = BlogModel.get_blog_by_author(author)
    if blogs:
        return render_template('my-blogs.html',my_blogs=my_blogs)
    return render_template('my-blogs.html',blogs=None)

@app.route('/edit-blog/<int:id>', methods = ['GET', 'POST'])
def edit_blog(id):
    blog = BlogModel.get_blog_by_id(id)
    if blog:
        if request.method=='POST':
            title = request.form['title']
            body = request.form['body']

            blog.title = title
            blog.body = body
            blog.save_to_db()
            flash("Blog Post Updated Successfully","success")
            return redirect('/myblogs')
        return render_template('edit-blog.html',blog=blog)
    return render_template("/myblogs")
    
@app.route('/delete-blog/<int:id>')
def delete_blog(id):
    blog = BlogModel.get_blog_by_id(id)
    if blog:
        blog.delete_from_db()
        flash("Blog Post has been successfully Deleted","success")
    else:
        flash("Blog not found","danger")
    return redirect('/myblogs')

@app.route('/logout')
def logout():
    #Destroying session Variables
    session.clear()
    flash("You have Been Successfully logged out","success")
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(debug=False)