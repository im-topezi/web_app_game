import modules.db as db
import modules.game as game
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
        self.generate_gear()
        self.generate_containers()

    def generate_gear(self):
        for npc in self.npcs:
            npc.generate_items(self.world.difficulty)
            npc.equip_items()
            npc.create_stat_sheet(self.world.difficulty)
            npc.set_max_health()

    def save_tile_to_database(self):
        sql="""
        INSERT INTO tiles (world_id,x_coordinate,y_coordinate,tile_type)
        VALUES (?,?,?,?)
        RETURNING id
        """
        result=db.execute(sql,[self.world.world_id,self.x_coordinate,self.y_coordinate,self.type])
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
                new_container.add_items_to_container(self.world.difficulty)
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

    def __str__(self):
        return f"Goes from {self.first_tile.x_coordinate},{self.first_tile.y_coordinate} to {self.second_tile.x_coordinate},{self.second_tile.y_coordinate}"


class NPC:
    def __init__(self,tile_id,biome):
        self.id=""
        self.tile=tile_id
        self.type=self.generate_npc_type(biome)
        self.name=self.type["npc_type"]
        self.save_npc_to_database()
        self.items=[]

    def create_stat_sheet(self,stat_amount):
        stats={
            "agility":0,
            "stamina":0,
            "strength":0,
            "magic":0,
            "armor":0
        }
        if self.type["npc_type"] in ("Bear","Alligator"):
            stats["armor"]=stat_amount*3
            for i in range(stat_amount):
                random_value=random.randint(1,100)
                if random_value>90:
                    stats["agility"]+=1
                elif random_value>45:
                    stats["strength"]+=1
                else:
                    stats["stamina"]+=1
        elif self.type["npc_type"]=="Dragon":
            stats["armor"]=stat_amount*10
            for i in range(stat_amount*2):
                random_value=random.randint(1,100)
                if random_value>90:
                    stats["agility"]+=1
                elif random_value>45:
                    stats["magic"]+=1
                    stats["strength"]+=1
                else:
                    stats["stamina"]+=1
        sql="""
        INSERT INTO stat_sheet (stamina,strength,agility,magic,armor,npc_id)
        VALUES (?,?,?,?,?,?)
        """
        db.execute(sql,[stats["stamina"],stats["strength"],stats["agility"],stats["magic"],stats["armor"],self.id])

    def set_max_health(self):
        stamina=game.get_npc_stats(self.id)["stamina"]
        health=100+stamina*10
        sql="""
        UPDATE npcs
        SET health=?,max_health=?
        WHERE id=?
        """
        db.execute(sql,[health,health,self.id])

    def generate_items(self,world_level):
        stats=world_level
        if self.type["npc_type"] in ("Human","Skeleton"):
            
            sql_get_slots="""
            SELECT slot_name
            FROM item_slots
            """
            slots=db.query(sql_get_slots)
            weapon_stats=random.randint(1,stats)
            stats-=weapon_stats
            weapon=Item(world_level,{"id":self.id,"location":"npc"})
            weapon.generate_a_random_weapon(weapon_stats)
            for slot in slots:
                if slot["slot_name"]=="Weapon":
                    slots.remove(slot)
            self.items.append(weapon)
            while stats>0 and slots:
                armor_stats=random.randint(1,stats)
                stats-=armor_stats
                slot=random.choice(slots)
                armor=Item(world_level,{"id":self.id,"location":"npc"})
                armor.generate_a_random_armor(slot["slot_name"],armor_stats)
                slots.remove(slot)
                self.items.append(armor)
            
    def equip_items(self):
        for item in self.items:
            sql="""
            INSERT INTO equipped_items (
            npc_id,item_id,slot)
            VALUES (?,?,(SELECT id
            FROM item_slots
            WHERE slot_name=?))
            """
            result=db.execute(sql,[self.id,item.id,item.slot])


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
        self.id=result["rows"][0][0]["id"]
    def add_items_to_container(self,difficulty):
        if self.type=="barrel":
            new_item=Item(difficulty,{"location":"container","id":self.id})
            new_range=random.choice([1,1,1,1,1,1,1,1,2])
            for i in range(new_range):
                new_item.generate_a_potion()
        if self.type=="chest":
            new_item=Item(difficulty,{"location":"container","id":self.id})
            new_range=random.choice([1,1,1,1,1,1,1,1,2])
            for i in range(new_range):
                new_item.generate_a_random_item()

