import sqlite3
import modules.db as db


def get_player_items(username):
    sql="""
    SELECT * 
    FROM items 
    LEFT JOIN marketplace_listings ON marketplace_listings.item_id=items.id
    LEFT JOIN offered_items ON offered_items.item_id=items.id
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?)
    AND marketplace_listings.item_id IS NULL
    AND offered_items.item_id IS NULL
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
    if result["error"]:
        return "Database error"
    if result["rows_affected"]==1:
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
    SELECT gold,username,stamina,strength,agility,magic,set_stats,SUM(stamina+strength+agility+magic) AS total_stats
    FROM users
    LEFT JOIN stat_sheet ON player_id=users.id
    WHERE username=?
    """
    return db.query(user_info_sql,[username])


