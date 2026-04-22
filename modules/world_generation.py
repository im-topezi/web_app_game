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
        self.save_world_to_database()
        print(self.player)


    def save_world_to_database(self):
        sql="""
        INSERT INTO worlds (id,player,difficulty,world_name)
        VALUES (?,(SELECT id FROM users WHERE username=?),?,?)
        """
        db.execute(sql,[self.world_id,self.player,self.difficulty,self.name])

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
            
            if x==0 and y==0 and not self.tile_coordinates:

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
        self.id=""
        self.world=world
        self.x_coordinate=x
        self.y_coordinate=y
        self.type=type
        self.npcs=[]
        self.containers=[]
        self.save_tile_to_database()
        self.generate_npcs()
        self.generate_containers()


    def save_tile_to_database(self):
        sql="""
        INSERT INTO tiles (world_id,x_coordinate,y_coordinate,tile_type)
        VALUES (?,?,?,?)
        RETURNING id
        """
        result=db.execute(sql,[self.world.world_id,self.x_coordinate,self.y_coordinate,self.type])
        print(result)
        self.id=result["rows"][0][0]["id"]

    def generate_npcs(self):
        for i in range(random.randint(0,3)):
            self.npcs.append(NPC(self.id,self.type))

    def generate_containers(self):
        if self.type=="Village":
            container_type="barrel"
        else:
            container_type="chest"

        if container_type=="barrel":
            for i in range(random.randint(0,1)):
                new_container=Container(self.id,container_type)
                new_container.add_items_to_container(self.world.difficulty)
                self.containers.append(new_container)
        else:
            if (random.randint(1,100))>=90:
                new_container=Container(self.id,container_type)
                #new_container.add_items_to_container(self.world.difficulty)
                self.containers.append(new_container)

class Path:
    def __init__(self,first_tile,second_tile):
        self.first_tile=first_tile
        self.second_tile=second_tile
        self.save_path_to_database()


    def save_path_to_database(self):
        sql="""
        INSERT INTO paths (first_tile,second_tile)
        VALUES ((SELECT id FROM tiles WHERE x_coordinate=? AND y_coordinate=? AND world_id=?),(SELECT id FROM tiles WHERE x_coordinate=? AND y_coordinate=? AND world_id=?))
        """
        db.execute(sql,[self.first_tile.x_coordinate,self.first_tile.y_coordinate,self.first_tile.world.world_id,self.second_tile.x_coordinate,self.second_tile.y_coordinate,self.second_tile.world.world_id])
        print(sql)

    def __str__(self):
        return f"Goes from {self.first_tile.x_coordinate},{self.first_tile.y_coordinate} to {self.second_tile.x_coordinate},{self.second_tile.y_coordinate}"


class NPC:
    def __init__(self,tile_id,biome):
        self.id=""
        self.tile=tile_id
        self.name="Test NPC"
        self.type=self.generate_npc_type(biome)
        self.save_npc_to_database()
        Item(16,0).generate_a_random_armor("Head")


    def generate_npc_type(self,biome):
        sql="""
        SELECT id,npc_type
        FROM npc_types
        WHERE biome=?
        """
        types=db.query(sql,[biome])
        return random.choice(types)
    
    def save_npc_to_database(self):
        sql="""
        INSERT INTO npcs (npc_name,tile,npc_type_id)
        VALUES (?,?,?)
        RETURNING id
        """
        result=db.execute(sql,[self.name,self.tile,self.type["id"]])
        print(result)
        self.id=result["rows"][0][0]["id"]

class Container:
    def __init__(self,tile_id,type):
        self.id=""
        self.tile=tile_id
        self.type=type
        self.save_container_to_database()

    
    def save_container_to_database(self):
        sql="""
        INSERT INTO containers (tile,container_type)
        VALUES (?,?)
        RETURNING id
        """
        result=db.execute(sql,[self.tile,self.type])
        print(result)
        self.id=result["rows"][0][0]["id"]
    def add_items_to_container(self,difficulty):
        if self.type=="barrel":
            new_item=Item(difficulty,{"location":"container","id":self.id})
            new_range=random.choice([1,1,1,1,1,1,1,1,2])
            for i in range(new_range):
                new_item.generate_a_potion()

class Item:
    def __init__(self,level,location):
        self.id=""
        self.level=level
        self.price=0
        self.location=location
        self.name=""
        self.type=""
        self.stats={
            "agility":0,
            "magic":0,
            "stamina":0,
            "strength":0,
            "armor":0
        }
        self.damage=0
        self.speed=0
        self.slot=""

    def update_location(self):
        if self.location["location"]=="npc":
            sql_update_location="""
            UPDATE items
            SET npc=?
            WHERE id=?
            """
            db.execute(sql_update_location,[self.location["id"],self.id])
        elif self.location["location"]=="container":
            sql_update_location="""
            UPDATE items
            SET container=?
            WHERE id=?
            """
            db.execute(sql_update_location,[self.location["id"],self.id])
        elif self.location["location"]=="player":
            sql_update_location="""
            UPDATE items
            SET player=?
            WHERE id=?
            """
            db.execute(sql_update_location,[self.location["id"],self.id])
        
    def generate_a_random_item(self):
        sql_get_categories="""
        SELECT category_name FROM item_categories
        """
        categories=db.query(sql_get_categories)
        item_category=random.choice(categories)["category_name"]


    def generate_a_random_weapon(self):
        sql_get_categories="""
        SELECT category_name FROM item_categories
        """
        categories=db.query(sql_get_categories)
        item_category=random.choice(categories)["category_name"]

    def generate_a_random_armor(self,slot):
        sql_get_categories="""
        SELECT subcategory_name,item_material
        FROM item_subcategories
        WHERE category_id=(SELECT id
        FROM item_categories
        WHERE category_name="Armor")
        """
        categories=db.query(sql_get_categories)
        armor_category=random.choice(categories)
        print(armor_category["item_material"])

        sql_get_conditions="""
        SELECT condition_name,modifier
        FROM item_conditions
        WHERE material=?
        """
        conditions=db.query(sql_get_conditions,[armor_category["item_material"]])
        condition=random.choice(conditions)

        sql_get_armor_name="""
        SELECT armor_name
        FROM armor_names
        WHERE item_type=? AND slot=?
        """
        armor_names=db.query(sql_get_armor_name,[armor_category["subcategory_name"],slot])
        armor_name=random.choice(armor_names)["armor_name"]

        print(condition["condition_name"]+" "+armor_name)




    def generate_a_potion(self):
        self.name="Health Potion"
        random_range=float("1."+str(random.randint(1,6)))
        self.price=(int(self.level)*random_range)//1
        sql_create_item="""
        INSERT INTO items (item_name)
        VALUES ("Health Potion")
        RETURNING id
        """
        result=db.execute(sql_create_item)
        self.id=result["rows"][0][0]["id"]
        sql_create_item_details="""
        INSERT INTO item_details (item_id,item_type,trader_price,item_level)
        VALUES (?,(SELECT id
          FROM item_subcategories WHERE subcategory_name="Health Potion")
          ,?,?)
        """
        result2=db.execute(sql_create_item_details,[self.id,self.price,self.level])
        print(result2)
        self.update_location()
