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
from login_required import login_required

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
app.config["SESSION_PERMANENT"] = False
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

# --- DEFINE PASSWORD MANAGER FORM ---
class PasswordManagerForm(FlaskForm):
    website = StringField('Website', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()]) 
    submit = SubmitField('Save')

   
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
                flash(f"Please fill out all fields")
                return redirect("/register")

            # Check if the email already exists
            connection = sqlite3.connect('castlepass.db')  
            
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash(f"Email already exists")
                return redirect("/register")

            # Check password is at least 6 characters long
            if len(password) < 6:
                flash(f"Password should be at least 6 characters long")
                return redirect("/register")
           
            # Check email is correct format 
            if email.find("@") == -1 or email.find(".") == -1:
                flash(f"Check your email is formatted correctly")
                return redirect("/register")

            # Create a new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            user = User(None, first_name, last_name, email, hashed_password)
            user.save()

            return render_template("login.html", form=LoginForm())

        finally:    
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    else:
        return render_template("register.html")



# @app.route('/login', methods=['GET', 'POST'])
# def login():  
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

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            flash(f"Must provide email")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(f"Must provide password")
            return redirect("/login")
        
        # Open the database connection
        connection = sqlite3.connect('castlepass.db')
        cursor = connection.cursor()

        # Query database for username
        cursor.execute(
            "SELECT * FROM users WHERE email = ?", (request.form.get("email"),)
        )

        # Fetch all the rows
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][4], request.form.get("password")
        ):
            flash(f"Invalid email and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0][1]

        # Close the database connection
        cursor.close()
        connection.close()

        # Redirect user to password generator page
        flash(f"Logged in as: {rows[0][1]} {rows[0][2]}")
        return redirect("/pass_manager")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    


@app.route('/logout')
# @login_required
def logout():
    session.clear()
    flash('Logged out successfully.')
    return render_template('index.html')


@app.route('/pass_generator', methods=["GET", "POST"])
# @login_required
def pass_generator():
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

        password_history = False

        if password:
            password_history = True

        # Open the database connection
        connection = sqlite3.connect('castlepass.db')
        cursor = connection.cursor()

        user_id = session["user_id"]
        
        # Store the password in the database
        cursor.execute(
            "INSERT INTO generator (gen_password, user_id) VALUES (?, ?)",
            (password, user_id)
        )

        # Retrieve the password in the database
        cursor.execute(
        "SELECT gen_password, time_generated FROM generator WHERE user_id = ? ORDER BY time_generated DESC",
        (user_id,)
        )
        entries = cursor.fetchall()

        # Commit the changes    
        connection.commit()

        if cursor:
                cursor.close()
        if connection:
            connection.close()

        return render_template("pass_generator.html", password=password, password_history=password_history, entries=entries, form=LoginForm())
    
    return render_template('pass_generator.html', form=LoginForm())


@app.route('/pass_manager', methods=["GET", "POST"])
@login_required
def pass_manager():
    """Password Manager"""
    form = PasswordManagerForm()
    user_id = session["user_id"]
    
    connection = sqlite3.connect('castlepass.db')
    cursor = connection.cursor()

    if not user_id:
        flash(f"Please login to access password manager")
        return redirect("/login")
    
    elif user_id:
        # Retrieve users passwords in the database
        cursor.execute(
        "SELECT site_address, site_username, site_password, id FROM passwords WHERE user_id = ?",
        (user_id,)
        )
        entries = cursor.fetchall()
    
    if request.method == "GET":
        return render_template('pass_manager.html', entries=entries, form=form)

    # Get password details from the form
    website = request.form.get("website")
    username = request.form.get("username")
    password = str(request.form.get("password"))
    
    if request.method == "POST":
        try:
            connection = sqlite3.connect('castlepass.db')
            cursor = connection.cursor()

            # Check all parameters are filled
            if not website or not username or not password:
                flash(f"Please fill out all fields")
                return redirect("/pass_manager")
            
            # Insert new row into database
            cursor.execute("INSERT INTO passwords (user_id, site_address, site_username, site_password) VALUES (?, ?, ?, ?)", 
            (user_id, website, username, password))

            # Commit the changes
            connection.commit()

            # Retrieve updated passwords from the database
            cursor.execute(
            "SELECT site_address, site_username, site_password, id FROM passwords WHERE user_id = ?",
            (user_id,)
            )
            entries = cursor.fetchall()

            return render_template('pass_manager.html', entries=entries, form=form)
        
        finally:    
            if cursor:
                cursor.close()
            if connection:
                connection.close()


@app.route('/delete_password', methods=["POST"])
@login_required  
def delete_password():
    """Password Deletion"""
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login to access password manager")
        return redirect("/login")

    delete_website = request.form.get("delete_website")
    delete_password_id = request.form.get("delete_password_id")

    if delete_website and delete_password_id:

        connection = sqlite3.connect('castlepass.db')
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM passwords WHERE user_id = ? AND site_address = ? AND id = ?",
                        (user_id, delete_website, delete_password_id))
            connection.commit()
            flash(f"Password {delete_website} deleted successfully")

        except sqlite3.Error as e:
            print("Error deleting password:", e)
            flash("Error deleting password")

        finally:
            cursor.close()
            connection.close()

    return redirect("/pass_manager")


@app.route('/edit_form', methods=["POST"])
@login_required
def edit_password():
    """Edit Password"""
    user_id = session.get("user_id")

    edit_website = request.form.get("editWebsite")
    edit_username = request.form.get("editUsername")
    edit_password = request.form.get("editPassword")
    password_id = request.form.get("passwordId")

    print(f"Website: {edit_website}")
    print(f"Username: {edit_username}")
    print(f"Password: {edit_password}")
    print(f"Password ID: {password_id}")

    if not user_id:
        flash("Please login to access password manager")
        return redirect("/login")
   
    if request.method == "POST":
        
        connection = sqlite3.connect('castlepass.db')
        cursor = connection.cursor()

        try:

            cursor.execute("UPDATE passwords SET site_address = ?, site_username = ?, site_password = ? WHERE id = ?",
            (edit_website, edit_username, edit_password, password_id))
            connection.commit()
            flash(f"{edit_website} updated successfully")
            return redirect("/pass_manager")
    
        except sqlite3.Error as e:
            print(f"Error editing {edit_website} information:", e)
            flash(f"Error editing {edit_website} information")

        finally:
            cursor.close()
            connection.close()
    
    return redirect("/pass_manager")


if __name__ == "__main__":
    app.run(debug=True)
