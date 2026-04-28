import sqlite3
import modules.db as db

class Offer:
    def __init__(self,id,buyer_id,item_id,item_name,gold_offer,buyer_username=""):
        self.id=id
        self.item_id=item_id
        self.item_name=item_name
        self.buyer_id=buyer_id
        self.gold_offer=gold_offer
        self.buyer_name=buyer_username
        self.offered_items=[]
        self.get_offered_items()
    
    def get_offered_items(self):
        sql="""
        SELECT items.item_name
        FROM offered_items
        LEFT JOIN items ON item_id=items.id
        WHERE offer_id=?
        """
        self.offered_items=db.query(sql,[self.id])



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
    sql="""SELECT items.id,items.item_name,items.player,marketplace_listings.marketplace_price,users.username,item_subcategories.subcategory_name AS type,item_details.trader_price,item_slots.slot_name AS slot, item_details.rarity AS rarity,item_details.item_level,stat_sheet.agility,stat_sheet.stamina,stat_sheet.strength,stat_sheet.magic,stat_sheet.armor,weapon_details.min_damage,weapon_details.max_damage,weapon_details.weapon_speed,(SELECT style FROM damage_styles WHERE id=weapon_details.damage_style) AS damage_style,(SELECT style FROM damage_styles WHERE id=weapon_details.secondary_style) AS secondary_style
    FROM marketplace_listings
    LEFT JOIN items ON marketplace_listings.item_id=items.id
    LEFT JOIN users on marketplace_listings.seller_id=users.id
    LEFT JOIN item_details ON item_details.item_id=items.id
    LEFT JOIN weapon_details ON weapon_details.item_id=items.id
    LEFT JOIN stat_sheet ON stat_sheet.item_id=items.id
    LEFT JOIN item_slots ON item_details.slot=item_slots.id
    LEFT JOIN item_subcategories ON item_details.item_type=item_subcategories.id
    WHERE marketplace_listings.seller_id=users.id
    AND items.item_name LIKE ?
    """
    result=db.query(sql,["%"+ query +"%"])
    return result

def check_item_owner(item_id,username):
    sql="""
    SELECT items.id,items.item_name,items.player
    FROM items WHERE items.id=? 
    AND(SELECT id FROM users WHERE users.username=?)=items.player
    """
    return db.query(sql,[item_id,username])

def check_item_is_listed(item_id,username):
    sql="""
    SELECT id,marketplace_price
    FROM marketplace_listings WHERE item_id=? 
    AND (SELECT id FROM users WHERE users.username=?)=seller_id
    """
    return db.query(sql,[item_id,username])

def get_item_details(item_id):
    sql="""
    SELECT items.id,items.item_name,items.player,users.username
    FROM items
    LEFT JOIN users ON users.id=items.player
    WHERE items.id=?
    """
    return db.query(sql,[item_id])

def put_item_for_sale(item_id,market_price):
    sql="""
    INSERT INTO marketplace_listings (item_id,seller_id,marketplace_price)
    VALUES (?,(SELECT player 
    FROM items
    WHERE id=?),?)
    """
    return db.execute(sql,[item_id,item_id,market_price])


def trade_item(item_id,buyer_username,seller_username):
    seller_id=get_player_id(seller_username)
    buyer_id=get_player_id(buyer_username)
    sql_take_money="""
    UPDATE users 
    SET gold= users.gold-(SELECT marketplace_listings.marketplace_price 
    FROM marketplace_listings WHERE item_id=? 
    AND marketplace_listings.seller_id=?) 
    WHERE users.username=?
    """
    sql_give_money="""
    UPDATE users 
    SET gold= users.gold+(SELECT marketplace_listings.marketplace_price 
    FROM marketplace_listings WHERE item_id=? 
    AND marketplace_listings.seller_id=?) 
    WHERE users.username=?
    """
    sql_delete_marketplace_listing="""
    DELETE FROM marketplace_listings
    WHERE item_id=? AND seller_id=?
    """
    sql_transfer_item="""
    UPDATE items 
    SET player=?
    WHERE items.id=? 
    AND items.player=?"""

    sql_delete_offers_from_buyer="""
    DELETE FROM trade_offers
    WHERE sold_item=?
    AND buyer_id=?
    """

    sqls=[sql_take_money,sql_give_money,sql_delete_marketplace_listing,sql_transfer_item,sql_delete_offers_from_buyer]
    parameters=[[item_id,seller_id,buyer_username],[item_id,seller_id,seller_username],[item_id,seller_id],[buyer_id,item_id,seller_id],[item_id,buyer_id]]
    result=db.execute(sqls,parameters)
    item=db.query("SELECT player,item_name FROM items WHERE items.id=?",[item_id])[0]
    print(result)
    if sqlite3.IntegrityError==type(result["error"]):
        if str(result["error"])=="CHECK constraint failed: gold >= 0":
            return "You don't have enough gold"
    elif item["player"]==buyer_id and result["rows_affected"]>=4:
        return f"You've bought {item['item_name']}"
    else:
        return "Item not available"

