import modules.db as db
import random,secrets,sqlite3

class World:
    def __init__(self,difficulty,player,name):
        self.world_id=secrets.token_hex(8)
        self.tiles=[]
        self.tile_coordinates=set()
        self.difficulty=difficulty
        self.player=player
        self.name=name
        self.paths=[]

    def get_tile_types(self):
        sql="""
        SELECT * 
        FROM tile_types 
        WHERE difficulty<=?
        """
        result=db.query(sql,[self.difficulty])
        return result
    
    def choose_direction(self,x,y):
        coorninates=["x","y"]
        heading=[1,-1]
        direction=(random.choice(coorninates),random.choice(heading))
        if direction[0]=="x":
            x+=direction[1]
        else:
            y+=direction[1]
        return x,y
    
    
    def generate_world(self):
        tile_types=self.get_tile_types()
        tile_amounts={}
        for tile_type in tile_types:
            tile_amounts[tile_type["type_name"]]=0
        for i in range(self.difficulty):
            random_type=random.choice(tile_types)
            tile_amounts[random_type["type_name"]]+=1
        x=0
        y=0
        previous_tile=None
        previous_coordinate=tuple()
        while tile_amounts:
            
            if x==0 and y==0:
                new_tile=Tile(self,x,y,"Village")
                self.tile_coordinates.add((x,y))
                self.tiles.append(new_tile)
                previous_coordinate=(x,y)
                x,y=self.choose_direction(x,y)
                previous_tile=new_tile
            for tile_type in tile_amounts:
                
                if tile_amounts[tile_type]==0:
                    tile_amounts.pop(tile_type)
                    break
                if tile_amounts[tile_type]>1:
                    for i in range(random.randint(2,tile_amounts[tile_type])):
                        if (x,y) in self.tile_coordinates:
                            previous_coordinate=(x,y)
                            x,y=self.choose_direction(x,y)
                            break
                        else:
                            print(tile_amounts,tile_type)
                            new_tile=Tile(self,x,y,tile_type)
                            self.tile_coordinates.add((x,y))
                            self.tiles.append(new_tile)
                            if previous_coordinate != (previous_tile.x_coordinate,previous_tile.y_coordinate):
                                for tile in self.tiles:
                                    if (tile.x_coordinate,tile.y_coordinate)==previous_coordinate:
                                        previous_tile=tile
                            self.paths.append(Path(previous_tile,new_tile))
                            previous_coordinate=(x,y)
                            x,y=self.choose_direction(x,y)
                            previous_tile=new_tile
                            tile_amounts[tile_type]-=1
                else:
                    if (x,y) in self.tile_coordinates:
                        previous_coordinate=(x,y)
                        x,y=self.choose_direction(x,y)
                    else:
                        print(tile_amounts,tile_type)
                        new_tile=Tile(self,x,y,tile_type)
                        self.tile_coordinates.add((x,y))
                        self.tiles.append(new_tile)
                        if previous_coordinate != (previous_tile.x_coordinate,previous_tile.y_coordinate):
                            for tile in self.tiles:
                                if (tile.x_coordinate,tile.y_coordinate)==previous_coordinate:
                                    previous_tile=tile
                        self.paths.append(Path(previous_tile,new_tile))
                        previous_coordinate=(x,y)
                        x,y=self.choose_direction(x,y)
                        previous_tile=new_tile
                        tile_amounts[tile_type]-=1
        for path in self.paths:
            print(path)
        return(len(self.tiles),len(self.paths))

                            




class Tile:
    def __init__(self,world,x,y,type):
        self.world=world
        self.x_coordinate=x
        self.y_coordinate=y
        self.type=type
        self.npcs=[]
        self.containers=[]


class Path:
    def __init__(self,first_tile,second_tile):
        self.first_tile=first_tile
        self.second_tile=second_tile
    def __str__(self):
        return f"Goes from {self.first_tile.x_coordinate},{self.first_tile.y_coordinate} to {self.second_tile.x_coordinate},{self.second_tile.y_coordinate}"


class NPC:
    def __init__(self):
        pass

class Container:
    def __init__(self):
        pass

class Item:
    def __init__(self):
        pass

    