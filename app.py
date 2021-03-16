from flask import Flask, render_template, redirect, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml
from flask_ckeditor import CKEditor
import random
import string

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

#Loading db config from db.yaml file
db = yaml.safe_load(open('db.yaml','r'))
random_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(25))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user'] 
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = random_string
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/', methods = ['GET'])
def index():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog")
    if result_value>0:
        blogs = cur.fetchall()
        return render_template('index.html',blogs=blogs)
    cur.close()
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

        #curson for mysql databse
        cur = mysql.connection.cursor()
        password = generate_password_hash(user_details['password'])
        sql = "INSERT INTO users(first_name, last_name, username, email, password) VALUES (%s,%s,%s,%s,%s)"
        values = (user_details['first_name'], user_details['last_name'], user_details['username'], user_details['email'], password)
        # Inserting the details into database
        cur.execute(sql,values)
        mysql.connection.commit() #commiting changes to database
        cur.close()
        #Flash message for successful registration
        flash('!Registration Successful Please login', 'success')
        #redirecting to login Page
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        #saving form deatils into variable
        login_creds = request.form
        if login_creds['username']!='' and login_creds['password']!='':
            cur = mysql.connection.cursor()
            # Quering DB for username if exists then check password else return incorrect username
            result_value = cur.execute("SELECT * FROM users WHERE username=%s",{login_creds['username']})
            if result_value>0:
                user = cur.fetchone()
                if check_password_hash(user['password'],login_creds['password']):
                    #Creating session Variables
                    session['login'] = True
                    session['first_name'] = user['first_name']
                    session['last_name'] = user['last_name']
                    flash('Welcome '+str(session['first_name'])+', Login Successful','success')
                    cur.close()
                    return redirect('/')
                else:
                    flash("Enter correct Password","danger")
                    cur.close()
                    return render_template('login.html')
            else:
                flash("Enter correct Username. Try Again.", "danger")
                cur.close()
                return render_template('login.html')
        flash("Enter Correct Login credentials","danger")
    return render_template('login.html')

@app.route('/write-blog',methods=['GET','POST'])
def writeblog():
    if request.method == 'POST':
        #saving form details into variables and Inserting into DB
        title = request.form['title']
        body = request.form['body']
        author = session['first_name']+" "+session['last_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blog(title, author, body) VALUES (%s,%s,%s)",(title,author,body))
        mysql.connection.commit()
        cur.close()
        flash("Blog Posted Successfully","success")
        return redirect("/")
    return render_template('write-blog.html')

@app.route('/blogs/<int:id>')
def blogs(id):
    cur = mysql.connection.cursor()
    #Quering blog details with id and passing to html template
    result_value = cur.execute(f"SELECT * FROM blog WHERE blogid={id}")
    if result_value>0:
        blog = cur.fetchone()
        return render_template('blogs.html',blog=blog)
    cur.close()
    return "<h1>Blog Not Found</h1>"

@app.route('/myblogs')
def my_blogs():
    cur = mysql.connection.cursor()
    author = session['first_name']+" "+session['last_name']
    result_value = cur.execute(f"SELECT * FROM blog WHERE author='{author}'")
    if result_value>0:
        my_blogs = cur.fetchall()
        return render_template('my-blogs.html',my_blogs=my_blogs)
    cur.close()
    return render_template('my-blogs.html',blogs=None)

@app.route('/edit-blog/<int:id>', methods = ['GET', 'POST'])
def edit_blog(id):
    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        cur = mysql.connection.cursor()
        result_value = cur.execute(f"UPDATE blog SET title='{title}', body='{body}' WHERE blogid={id}")
        mysql.connection.commit()
        cur.close()
        flash("Blog Post Updated Successfully","success")
        return redirect('/myblogs')
    cur = mysql.connection.cursor()
    result_value = cur.execute(f"SELECT * FROM blog WHERE blogid={id}")
    blog = cur.fetchone()
    cur.close()
    return render_template('edit-blog.html',blog=blog)
    
@app.route('/delete-blog/<int:id>')
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM blog WHERE blogid={id}")
    mysql.connection.commit()
    flash("Blog Post has been successfully Deleted","success")
    cur.close()
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
    app.run(debug=False,host="localhost")