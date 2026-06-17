import sqlite3
import modules.db as db
from werkzeug.security import generate_password_hash,check_password_hash

def create_new_user(username,password1,password2):
    if password1 != password2:
        return "Passwords dont match"
    if not password1:
        return "You must have a password"
    if not username:
        return "You must have a username"
    if len(password1)<5:
        return "Password must be at least 5 characters"
    if len(username)>10:
        return "Username can't be longer than 10 characters"
    if not username.islower():
        return "Characters in username must be lowercase"
    if not username.isalnum():
        return "Username can contain letters and numbers only"
    if len(password1)>20:
        return "Password can't be more than 20 characters"
    password_hash=generate_password_hash(password1)
    sql="""
    INSERT INTO users (username, password_hash) 
    VALUES (?,?)
    RETURNING id
    """
    result=db.execute(sql,[username,password_hash])
    if type(result["error"]) is sqlite3.IntegrityError:
        return "Username must be unique"
    if result["rows_affected"]==1:
        sql_assign_stat_sheet="""
        INSERT INTO stat_sheet (player_id)
        VALUES (?)
        """
        db.execute(sql_assign_stat_sheet,[result["rows"][0][0]["id"]])
        return "User created succesfully"
    else:
        return "Database error"

def login_succesfully(username,password):
    sql="""
    SELECT password_hash 
    FROM users 
    WHERE username = ?
    """
    query_result=db.query(sql,[username])
    if query_result:
        password_hash=query_result[0]["password_hash"]
        return check_password_hash(password_hash,password)
    else:
        return False
    