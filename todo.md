Password manager
- Add ☑️, edit ☑️ and delete ☑️ passwords
- Search all your passwords 🟠
- Toggle password visibility ☑️

Password generator ✅
- Customise generated passwords by ☑️
    + length (>8 <25)
    -- Toggleable --
    + capital letters 
    + numbers 
    + special characters 
- Quick password-to-clipboard copy ☑️

Log in/Register ✅
- User registration ☑️
    + password strength checker
- Log in ☑️
    + show different navbar for logged in users ☑️
- Logout ☑️


Database
CREATE TABLE users (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL);
CREATE UNIQUE INDEX email ON users(email);

CREATE TABLE passwords (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER NOT NULL,
site_address TEXT,
site_username TEXT,
site_password TEXT NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(person_id)
);

CREATE TABLE generator (
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER NOT NULL,
time_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
gen_password TEXT NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(person_id)
);