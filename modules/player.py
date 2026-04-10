import sqlite3
import modules.db as db


def get_player_items(username):
    sql="""
    SELECT * 
    FROM items 
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?) 
    AND listed_for_sale!=TRUE
    """
    items=db.query(sql,[username])
    return items


def drop_item(item_id,player):
    sql="""
    DELETE FROM items 
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?) 
    AND id=?
    """
    result=db.execute(sql,[player,item_id])
    if result==1:
        return "Item dropped"
    

def get_user_worlds(username):
    sql="""
    SELECT *
    FROM worlds
    WHERE player=(SELECT id
    FROM users WHERE username=?)
    """
    return db.query(sql,[username])

def get_player_info(username):
    user_info_sql="""
    SELECT gold
    FROM users
    WHERE username=?
    """
    return db.query(user_info_sql,[username])