def cancel_listing(item_id,username):
    sql="""
    DELETE FROM marketplace_listings
    WHERE item_id=? 
    AND seller_id=(SELECT id 
    FROM users 
    WHERE users.username=?)
    """
    result=db.execute(sql,[item_id,username])
    if type(result["error"])==sqlite3.Error:
        print(result["error"])
        return "Error"
    elif result["rows_affected"]==1:
        return "Listing canceled"
    elif result["rows_affected"]==0:
        return "Listing has already been sold"

    
def get_gold_amount(username):
    sql="""
    SELECT gold
    FROM users
    WHERE username=?
    """
    gold=db.query(sql,[username])[0]["gold"]
    return gold

def check_item_not_in_offer(item_id):
    sql="""
    SELECT id
    FROM offered_items
    WHERE item_id=?
    """
    result=db.query(sql,[item_id])


def create_trade_offer(item_id,item_offers,buyer_username,gold_offer=0):
    if check_item_not_in_offer(item_id):
        return "Can't make trade offers for items that are part of another offer"
    if item_offers or gold_offer:
        buyer_id=get_player_id(buyer_username)

        sql_create_offer="""
        INSERT INTO trade_offers (sold_item,buyer_id,gold_offer)
        VALUES (?,?,?)
        RETURNING *
        """
        sql_reduce_gold="""
        UPDATE users 
        SET gold=(gold-?)
        WHERE id=?
        """
        db_changes=db.execute([sql_create_offer,sql_reduce_gold],[[item_id,buyer_id,gold_offer],[gold_offer,buyer_id]])
        print(db_changes)
        if sqlite3.IntegrityError==type(db_changes["error"]):
            if str(db_changes["error"])=="CHECK constraint failed: gold >= 0":
                return "You don't have enough gold"
        elif db_changes["error"]:
            print("Here")
            return db_changes["error"]
        elif db_changes["rows_affected"]==2:
            offer_id=db_changes["rows"][0][0]["id"]
            for item in item_offers:
                if check_item_owner(item,buyer_username):
                    sql_offer_item="""
                    INSERT INTO offered_items (offer_id,item_id)
                    VALUES (?,?)
                    """
                    print(db.execute(sql_offer_item,[offer_id,item]))
            return "Trade offer created"
    else:
        return "You must offer gold or items"

def get_my_offers(username):
    player_id=get_player_id(username)
    offers=[]
    sql="""
    SELECT trade_offers.id,sold_item,buyer_id,gold_offer,items.item_name,player
    FROM trade_offers
    LEFT JOIN items ON items.id=trade_offers.sold_item
    WHERE buyer_id=?
    """
    my_offers=db.query(sql,[player_id])
    for offer in my_offers:
        offers.append(Offer(offer["id"],offer["buyer_id"],offer["sold_item"],offer["item_name"],offer["gold_offer"],))
    return offers


def get_offers_for_me(username):
    player_id=get_player_id(username)
    offers=[]
    sql="""
    SELECT trade_offers.id,sold_item,player,buyer_id,gold_offer,items.item_name
    FROM trade_offers
    LEFT JOIN items ON items.id=trade_offers.sold_item
    WHERE player=?
    """
    my_offers=db.query(sql,[player_id])
    for offer in my_offers:
        offers.append(Offer(offer["id"],offer["buyer_id"],offer["sold_item"],offer["item_name"],offer["gold_offer"]))
    return offers

