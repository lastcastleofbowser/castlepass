# CastlePass ⛫ 

<i>A Fortress for your Passwords</i>


Password generator and manager. My final project submission for Harvard's CS50x Course.

Video Demo: https://youtu.be/dSM5KiwHoxQ

# Description
With today's society spending more time online, it is important to protect ourselves from risks in the digital space. One of the most effective ways to do this is to use strong, unique passwords for your separate accounts. Reusing passwords across multiple accounts is bad practice and can lead to your data and sensitive information being compromised. Likewise, weak, guessable passwords can easily allow people access into your account, which puts you at significant risk.

To help solve this problem I decided to create CastlePass, a fortress for your passwords!

CastlePass stores all your passwords in one place, securely. It can generate customised passwords and allows users to view, edit and delete their passwords all in one place. Generated passwords must be a minimum of 6 characters and can include lowercase and uppercase letters, numbers and special characters.

# Features
- User registration and log in
- Add, edit and delete passwords
- Customise generated passwords by length, letter case, numbers and special characters
- Toggle password visibility for security
- Quick password-to-clipboard copy

# Technologies Used
- Python
- JavaScript
- Flask
- Jinja
- SQL
- Bootstrap
- Werkzeug Security

# Code & Organisation

The Castlepass website is divided into two main sections: password management and password generation. Logic for the password generation is within a separate password_gen.py file and is called upon within the main app.py file.

app.py contains the functions responsible for the login and registration. It also handles the information taken from the add, edit and delete forms sent from the password manager when submitted. It communicates with the SQL database to either insert, delete or update values.

Backend information is stored within a SQLite database called castlepass.db. The tables used are a users table to handle registration and login; a passwords table to store users' passwords; and a generator table that stores all generated passwords so that they can be displayed in each user's generated passwords table.

# Folders
1. Templates - this folder contains the HTML pages that are visible to the user, including flask's master layout called layout.html, from which all other HTML files take their layout.

2. Static - inside this folder are my CSS and JS files alongside  any images used for this project.



# Password Generator Video

https://github.com/lastcastleofbowser/castlepass/assets/123087687/9f722f93-6fb0-4619-8e50-79737d0371ff


# Authors
Christian Willcox
