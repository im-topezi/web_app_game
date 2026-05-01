import sqlite3,random
import modules.db as db
import modules.player as player
import modules.combat as combat

def tile_details(tile_id):
    tile={
        "connected":{
            "north":False,
            "south":False,
            "east":False,
            "west":False
        },
        "objects":[],
        "npcs":[],
        "tile_type":"void"
    }
    get_paths_sql="""
    SELECT first_tile AS tile
    FROM paths
    WHERE second_tile=?
    UNION
    SELECT second_tile AS tile
    FROM paths
    WHERE first_tile=?
    """
    paths=db.query(get_paths_sql,[tile_id,tile_id])
    if paths:

        for route in paths:
            get_coordinates_sql="""
            SELECT x_coordinate-(SELECT x_coordinate
            FROM tiles
            WHERE id=?) AS x_coordinate,y_coordinate-(SELECT y_coordinate
            FROM tiles
            WHERE id=?) AS y_coordinate
            FROM tiles
            WHERE id=?
            """
            coordinates=db.query(get_coordinates_sql,[tile_id,tile_id,route["tile"]])[0]
            if coordinates["x_coordinate"]>0:
                tile["connected"]["west"]=route["tile"]
            elif coordinates["x_coordinate"]<0:
                tile["connected"]["east"]=route["tile"]
            if coordinates["y_coordinate"]>0:
                tile["connected"]["north"]=route["tile"]
            elif coordinates["y_coordinate"]<0:
                tile["connected"]["south"]=route["tile"]


    sql_npc="""
    SELECT * 
    FROM npcs 
    WHERE tile=?
    """
    sql_container="""
    SELECT * 
    FROM containers 
    WHERE tile=?
    """

    sql_type="""
    SELECT tile_type
    FROM tiles
    WHERE id=?
    """

    tile["npcs"]=db.query(sql_npc,[tile_id])
    tile["containers"]=db.query(sql_container,[tile_id])
    tile["tile_type"]=db.query(sql_type,[tile_id])[0]["tile_type"]
    return tile




def get_container_items(container_id):
    sql="""
    SELECT * 
    FROM items 
    WHERE container=?
    """
    items=db.query(sql,[container_id])
    return items

def take_item(item_id,player):
    sql="""
    UPDATE items 
    SET player=(SELECT id 
    FROM users 
    WHERE username=?), npc=NULL,container=NULL  
    WHERE id=?
    """
    result=db.execute(sql,[player,item_id])
    return result



def generate_container_placement():
    pass



def visit_world(world_id,username):
    visit_sql="""
    UPDATE worlds
    SET visited=TRUE
    WHERE id=?
    """
    db.execute(visit_sql,[world_id])

    set_location_sql="""
    INSERT INTO location (player,tile)
    SELECT worlds.player,tiles.id 
    FROM tiles 
    LEFT JOIN worlds 
    ON tiles.world_id=worlds.id
    WHERE tiles.x_coordinate=0 AND tiles.y_coordinate=0 AND tiles.world_id=?
    """
    db.execute(set_location_sql,[world_id])
    
    get_location_sql="""
    SELECT tile 
    FROM location
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?)
    """
    return db.query(get_location_sql,[username])


def check_if_in_game(username):
    sql="""
    SELECT tile
    FROM location
    WHERE player=(SELECT id 
    FROM users
    WHERE username=?)
    """
    return db.query(sql,[username])


def move(target_tile_id,current_tile_id):
    check_path_sql="""
    SELECT id
    FROM paths
    WHERE (first_tile=? AND second_tile=?) 
    OR (second_tile=? AND first_tile=?)
    """
    path_exists=db.query(check_path_sql,[target_tile_id,current_tile_id,target_tile_id,current_tile_id])
    if path_exists:
        return True
    return False

def update_location(current_tile_id,target_tile_id,username):
    if not target_tile_id:
        delete_location_sql="""
        DELETE FROM location
        WHERE tile=? 
        AND player=(SELECT id 
        FROM users
        WHERE username=?)
        """
        return db.execute(delete_location_sql,[current_tile_id,username])
    else:
        update_location_sql="""
        UPDATE location
        SET tile=?
        WHERE tile=? AND player=(SELECT id 
        FROM users
        WHERE username=?)
        """
        return db.execute(update_location_sql,[target_tile_id,current_tile_id,username])
    
    

