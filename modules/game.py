import sqlite3
import modules.db as db

def tile_details(x,y):
    #sql that gets the tile details from db
    tile={
        "connected":{
            "north":True,
            "south":False,
            "east":False,
            "west":True
        },
        "objects":[
            "barrel2"
        ],
        "npcs":[
            "selma"
        ]
    }
    return tile