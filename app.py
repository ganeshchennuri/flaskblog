from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
Bootstrap(app)

db = yaml.safe_load(open('db.yaml','r'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user'] 
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = 'noneedtodisclosekey'
mysql = MySQL(app)


@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_creds = request.form
        if login_creds['username']!='' and login_creds['password']!='':
            cur = mysql.connection.cursor()
            result_value = cur.execute("SELECT password FROM users WHERE username=%s",{login_creds['username']})
            if result_value>0:
                password = cur.fetchall()
                if check_password_hash(password[0][0],login_creds['password']) == True:
                    flash('Login Successful','success')
                    return redirect('/')
                    cur.close()
                else:
                    flash("Enter correct Password","danger")
                    return render_template('login.html')
            else:
                flash("Username not found. Try Again.", "danger")
                return render_template('login.html')
        else:
            flash("Enter Login credentials","danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_details = request.form
        if user_details['password'] != user_details['confirm_password']:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
        cur = mysql.connection.cursor()
        print(user_details['first_name'],user_details['last_name'], user_details['username'], user_details['email'], generate_password_hash(user_details['password']))
        cur.execute(f"INSERT INTO users(first_name,last_name,username,email,password) VALUES \
            ({user_details['first_name']},{user_details['last_name']},{user_details['username']},{user_details['email']},\
                {generate_password_hash(user_details['password'])})")
        mysql.connection.commit()
        cur.close()
        flash('!Registration Successful Please login', 'success')
        return redirect('/login')

    return render_template('register.html')

@app.route('/write-blog',methods=['GET','POST'])
def writeblog():
    return render_template('write-blog.html')

@app.route('/blog/<int:id>')
def blog():
    return render_template('blog.html',blog_id = id)

@app.route('/myblogs')
def my_blogs():
    return render_template('my-blogs.html')

@app.route('/edit-blog/<int:id>', methods = ['GET', 'POST'])
def edit_blog():
    return render_template('edit-blog.html',blog_id = id)

@app.route('/delete-blog/<int:id>')
def delete_blog():
    return render_template('delete-blog.html', blog_id = id)

@app.route('/logout')
def logout():
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)