import sqlite3
import modules.db as db

def get_listed_items():
    sql="SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price,users.username FROM items LEFT JOIN users ON items.player=users.id WHERE listed_for_sale=TRUE"
    result=db.query(sql)
    return result

def check_item_owner(item_id,username):
    sql="SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price FROM items WHERE items.id=? AND(SELECT id FROM users WHERE users.username=?)=items.player AND items.listed_for_sale!=TRUE"
    return db.query(sql,[item_id,username])
