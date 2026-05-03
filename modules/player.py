import sqlite3
import modules.db as db

def get_health_amount(username):
    sql="""
    SELECT health,max_health
    FROM users
    WHERE username=?
    """
    result=db.query(sql,[username])[0]
    health={
        "current":result["health"],
        "max":result["max_health"]
    }
    return health

def update_max_health(username):
    old_health=get_health_amount(username)
    stats=get_total_stats(username)
    max_health=100+(stats["stamina"]*10)
    if old_health["current"]==old_health["max"] or old_health["current"]>max_health:
        sql="""
        UPDATE users
        SET max_health=?,health=?
        WHERE username=?
        """
        health=max_health
    else:
        sql="""
        UPDATE users
        SET max_health=?,health=?
        WHERE username=?
        """
        health=old_health["current"]



    db.execute(sql,[max_health,health,username])

def get_equipped_items(username):
    sql="""
    SELECT items.id,items.player,items.item_name,item_subcategories.subcategory_name AS type,item_details.trader_price,item_slots.slot_name AS slot, item_details.rarity AS rarity,item_details.item_level,stat_sheet.agility,stat_sheet.stamina,stat_sheet.strength,stat_sheet.magic,stat_sheet.armor,weapon_details.min_damage,weapon_details.max_damage,weapon_details.weapon_speed,(SELECT style FROM damage_styles WHERE id=weapon_details.damage_style) AS damage_style,(SELECT style FROM damage_styles WHERE id=weapon_details.secondary_style) AS secondary_style
    FROM equipped_items 
    LEFT JOIN items ON equipped_items.item_id=items.id
    LEFT JOIN item_details ON item_details.item_id=items.id
    LEFT JOIN weapon_details ON weapon_details.item_id=items.id
    LEFT JOIN stat_sheet ON stat_sheet.item_id=items.id
    LEFT JOIN item_slots ON item_details.slot=item_slots.id
    LEFT JOIN item_subcategories ON item_details.item_type=item_subcategories.id
    WHERE equipped_items.player_id=(SELECT id 
    FROM users 
    WHERE username=?)
    """
    items=db.query(sql,[username])
    return items

def get_total_stats(username):
    sql_get_player_stat_sheet="""
    SELECT agility,stamina,strength,magic
    FROM stat_sheet
    WHERE player_id=(SELECT id 
    FROM users 
    WHERE username=?)
    """
    player_stats=db.query(sql_get_player_stat_sheet,[username])[0]
    sql_item_stats="""
    SELECT IFNULL(SUM(stat_sheet.agility),0) AS agility,
    IFNULL(SUM(stat_sheet.stamina),0) AS stamina,
    IFNULL(SUM(stat_sheet.strength),0) AS strength,
    IFNULL(SUM(stat_sheet.magic),0) AS magic,
    IFNULL(SUM(stat_sheet.armor),0) AS armor
    FROM equipped_items
    LEFT JOIN stat_sheet ON equipped_items.item_id=stat_sheet.item_id
    WHERE equipped_items.player_id=(SELECT id 
    FROM users 
    WHERE username=?)
    AND stat_sheet.id IS NOT NULL
    """
    item_stats=db.query(sql_item_stats,[username])
    sql_heavy_items="""
    SELECT COUNT(equipped_items.item_id) AS item_count
    FROM equipped_items
    LEFT JOIN item_details ON equipped_items.item_id=item_details.item_id
    WHERE equipped_items.player_id=(SELECT id 
    FROM users 
    WHERE username=?)
    AND item_type IN (SELECT id
    FROM item_subcategories
    WHERE subcategory_name IN ("Metal Armor","Mace","Axe"))
    """
    heavy_items=db.query(sql_heavy_items,[username])
    stats={
        "agility":player_stats["agility"]+item_stats[0]["agility"],
        "magic":player_stats["magic"]+item_stats[0]["magic"],
        "stamina":player_stats["stamina"]+item_stats[0]["stamina"],
        "strength":player_stats["strength"]+item_stats[0]["strength"],
        "armor":item_stats[0]["armor"],
        "speed_modifier":1,
        "physical_modifier":1,
        "magical_modifier":1
    }
    stats["physical_modifier"]+=(stats["strength"]/1000)
    stats["magical_modifier"]+=(stats["magic"]/1000)


    if heavy_items[0]["item_count"]>0:
        total_stats=stats["agility"]+stats["magic"]+stats["stamina"]+stats["strength"]
        strength_modifier=stats["strength"]/total_stats*10
        heavy_items=heavy_items[0]["item_count"]
        if strength_modifier<heavy_items:
            stats["speed_modifier"]+=heavy_items-strength_modifier
    return stats
    

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
    ORDER BY item_slots.slot_name,item_subcategories.subcategory_name,item_details.item_level,items.item_name
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
    
