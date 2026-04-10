import sqlite3
import modules.db as db


def get_player_id(username):
    sql="""
    SELECT id
    FROM users 
    WHERE users.username=?
    """
    result=db.query(sql,[username])
    return result[0]["id"]

def check_balance(item_id,username):
    sql="""
    SELECT users.id 
    FROM users 
    WHERE users.username=? AND 
    users.gold>=(SELECT items.marketplace_price 
    FROM items WHERE items.id=?)
    """
    result=db.query(sql,[username,item_id])
    return result[0] if result else False

def get_listed_items(query):
    if not query:
        query=""
    sql="""SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price,users.username 
    FROM items 
    LEFT JOIN users ON items.player=users.id 
    WHERE listed_for_sale=TRUE AND items.item_name 
    LIKE ?
    """
    result=db.query(sql,["%"+ query +"%"])
    return result

def check_item_owner(item_id,username):
    sql="""
    SELECT items.id,items.item_name,items.player,items.listed_for_sale,items.marketplace_price 
    FROM items WHERE items.id=? 
    AND(SELECT id FROM users WHERE users.username=?)=items.player 
    AND items.listed_for_sale!=TRUE
    """
    return db.query(sql,[item_id,username])

def put_item_for_sale(item_id,market_price):
    sql="""
    UPDATE items 
    SET listed_for_sale=TRUE,marketplace_price=? 
    WHERE id=?
    """
    return db.execute(sql,[market_price,item_id])


def trade_item(item_id,buyer_username,seller_username):
    seller_id=get_player_id(seller_username)
    buyer_id=get_player_id(buyer_username)
    sql_take_money="""
    UPDATE users 
    SET gold= users.gold-(SELECT items.marketplace_price 
    FROM items WHERE items.id=? 
    AND items.player=?) 
    WHERE users.username=?
    """
    sql_give_money="""
    UPDATE users 
    SET gold= users.gold+(SELECT items.marketplace_price 
    FROM items 
    WHERE items.id=? 
    AND items.player=?) 
    WHERE users.username=?
    """
    sql_transfer_item="""
    UPDATE items 
    SET player=?,listed_for_sale=FALSE 
    WHERE items.id=? 
    AND items.player=?"""
    sqls=[sql_take_money,sql_give_money,sql_transfer_item]
    parameters=[[item_id,seller_id,buyer_username],[item_id,seller_id,seller_username],[buyer_id,item_id,seller_id]]
    result=db.execute(sqls,parameters)
    item=db.query("SELECT player,item_name FROM items WHERE items.id=?",[item_id])[0]
    print(result)
    if result==3 and item["player"]==buyer_id:
        return f"You've bought {item["item_name"]}"
    elif sqlite3.IntegrityError==type(result):
        if str(result)=="CHECK constraint failed: gold >= 0":
            return "You don't have enough gold"
    else:
        return "Item not available"

def cancel_listing(item_id,username):
    sql="""
    UPDATE items 
    SET listed_for_sale=FALSE 
    WHERE items.id=? 
    AND player=(SELECT id 
    FROM users 
    WHERE users.username=?)
    """
    result=db.execute(sql,[item_id,username])
    if result==1:
        return "Listing canceled"
    elif result==0:
        return "Listing has already been sold"
    else:
        print(result)
        return "Error"
    
def get_gold_amount(username):
    sql="""
    SELECT gold
    FROM users
    WHERE username=?
    """
    gold=db.query(sql,[username])[0]["gold"]
    return gold