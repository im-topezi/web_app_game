import sqlite3
import modules.db as db

def tile_details(world_id,player):



    sql_npc="""
    SELECT * 
    FROM npcs 
    WHERE x_coordinate=? 
    AND y_coordinate=?
    """
    sql_container="""
    SELECT * 
    FROM containers 
    WHERE x_coordinate=? 
    AND y_coordinate=?"""
    npcs=db.query(sql_npc,[x,y])
    containers=db.query(sql_container,[x,y])
    tile={
        "connected":{
            "north":True,
            "south":True,
            "east":True,
            "west":True
        },
        "objects":containers if containers else [],
        "npcs":npcs if npcs else []
    }
    return tile


def get_player_items(username):
    sql="""
    SELECT * 
    FROM items 
    WHERE player=(SELECT id 
    FROM users 
    WHERE username=?) 
    AND listed_for_sale!=TRUE
    """
    print(username)
    items=db.query(sql,[username])
    print(items)
    return items

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
    WHERE username=?), item_owner=NULL,container=NULL  
    WHERE id=?
    """
    result=db.execute(sql,[player,item_id])
    return result

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


def generate_container_placement():
    pass

def get_user_worlds(username):
    sql="""
    SELECT *
    FROM worlds
    WHERE player=(SELECT id
    FROM users WHERE username=?)
    """
    return db.query(sql,[username])

def visit_world(world_id):
    visit_sql="""
    UPDATE worlds
    SET visited=TRUE
    WHERE id=?
    """
    db.execute(visit_sql,[world_id])

    set_location_sql="""
    INSERT INTO location (player,tile)
    VALUES ((SELECT worlds.player,tiles.id 
    FROM tiles 
    LEFT JOIN worlds 
    ON tiles.world_id=worlds.id
    WHERE tiles.x_coordinate=0 AND tiles.y_coordinate=0 AND tiles.world_id=?))
    """
    db.execute(set_location_sql,[world_id])


def check_if_in_game(username):
    sql="""
    SELECT tile
    FROM locations
    WHERE player=(SELECT id 
    FROM users
    WHERE username=?)
    """
    return db.query(sql,[username])