def check_player_exists(username):
    sql="""
    SELECT id
    FROM users
    WHERE username=?
    """
    return db.query(sql,[username])

def get_user_worlds(username):
    sql="""
    SELECT id,world_name,difficulty,visited
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
    
def drink_health_potion(item,username):
    stats=get_total_stats(username)
    healed_amount=item["item_level"]*2+50+stats["magic"]*3
    health=get_health_amount(username)
    healed_health=healed_amount+health["current"]
    if healed_health>health["max"]:
        healed_health=health["max"]
    heal_sql="""
    UPDATE users
    SET health=?
    WHERE username=?
    """
    db.execute(heal_sql,[healed_health,username])
    drop_item(item["id"],username)
    return f"You heal for {healed_health-health["current"]} health"
    
def deal_damage_to_player(username,damage):
    health=get_health_amount(username)
    if damage>=health["current"]:
        sql_deal_damage_to_player="""
        UPDATE users
        SET health=1
        WHERE username=?
        """
        result=db.execute(sql_deal_damage_to_player,[username])
    else:
        sql_deal_damage_to_player="""
        UPDATE users
        SET health=health-?
        WHERE username=?
        """
        result=db.execute(sql_deal_damage_to_player,[damage,username])

def unequip_item(item_id,username):
    sql="""
    DELETE FROM equipped_items
    WHERE item_id=?
    AND player_id=(SELECT id 
    FROM users 
    WHERE username=?)
    """
    result=db.execute(sql,[item_id,username])
    if result["rows_affected"]>=1:
        return "Item unequipped"
    else:
        return "You can't unequip that"

def use_item(item_id,username):
    sql="""
    SELECT items.id,items.player,items.item_name,item_slots.slot_name AS slot,item_level
    FROM items 
    LEFT JOIN marketplace_listings ON marketplace_listings.item_id=items.id
    LEFT JOIN offered_items ON offered_items.item_id=items.id
    LEFT JOIN equipped_items ON equipped_items.item_id=items.id
    LEFT JOIN item_details ON item_details.item_id=items.id
    LEFT JOIN item_slots ON item_details.slot=item_slots.id
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?)
    AND items.id=?
    AND marketplace_listings.item_id IS NULL
    AND offered_items.item_id IS NULL
    AND equipped_items.item_id IS NULL
    """
    result=db.query(sql,[username,item_id])
    if result:
        item=result[0]
        if item["item_name"]=="Health Potion":
            return drink_health_potion(item,username)
        elif item["slot"]:
            sql_get_slot_information="""
            SELECT item_id
            FROM equipped_items
            WHERE player_id=?
            AND slot=(SELECT id
            FROM item_slots
            WHERE slot_name=?)
            """
            slot_result=db.query(sql_get_slot_information,[item["player"],item["slot"]])
            if slot_result:
                sql_update_slot="""
                UPDATE equipped_items
                SET item_id=?
                WHERE player_id=?
                AND slot=(SELECT id
                FROM item_slots
                WHERE slot_name=?)
                """
                update_result=db.execute(sql_update_slot,[item_id,item["player"],item["slot"]])
                print(update_result)
            else:
                sql_insert_slot="""
                INSERT INTO equipped_items (item_id,player_id,slot)
                VALUES (?,?,(SELECT id
                FROM item_slots
                WHERE slot_name=?))
                """
                insert_result=db.execute(sql_insert_slot,[item_id,item["player"],item["slot"]])
                print(insert_result)
            return f"{item['item_name']} equipped"
    else:
        return "Item not available"


def check_if_in_combat(username):
    sql="""
    SELECT npc_id,combat_action,damage,style,player_swing_timer,npc_swing_timer,damage_type,attacker
    FROM combat_log
    LEFT JOIN damage_styles ON damage_style=damage_styles.id
    LEFT JOIN damage_types ON damage_styles.type_id=damage_types.id
    WHERE player_id=(
    SELECT id
    FROM users
    WHERE username=?)
    ORDER BY combat_log.id DESC
    """
    result=db.query(sql,[username])
    return result

def delete_combat_log(username):
    sql="""
    DELETE FROM combat_log
    WHERE player_id=(
    SELECT id
    FROM users
    WHERE username=?)
    """
    db.execute(sql,[username])

def sell_item_on_blackmarket(item_id,username):

    sql_transfer_money="""
    UPDATE users
    SET gold=gold+(SELECT trader_price 
    FROM item_details
    WHERE item_id=?)
    WHERE username=?
    """
    db.execute(sql_transfer_money,[item_id,username])
    sql_transfer_item="""
    UPDATE items
    SET player=NULL,container=NULL,npc=NULL
    WHERE id=? AND player=(
    SELECT id
    FROM users
    WHERE username=?)
    """
    return db.execute(sql_transfer_item,[item_id,username])