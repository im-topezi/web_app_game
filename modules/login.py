import sqlite3
import modules.db as db
from werkzeug.security import generate_password_hash,check_password_hash

def create_new_user(username,password1,password2):
    if password1 != password2:
        return "Passwords dont match"
    password_hash=generate_password_hash(password1)
    sql="INSERT INTO users (username, password_hash) VALUES (?,?)"
    result=db.execute(sql,[username,password_hash])
    if type(result) is sqlite3.IntegrityError:
        return "Username must be unique"
    if result==1:
        return "User created succesfully"
    else:
        return "Database error"

def login_succesfully(username,password):
    sql="SELECT password_hash FROM users WHERE username = ?"
    query_result=db.query(sql,[username])
    if query_result:
        password_hash=query_result[0]["password_hash"]
        return check_password_hash(password_hash,password)
    else:
        return False
    