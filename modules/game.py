import sqlite3
import modules.db as db

def tile_details(coordinates):
    x=coordinates[0]
    y=coordinates[1]
    sql_npc="SELECT * FROM npcs WHERE x_coordinate=? AND y_coordinate=?"
    sql_container="SELECT * FROM containers WHERE x_coordinate=? AND y_coordinate=?"
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
    sql="SELECT * FROM items WHERE player=(SELECT id FROM users WHERE username=?)"
    print(username)
    items=db.query(sql,[username])
    print(items)
    return items

def get_container_items(container_id):
    sql="SELECT * FROM items WHERE container=?"
    items=db.query(sql,[container_id])
    return items

def take_item(item_id,player):
    sql="UPDATE items SET player=(SELECT id FROM users WHERE username=?), item_owner=NULL,container=NULL  WHERE id=?"
    db.execute(sql,[player,item_id])

def drop_item(item_id,player):
    sql="DELETE FROM items WHERE player=(SELECT id FROM users WHERE username=?) AND id=?"
    result=db.execute(sql,[player,item_id])
    if result=="success":
        return "Item dropped"