def create_combat_encounter(npc_id,username):
    sql="""
    INSERT INTO combat_log (player_id,npc_id,combat_action)
    VALUES ((SELECT id 
        FROM users
        WHERE username=?),?,"Combat encounter has started, select you next action")
    """
    result=db.execute(sql,[username,npc_id])
    if result["error"]:
        print(result["error"])


def check_npc_is_alive(npc_id):
    sql="""
    SELECT alive
    FROM npcs
    WHERE id=?
    """
    result=db.query(sql,[npc_id])
    if result and result[0]["alive"]:
        return True
    else:
        return False
    
def check_npc_location(npc_id,username):
    sql="""
    SELECT npcs.tile=(SELECT location.tile
    FROM location
    WHERE player=(SELECT id 
        FROM users
        WHERE username=?)) AS same_tile
    FROM npcs
    WHERE npcs.id=?
    """
    result=db.query(sql,[username,npc_id])
    if result and result[0]["same_tile"]:
        return True
    else:
        return False
    
def get_npc_items(npc_id):
    sql="""
    SELECT items.id,items.npc,items.item_name,item_subcategories.subcategory_name AS type,item_details.trader_price,item_slots.slot_name AS slot, item_details.rarity AS rarity,item_details.item_level,stat_sheet.agility,stat_sheet.stamina,stat_sheet.strength,stat_sheet.magic,stat_sheet.armor,weapon_details.min_damage,weapon_details.max_damage,weapon_details.weapon_speed,(SELECT style FROM damage_styles WHERE id=weapon_details.damage_style) AS damage_style,(SELECT style FROM damage_styles WHERE id=weapon_details.secondary_style) AS secondary_style
    FROM equipped_items 
    LEFT JOIN items ON equipped_items.item_id=items.id
    LEFT JOIN item_details ON item_details.item_id=items.id
    LEFT JOIN weapon_details ON weapon_details.item_id=items.id
    LEFT JOIN stat_sheet ON stat_sheet.item_id=items.id
    LEFT JOIN item_slots ON item_details.slot=item_slots.id
    LEFT JOIN item_subcategories ON item_details.item_type=item_subcategories.id
    WHERE equipped_items.npc_id=?
    """
    items=db.query(sql,[npc_id])
    return items

def get_npc_stats(npc_id):
    sql_get_player_stat_sheet="""
    SELECT agility,stamina,strength,magic
    FROM stat_sheet
    WHERE npc_id=?
    """
    player_stats=db.query(sql_get_player_stat_sheet,[npc_id])[0]
    sql_item_stats="""
    SELECT IFNULL(SUM(stat_sheet.agility),0) AS agility,
    IFNULL(SUM(stat_sheet.stamina),0) AS stamina,
    IFNULL(SUM(stat_sheet.strength),0) AS strength,
    IFNULL(SUM(stat_sheet.magic),0) AS magic,
    IFNULL(SUM(stat_sheet.armor),0) AS armor
    FROM equipped_items
    LEFT JOIN stat_sheet ON equipped_items.item_id=stat_sheet.item_id
    WHERE equipped_items.npc_id=?
    AND stat_sheet.id IS NOT NULL
    """
    item_stats=db.query(sql_item_stats,[npc_id])
    sql_heavy_items="""
    SELECT COUNT(equipped_items.item_id) AS item_count
    FROM equipped_items
    LEFT JOIN item_details ON equipped_items.item_id=item_details.item_id
    WHERE equipped_items.npc_id=?
    AND item_type IN (SELECT id
    FROM item_subcategories
    WHERE subcategory_name IN ("Metal Armor","Mace","Axe"))
    """
    heavy_items=db.query(sql_heavy_items,[npc_id])
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
    

def combat_attack_sequence(attack,username):
    sql_player_get_combat_log="""
    SELECT npc_id,player_id,player_swing_timer,npc_swing_timer
    FROM combat_log
    WHERE player_id=(SELECT id 
        FROM users
        WHERE username=?)
    ORDER BY id
    """
    combat_log=db.query(sql_player_get_combat_log,[username])[-1]
    result=combat.calculate_attacks(combat_log,attack,username)
    return result


def combat_use_items(item_id,username):
    player.use_item(item_id,username)
    sql_player_get_combat_log="""
    SELECT npc_id,player_id,player_swing_timer,npc_swing_timer
    FROM combat_log
    WHERE player_id=(SELECT id 
        FROM users
        WHERE username=?)
    ORDER BY id
    """
    combat_log=db.query(sql_player_get_combat_log,[username])[-1]
    result=combat.calculate_attacks(combat_log,"",username)
    return result