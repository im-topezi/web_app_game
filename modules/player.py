import sqlite3
import modules.db as db


def get_player_items(username):
    sql="""
    SELECT items.id,items.player,items.item_name,item_subcategories.subcategory_name AS type,item_details.trader_price,item_slots.slot_name AS slot, item_details.rarity AS rarity,item_details.item_level,stat_sheet.agility,stat_sheet.stamina,stat_sheet.strength,stat_sheet.magic,stat_sheet.armor,weapon_details.min_damage,weapon_details.max_damage,weapon_details.weapon_speed,(SELECT style FROM damage_styles WHERE id=weapon_details.damage_style) AS damage_style,(SELECT style FROM damage_styles WHERE id=weapon_details.secondary_style) AS secondary_style
    FROM items 
    LEFT JOIN marketplace_listings ON marketplace_listings.item_id=items.id
    LEFT JOIN offered_items ON offered_items.item_id=items.id
    LEFT JOIN equipped_items ON equipped_items.item_id=items.id
    LEFT JOIN item_details ON item_details.item_id=items.id
    LEFT JOIN weapon_details ON weapon_details.item_id=items.id
    LEFT JOIN stat_sheet ON stat_sheet.item_id=items.id
    LEFT JOIN item_slots ON item_details.slot=item_slots.id
    LEFT JOIN item_subcategories ON item_details.item_type=item_subcategories.id
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?)
    AND marketplace_listings.item_id IS NULL
    AND offered_items.item_id IS NULL
    AND equipped_items.item_id IS NULL
    """
    items=db.query(sql,[username])
    return items


def delete_world(world_id,username):
    sql="""
    DELETE FROM worlds
    WHERE id=? 
    AND player=(SELECT id 
    FROM users 
    WHERE username=?) 
    """
    result=db.execute(sql,[world_id,username])
    if result["error"]:
        print(result)
        return "Database error"
        
    if result["rows_affected"]>=1:
        return "World destroyed!"

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
    if result["rows_affected"]>=1:
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


def set_stats(username,agility,magic,stamina,strength,total_stats):
    sql_get_stat_sheet="""
    SELECT agility,magic,stamina,strength
    FROM stat_sheet
    WHERE player_id=(
    SELECT id
    FROM users
    WHERE username=?)
    """
    existing_stats=db.query(sql_get_stat_sheet,[username])[0]
    if agility<existing_stats["agility"] or magic<existing_stats["magic"] or stamina<existing_stats["stamina"] or strength<existing_stats["strength"]:
        return "Stat can't be less then existing stat"
    sql_update_stat_sheet="""
    UPDATE stat_sheet
    SET agility=?,magic=?,stamina=?,strength=?
    WHERE player_id=(
    SELECT id
    FROM users
    WHERE username=? AND set_stats=FALSE)
    AND player_id IS NOT NULL
    """
    result=db.execute(sql_update_stat_sheet,[agility,magic,stamina,strength,username])
    print(result)
    if result["rows_affected"]==1:
        if total_stats==15:
            sql_lock_stats="""
            UPDATE users
            SET set_stats=TRUE
            WHERE username=?
            """
            db.execute(sql_lock_stats,[username])
        return "Stats updated"
    else:
        return "All skillpoints have already been spent"