def get_offers_for_item(item_id):
    offers=[]
    sql="""
    SELECT trade_offers.id,sold_item,player,username,buyer_id,gold_offer,items.item_name
    FROM trade_offers
    LEFT JOIN items ON items.id=trade_offers.sold_item
    LEFT JOIN users ON items.player=users.id
    WHERE sold_item=?
    """
    my_offers=db.query(sql,[item_id])
    for offer in my_offers:
        offers.append(Offer(offer["id"],offer["buyer_id"],offer["sold_item"],offer["item_name"],offer["gold_offer"],offer["username"]))
    return offers

def modify_listing(item_id,username,new_price):

    sql="""
    UPDATE marketplace_listings
    SET marketplace_price=?
    WHERE item_id=?
    AND seller_id=(SELECT id
    FROM users
    WHERE username=?)
    """
    db.execute(sql,[new_price,item_id,username])



def cancel_offer(offer_id,username):
    buyer_id=get_player_id(username)
    return_gold_sql="""
    UPDATE users
    SET gold=gold+(SELECT gold_offer
    FROM trade_offers
    WHERE id=?
    AND buyer_id=?)
    WHERE id=?
    """
    delete_sql="""
    DELETE FROM trade_offers
    WHERE id=? AND buyer_id=?
    """
    result=db.execute([return_gold_sql,delete_sql],[[offer_id,buyer_id,buyer_id],[offer_id,buyer_id]])
    if result["error"]:
        print(result["error"])
        return "Database error"
    if result["rows_affected"]>0:
        return "Offer removed"
    else:
        return "Offer no longer exists"
    

def accept_offer(offer_id,username,buyer_id,item_id):
    seller_id=get_player_id(username)
    delete_marketplace_listing_sql="""
    DELETE FROM marketplace_listings
    WHERE item_id=? AND seller_id=?
    """
    transfer_offered_items_sql="""
    UPDATE items
    SET player=?
    WHERE id IN (
    SELECT item_id
    FROM offered_items
    WHERE offer_id=?)
    AND player=?
    AND EXISTS (
    SELECT id 
    FROM items
    WHERE id=?
    AND player=?)
    """
    transfer_offered_money="""
    UPDATE users
    SET gold=gold+(
    SELECT gold_offer
    FROM trade_offers
    WHERE id=?
    AND sold_item=?)
    WHERE id=?
    AND EXISTS (
    SELECT id 
    FROM items
    WHERE id=?
    AND player=?)
    """
    transfer_sold_item_sql="""
    UPDATE items
    SET player=?
    WHERE id=?
    AND player=?
    AND EXISTS (
    SELECT id 
    FROM trade_offers
    WHERE id=?
    AND buyer_id=?
    AND sold_item=?)
    """
    delete_trade_offer_sql="""
    DELETE FROM trade_offers
    WHERE id=?
    AND buyer_id=?
    AND EXISTS (
    SELECT id 
    FROM items
    WHERE player=? AND id=?)
    """

    delete_marketplace_listing_parameters=[item_id,seller_id]
    tranfer_offered_items_parameters=[seller_id,offer_id,buyer_id,item_id,seller_id]
    transfer_offered_money_parameters=[offer_id,item_id,seller_id,item_id,seller_id]
    transfer_sold_item_parameters=[buyer_id,item_id,seller_id,offer_id,buyer_id,item_id]
    delete_trade_offer_parameters=[offer_id,buyer_id,buyer_id,item_id]
    parameters=[delete_marketplace_listing_parameters,tranfer_offered_items_parameters,transfer_offered_money_parameters,transfer_sold_item_parameters,delete_trade_offer_parameters]
    sqls=[delete_marketplace_listing_sql,transfer_offered_items_sql,transfer_offered_money,transfer_sold_item_sql,delete_trade_offer_sql]

    result=db.execute(sqls,parameters)

    if result["rows_affected"]>3:
        return "Trade offer accepted"
    
    else:
        return "Offer no longer available"