class Item:
    def __init__(self,level,location):
        self.id=""
        self.level=level
        self.price=0
        self.location=location
        self.name=""
        self.type=""
        self.subtype=""
        self.rarity=""
        self.stats={
            "agility":0,
            "magic":0,
            "stamina":0,
            "strength":0,
            "armor":0
        }
        self.damage=tuple()
        self.speed=0
        self.slot=""

    def add_item_to_database(self):
        sql_create_item="""
        INSERT INTO items (item_name)
        VALUES (?)
        RETURNING id
        """
        result=db.execute(sql_create_item,[self.name])
        self.id=result["rows"][0][0]["id"]
        

        sql_create_item_details="""
        INSERT INTO item_details (item_id,item_type,trader_price,item_level,slot,rarity)
        VALUES (?,(SELECT id
          FROM item_subcategories WHERE subcategory_name=?)
          ,?,?,(SELECT id
          FROM item_slots WHERE slot_name=?),?)
        """

        details=db.execute(sql_create_item_details,[self.id,self.subtype,self.price,self.level,self.slot,self.rarity])
        

        sql_create_stat_sheet="""
        INSERT INTO stat_sheet (stamina,strength,agility,magic,armor,item_id)
        VALUES (?,?,?,?,?,?)
        """
        db.execute(sql_create_stat_sheet,[self.stats["stamina"],self.stats["strength"],self.stats["agility"],self.stats["magic"],self.stats["armor"],self.id])

        if self.type=="Weapon":
            weapon_details_parameters=[self.id,self.damage[0],self.damage[1],self.speed]
            magic_styles_sql="""
            SELECT damage_styles.id,style
            FROM damage_styles
            LEFT JOIN damage_types 
            ON damage_types.id=damage_styles.type_id
            WHERE damage_type="Magic"
            """
            magic_styles=db.query(magic_styles_sql)
            weapon_details_sql="""
            INSERT INTO weapon_details (item_id,min_damage,max_damage,weapon_speed,damage_style,secondary_style)
            VALUES (?,?,?,?,?,?)
            """
            if self.subtype=="Staff":
                weapon_details_parameters.append(random.choice(magic_styles)["id"])
                crush_sql="SELECT id FROM damage_styles WHERE style='Crush'"

                weapon_details_parameters.append(db.query(crush_sql)[0]["id"])
            elif self.subtype=="Wand":
                weapon_details_parameters.append(random.choice(magic_styles)["id"])
                weapon_details_parameters.append(None)
            elif self.subtype=="Mace":
                crush_sql="SELECT id FROM damage_styles WHERE style='Crush'"
                weapon_details_parameters.append(db.query(crush_sql)[0]["id"])
                weapon_details_parameters.append(None)
            elif self.subtype=="Axe":
                slash_sql="SELECT id FROM damage_styles WHERE style='Slash'"
                weapon_details_parameters.append(db.query(slash_sql)[0]["id"])
                crush_sql="SELECT id FROM damage_styles WHERE style='Crush'"
                weapon_details_parameters.append(db.query(crush_sql)[0]["id"])
            elif self.subtype=="Sword":
                slash_sql="SELECT id FROM damage_styles WHERE style='Slash'"
                weapon_details_parameters.append(db.query(slash_sql)[0]["id"])
                stab_sql="SELECT id FROM damage_styles WHERE style='Stab'"
                weapon_details_parameters.append(db.query(stab_sql)[0]["id"])
            elif self.subtype=="Dagger":
                stab_sql="SELECT id FROM damage_styles WHERE style='Stab'"
                weapon_details_parameters.append(db.query(stab_sql)[0]["id"])
                slash_sql="SELECT id FROM damage_styles WHERE style='Slash'"
                weapon_details_parameters.append(db.query(slash_sql)[0]["id"])

            result=db.execute(weapon_details_sql,weapon_details_parameters)

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

    def define_rarity(self,modifier,level,stats):
        stat_value=stats/level
        if stat_value>0.90 and modifier>=1:
            self.rarity="Legendary"
        elif stat_value>0.80 and modifier>=0.8:
            self.rarity="Epic"
        elif stat_value>0.60 and modifier>=0.7:
            self.rarity="Rare"
        elif stat_value>0.45 and modifier>=0.5:
            self.rarity="Uncommon"
        else:
            self.rarity="Common"

        
    def generate_a_random_item(self):
            sql_get_slots="""
            SELECT slot_name
            FROM item_slots
            """
            slots=db.query(sql_get_slots)
            slot=random.choice(slots)
            if slot["slot_name"]=="Weapon":
                self.generate_a_random_weapon(self.level)
            else:
                self.generate_a_random_armor(slot["slot_name"],self.level)
        


    def generate_a_random_weapon(self,stats):
        def define_damage_value(condition_modifier,item_level,weapon_type):
            get_weapon_speed_sql="""
            SELECT speed
            FROM weapon_speeds
            WHERE weapon_type=?
            """
            speed=db.query(get_weapon_speed_sql,[weapon_type])[0]["speed"]
            base_dmg=speed*item_level//1+1
            max_dmg=base_dmg+(base_dmg*condition_modifier)//1+2
            return (speed,base_dmg,max_dmg)
        
        def allocate_stats(weapon_type,stat_amount):
            print(weapon_type)

            if weapon_type in ("Dagger","Sword"):
                stats={
                    "agility":0,
                    "stamina":0,
                    "strength":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["strength"]+=1
                    elif random_value>45:
                        stats["agility"]+=1
                    else:
                        stats["stamina"]+=1
            elif weapon_type in ("Wand","Staff"):
                stats={
                    "agility":0,
                    "stamina":0,
                    "magic":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["agility"]+=1
                    elif random_value>45:
                        stats["magic"]+=1
                    else:
                        stats["stamina"]+=1
            else:
                stats={
                    "agility":0,
                    "stamina":0,
                    "strength":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["agility"]+=1
                    elif random_value>45:
                        stats["strength"]+=1
                    else:
                        stats["stamina"]+=1
            return stats

        
        sql_get_categories="""
        SELECT subcategory_name,item_material
        FROM item_subcategories
        WHERE category_id=(SELECT id
        FROM item_categories
        WHERE category_name="Weapon")
        """
        categories=db.query(sql_get_categories)
        weapon_category=random.choice(categories)

        sql_get_conditions="""
        SELECT condition_name,modifier
        FROM item_conditions
        WHERE material=?
        """
        conditions=db.query(sql_get_conditions,[weapon_category["item_material"]])
        condition=random.choice(conditions)

        damage=define_damage_value(condition["modifier"],self.level,weapon_category["subcategory_name"])
        self.speed=damage[0]
        self.damage=(damage[1],damage[2])
        self.name=condition["condition_name"]+" "+weapon_category["subcategory_name"]
        allocated_stats=allocate_stats(weapon_category["subcategory_name"],stats)
        for stat in allocated_stats:
            self.stats[stat]=allocated_stats[stat]
        self.type="Weapon"
        self.slot="Weapon"
        self.define_rarity(condition["modifier"],self.level,stats)
        self.subtype=weapon_category["subcategory_name"]
        self.add_item_to_database()
        self.update_location()

    def generate_a_random_armor(self,slot,stats):

        def define_armor_value(condition_modifier,slot,item_level,armor_type):
            get_armor_multiplier_sql="""
            SELECT multiplier
            FROM armor_multipliers
            WHERE armor_slot=?
            """
            multiplier=db.query(get_armor_multiplier_sql,[slot])[0]["multiplier"]
            armor_values={"Metal Armor":1,
             "Leather Armor":0.5,
             "Cloth Armor": 0.2}
            armor=item_level*multiplier*condition_modifier*armor_values[armor_type]//1
            return int(armor)
        
        def allocate_stats(armor_type,stat_amount):
            if armor_type=="Metal Armor":
                stats={
                    "agility":0,
                    "stamina":0,
                    "strength":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["agility"]+=1
                    elif random_value>45:
                        stats["strength"]+=1
                    else:
                        stats["stamina"]+=1
            if armor_type=="Leather Armor":
                stats={
                    "agility":0,
                    "stamina":0,
                    "strength":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["strength"]+=1
                    elif random_value>45:
                        stats["agility"]+=1
                    else:
                        stats["stamina"]+=1
            if armor_type=="Cloth Armor":
                stats={
                    "agility":0,
                    "stamina":0,
                    "magic":0
                }
                for i in range(stat_amount):
                    random_value=random.randint(1,100)
                    if random_value>90:
                        stats["agility"]+=1
                    elif random_value>45:
                        stats["magic"]+=1
                    else:
                        stats["stamina"]+=1
            return stats

        
        sql_get_categories="""
        SELECT subcategory_name,item_material
        FROM item_subcategories
        WHERE category_id=(SELECT id
        FROM item_categories
        WHERE category_name="Armor")
        """
        categories=db.query(sql_get_categories)
        armor_category=random.choice(categories)

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
        armor=define_armor_value(condition["modifier"],slot,self.level,armor_category["subcategory_name"])
        self.name=condition["condition_name"]+" "+armor_name
        allocated_stats=allocate_stats(armor_category["subcategory_name"],stats)
        for stat in allocated_stats:
            self.stats[stat]=allocated_stats[stat]
        self.stats["armor"]=armor
        self.slot=slot
        self.type="Armor"
        self.define_rarity(condition["modifier"],self.level,stats)
        self.subtype=armor_category["subcategory_name"]
        self.add_item_to_database()
        self.update_location()
        
        




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
        INSERT INTO item_details (item_id,item_type,trader_price,item_level,rarity)
        VALUES (?,(SELECT id
          FROM item_subcategories WHERE subcategory_name="Health Potion")
          ,?,?,"Common")
        """
        result2=db.execute(sql_create_item_details,[self.id,self.price,self.level])
        self.update_location()
