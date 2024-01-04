import sqlite3, os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for, flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from contextlib import closing
from flask_login import LoginManager, UserMixin, logout_user, login_required, login_user, current_user 
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import DataRequired, Email

from password_gen import password_generator

# Create the Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# CSRF protection
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config['WTF_CSRF_ENABLED'] = False

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
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(person_id):
    return User.get(int(person_id))

# --- DEFINE USER CLASS ---
class User(UserMixin):
    def __init__(self, person_id, first_name, last_name, email, password_hash):
        self.id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash

    def __str__(self):
        return f"User: {self.first_name} {self.last_name} (ID: {self.id}, Email: {self.email})"
    
    def save(self):
        connection = sqlite3.connect("castlepass.db")
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO users (first_name, last_name, password_hash, email) VALUES (?, ?, ?, ?)',
            (self.first_name, self.last_name, self.password_hash, self.email)
        )
        self.id = cursor.lastrowid
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
    
    def get_id(self):
        return str(self.id) if self.id is not None else None 

    @property
    def is_authenticated(self):
        return True if self.id is not None else False
    
    @property
    def is_active(self):
        return True if self.id is not None else False
    
    def is_anonymous(self):
        return False
    
    def check_password(self, entered_password):
        return check_password_hash(self.password_hash, entered_password)

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
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            # cursor.execute(
            #     "INSERT INTO users (first_name, last_name, password_hash, email) VALUES (?, ?, ?, ?)",
            #     (first_name, last_name, hashed_password, email)
            # )
            # connection.commit()
            user = User(None, first_name, last_name, email, hashed_password)
            user.save()

            # user = User.get(email)
            # print(f"User details:", user.__str__())
            # print(f"User details:", {user})

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
    email = request.form.get("email")
    password = request.form.get("password")

    if request.method == "POST" and form.validate_on_submit():
        print(f"Form data: {request.form}")
        
        user = User.get(email)

        if user and user.check_password(password):
            login_user(user)
            flash(f'Logged in as: {user.first_name} {user.last_name}')
            print(f"Current user authenticated: {current_user.is_authenticated}")
            print(f"Current user ID: {current_user.id}")
            print(f"Current user first name: {current_user.first_name}")

            next_page = request.args.get('next')
            print(f"Next Page: {next_page}")
            if not next_page or next_page == 'None' or not next_page.startswith('/'):
                next_page = '/passwords'
            print(f"Redirecting to: {next_page}")
            return redirect(next_page)

        flash('Invalid email or password.')
    
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))



@app.route('/passwords', methods=["GET", "POST"])
# @login_required
def passwords():
    if request.method == "POST":
        # Get the password length from the form
        pass_length = int(request.form.get("min_max"))

        # Get the password options from the form
        uppercase = request.form.get("uppercase")
        lowercase = request.form.get("lowercase")
        numbers = request.form.get("numbers")
        symbols = request.form.get("symbols")

        # Store data in session
        session['pass_length'] = pass_length
        session['uppercase'] = uppercase
        session['lowercase'] = lowercase
        session['numbers'] = numbers
        session['symbols'] = symbols

        # Generate the password
        password = password_generator(pass_length, uppercase, lowercase, numbers, symbols)

        return render_template("passwords.html", password=password, form=LoginForm())
    
    return render_template('passwords.html', form=LoginForm())




if __name__ == "__main__":
    app.run(debug=True)
