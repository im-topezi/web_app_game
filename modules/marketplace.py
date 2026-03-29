import sqlite3
import modules.db as db

def get_listed_items(query):
    if not query:
        query=""
    sql="SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price,users.username FROM items LEFT JOIN users ON items.player=users.id WHERE listed_for_sale=TRUE AND items.item_name LIKE ?"
    result=db.query(sql,["%"+ query +"%"])
    return result

def check_item_owner(item_id,username):
    sql="SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price FROM items WHERE items.id=? AND(SELECT id FROM users WHERE users.username=?)=items.player AND items.listed_for_sale!=TRUE"
    return db.query(sql,[item_id,username])

def put_item_for_sale(item_id,market_price):
    sql="UPDATE items SET listed_for_sale=TRUE,marketplace_price=? WHERE id=?"
    return db.execute(sql,[market_price,item_id])