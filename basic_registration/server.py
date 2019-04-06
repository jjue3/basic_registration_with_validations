from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
app = Flask(__name__)
app.secret_key = 'secret_key'
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re 
email_rex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_rex = re.compile(r'^[a-zA-Z]+$')    
password_rex = re.compile(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$")

@app.route('/') 
def index():
    return render_template('index.html')    

@app.route('/', methods=['POST'])
def registration():
    is_valid = True
    mysql = connectToMySQL('reg')       
    query = 'SELECT * FROM users WHERE email=%(email)s;'
    data = {
        "email" : request.form['email']
    }
    existing_email = mysql.query_db(query, data)
    if len(request.form['first_name']) < 2 or not name_rex.match(request.form['first_name']):
        is_valid = False
        flash("Please enter your first name")
        print('false')
        return redirect('/')
    if len(request.form['last_name']) < 2 or not name_rex.match(request.form['last_name']):
        is_valid = False
        flash("Please enter your last name")
        print('false')
        return redirect('/')
    if not email_rex.match(request.form['email']):
        is_valid = False
        flash("Please enter an email")
        print('false')
        return redirect('/')        
    if existing_email:
        is_valid = False
        flash("Email already in use")
        print('false')
        return redirect('/')
    if not password_rex.match(request.form['password']):
        is_valid = False
        flash("Please enter a password")
        print('false')
        return redirect('/')
    if len(request.form['passwordc']) < 5:
        is_valid = False
        flash("Please comfirm password")
        print('false')
        return redirect('/')
    if request.form['password'] != request.form['passwordc']:
        is_valid = False
        flash("Password does not match")
        print('false')    
        return redirect('/')
    if is_valid:
        flash("Successfully added!")
        session['first_name'] = request.form['first_name']
        session['last_name'] = request.form['last_name']
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        password = bcrypt.generate_password_hash(request.form['password'])
        print(password)
        data = {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "email": request.form["email"],
                "password" : password
                }
        mysql = connectToMySQL('reg')         
        query = "INSERT INTO reg.users (first_name, last_name, email, password, created_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW());"
        userlog = mysql.query_db(query, data)
        return redirect('/success')

@app.route('/login', methods=['POST'])
def login():
    if len(request.form['password'])<1:
        flash("Please enter password")
        return redirect('/')
    if len(request.form['email'])<1:
        flash("Please enter email")
        return redirect('/')
    mysql = connectToMySQL('reg')       
    query = 'SELECT * FROM users WHERE email=%(email)s;'
    data = {
        "email" : request.form['email']
        }
    query_result = mysql.query_db(query, data)
    if not query_result:
        flash('Email/Password is incorrect')
        return redirect('/')
    pw_hash = query_result[0]["password"]
    password_check = bcrypt.check_password_hash(pw_hash,request.form['password'])
    if query_result:
        if password_check:
            flash('Success')
            return redirect('/success')
    else:
        flash("Email/Password is incorrect")
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect('/')         

@app.route('/success')
def successload():
    if session == "":
        return redirect('/')
    else:    
        return render_template('success.html')
    
if __name__ == "__main__":
    app.run(debug=True)
