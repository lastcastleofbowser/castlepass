import sqlite3, os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from contextlib import closing
from flask_login import LoginManager, logout_user, login_required, login_user, UserMixin, current_user 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import DataRequired, Email


# from flask_session import Session

app = Flask(__name__)

# Open & configure the database
connection = sqlite3.connect("castlepass.db")
cursor = connection.cursor()
print("Opened database successfully", connection.total_changes)

# Close the database connection
with closing(sqlite3.connect("castlepass.db")) as connection:
    with closing(connection.cursor()) as cursor:
        rows = cursor.execute("SELECT 1").fetchall()
        print(rows)


# Get the secret key from the environment variable
secret_key = os.environ.get("SECRET_KEY")

if secret_key is None:
    # Secret key is not set
    raise ValueError("Secret key is not configured.")

# Assign the secret key to the app configuration
app.config["SECRET_KEY"] = secret_key

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(person_id):
    return User.get(person_id)

# --- DEFINE USER CLASS ---
class User(UserMixin):
    def __init__(self, password, email, first_name, last_name, person_id):
        self.id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = generate_password_hash(str(password))
        self.email = email

    def __str__(self):
        return f"User: {self.first_name} {self.last_name} (ID: {self.id}, Email: {self.email})"
    
    def save(self):
        cursor.execute(
            'INSERT INTO users (first_name, last_name, password, email) VALUES (?, ?, ?, ?, ?)',
            (self.first_name, self.last_name, self.password_hash, self.email)
        )
        connection.commit()

    @staticmethod
    def get(email):
        connection = sqlite3.connect("castlepass.db")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            connection.close()
            return None
        user = User(row[0], row[1], row[2], row[3], row[4])
        cursor.close()
        connection.close()
        return user
    
    @staticmethod
    def get_id(email):
        connection = sqlite3.connect("castlepass.db")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            connection.close()
            return None
        user_id = User(row[0])
        cursor.close()
        connection.close()
        return user_id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- DEFINE LOGIN FORM ---
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()]) 
    submit = SubmitField('Login')

   
# --- ROUTES BELOW ---

@app.route("/")
# @login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    connection= None
    cursor = None

    if request.method == "POST":
        try:
            # Get the username and password from the form
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            password = str(request.form.get("password"))
            email = request.form.get("email")

            # Check all parameters are filled
            if not first_name or not last_name or not password or not email:
                return render_template("error.html", message="Please fill out all fields", code="400 Bad Request")

            # Check if the email already exists
            connection = sqlite3.connect('castlepass.db')  
            
            # Replace with your actual database name
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template("error.html", message="Email already exists", code="409 Conflict")

            # Check password is at least 6 characters long
            if len(password) < 6:
                return render_template("error.html", message="Password should be at least 6 characters long")
           
            # Check email is correct format 
            if email.find("@") == -1 or email.find(".") == -1:
                return render_template("error.html", message="Check your email is formatted correctly", code="400 Bad Request")

            # Create a new user
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (first_name, last_name, password_hash, email) VALUES (?, ?, ?, ?)",
                (first_name, last_name, hashed_password, email)
            )
            connection.commit()

            user = User.get(email)
            print(f"User details:", user.__str__())
            print(f"User details:", {user})

            return render_template("login.html", form=LoginForm())

        finally:    
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    else:
        return render_template("register.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == "POST":
        connection = sqlite3.connect("castlepass.db")
        cursor = connection.cursor()

        try:
            print('Inside POST method')
            if form.validate_on_submit():
                print(f"Form validated: {form.validate_on_submit()}")
                user = User.get(email=form.email.data)
                print(f"Form email: {form.email.data}")
                print(f"User details: {user}")
                if user:
                    if check_password_hash(user.password_hash, form.password.data):
                        flash('Password correct.')
                        login_user(user)
                        flash('Logged in as: ' + user.first_name + ' ' + user.last_name)
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid password.')
                else:
                    flash('Invalid email: {form.email.data}')
            else:
                print(form.errors)
        finally:
            cursor.close()
            connection.close()
    
    print('Outside POST method')

     # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')