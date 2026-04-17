import sqlite3
import modules.db as db

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
    tile["npcs"]=db.query(sql_npc,[tile_id])
    tile["containers"]=db.query(sql_container,[tile_id])

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
    WHERE username=?), item_owner=NULL,container=NULL  
    WHERE id=?
    """
    result=db.execute(sql,[player,item_id])
    return result["rows_affected"]



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