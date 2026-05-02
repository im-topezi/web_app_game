import sqlite3,random
import modules.db as db
import modules.player as player
import modules.game as game

def calculate_attacks(combat_log,attack,username):
    player_items=player.get_equipped_items(username)
    player_stats=player.get_total_stats(username)
    npc_items=game.get_npc_items(combat_log["npc_id"])
    npc_stats=game.get_npc_stats(combat_log["npc_id"])
    player_weapon=None
    npc_weapon=None
    player_damage=0
    npc_damage=0
    npc_armor_types={
        "leather":0,
        "cloth":0,
        "metal":0
    }
    player_armor_types={
        "leather":0,
        "cloth":0,
        "metal":0
    }
    for item in player_items:
        if item["slot"]=="Weapon":
            player_weapon=item
        else:
            match item["type"]:
                case "Leather Armor":
                    player_armor_types["leather"]+=1
                case "Cloth Armor":
                    player_armor_types["cloth"]+=1
                case "Metal Armor":
                    player_armor_types["metal"]+=1
    for item in npc_items:
        if item["slot"]=="Weapon":
            npc_weapon=item
            if npc_weapon["secondary_style"]:
                npc_attack=random.choice((npc_weapon["damage_style"],npc_weapon["secondary_style"]))
            else:
                npc_attack=npc_weapon["damage_style"]
            
        else:
            match item["type"]:
                case "Leather Armor":
                    npc_armor_types["leather"]+=1
                case "Cloth Armor":
                    npc_armor_types["cloth"]+=1
                case "Metal Armor":
                    npc_armor_types["metal"]+=1
    if attack=="Punch":
        player_weapon=None
        attack="Crush"
    if player_weapon:
        player_speed=round(player_weapon["weapon_speed"]*player_stats["speed_modifier"],2)
    else:
        player_speed=round(1*player_stats["speed_modifier"],2)
    player_tick_time=3+combat_log["player_swing_timer"]
    npc_tick_time=3+combat_log["npc_swing_timer"]


    if attack:
        for i in range(int(player_tick_time//player_speed)):
            if attack in ("Slash","Crush","Stab"):
                hit_chance=player_stats["agility"]+5
                dodge_chance=npc_stats["agility"]+5
                rolls=hit_chance+dodge_chance
                roll=random.randint(1,rolls)
                if roll<=hit_chance:
                    if player_weapon:
                        damage=int(((random.randint(player_weapon["min_damage"],player_weapon["max_damage"]))*player_stats["physical_modifier"])//1)
                        if attack==player_weapon["secondary_style"]:
                            damage=damage*0.7
                    else:
                        damage=player_stats["strength"]+1

                    armor_modifier=1
                    match attack:
                        case "Slash":
                            armor_modifier+=1+npc_armor_types["metal"]*0.1
                            armor_modifier+=1-npc_armor_types["cloth"]*0.1
                        case "Stab":
                            armor_modifier+=1+npc_armor_types["metal"]*0.1
                            armor_modifier+=1-npc_armor_types["leather"]*0.1
                        case "Crush":
                            armor_modifier+=1-npc_armor_types["metal"]*0.1
                    armor_absorption=1+npc_stats["armor"]*armor_modifier/1000
                    final_damage=int((damage/armor_absorption)//1)
                    print(f"Final damage: {final_damage}, damage: {damage}, armor abs: {armor_absorption}")
                    player_damage+=final_damage
                    sql_player_hit="""
                    INSERT INTO combat_log (player_id,npc_id,combat_action,damage,damage_style,attacker)
                    VALUES (?,?,"You hit",?,(SELECT id
                    FROM damage_styles
                    WHERE style=?),"player")
                    """
                    result=db.execute(sql_player_hit,[combat_log["player_id"],combat_log["npc_id"],final_damage,attack])
                    
                    
                else:
                    sql_player_miss="""
                    INSERT INTO combat_log (player_id,npc_id,combat_action,attacker)
                    VALUES (?,?,"Your attack misses","player")
                    """
                    db.execute(sql_player_miss,[combat_log["player_id"],combat_log["npc_id"]])
            else:
                hit_chance=player_stats["magic"]+5
                dodge_chance=npc_stats["agility"]+5
                rolls=hit_chance+dodge_chance
                roll=random.randint(1,rolls)
                if roll<=hit_chance:
                    damage=int(((random.randint(player_weapon["min_damage"],player_weapon["max_damage"]))*player_stats["magical_modifier"])//1)
                    if attack==player_weapon["secondary_style"]:
                        damage=damage*0.7
                    armor_modifier=1
                    match attack:
                        case "Fire":
                            armor_modifier+=1-npc_armor_types["metal"]*0.1
                        case "Frost":
                            armor_modifier+=1-npc_armor_types["cloth"]*0.1
                        case "Shock":
                            armor_modifier+=1+npc_armor_types["metal"]*0.1
                            armor_modifier+=1-npc_armor_types["leather"]*0.1
                    final_damage=int((damage/armor_modifier)//1)
                    player_damage+=final_damage
                    print(f"Final damage: {final_damage}, damage: {damage}")
                    sql_player_hit="""
                    INSERT INTO combat_log (player_id,npc_id,combat_action,damage,damage_style,attacker)
                    VALUES (?,?,"You hit",?,(SELECT id
                    FROM damage_styles
                    WHERE style=?),"player")
                    """
                    result=db.execute(sql_player_hit,[combat_log["player_id"],combat_log["npc_id"],final_damage,attack])
                    
                    
                else:
                    sql_player_miss="""
                    INSERT INTO combat_log (player_id,npc_id,combat_action,attacker)
                    VALUES (?,?,"Your attack misses","player")
                    """
                    db.execute(sql_player_miss,[combat_log["player_id"],combat_log["npc_id"]])
        sql_deal_damage_to_npc="""
        UPDATE npcs
        SET health=health-?
        WHERE id=?
        RETURNING health
        """
        result=db.execute(sql_deal_damage_to_npc,[player_damage,combat_log["npc_id"]])
        if result["rows"][0][0]["health"]<=0:
            sql_kill_npc="""
            UPDATE npcs
            SET alive=FALSE
            WHERE id=?
            """
            db.execute(sql_kill_npc,[combat_log["npc_id"]])
            return "Enemy defeated"
    
    if npc_weapon:
        npc_speed=round(npc_weapon["weapon_speed"]*npc_stats["speed_modifier"],2)
        
        
    else:
        sql_get_npc_type="""
        SELECT npc_types.npc_type
        FROM npcs
        LEFT JOIN npc_types ON npc_types.id=npcs.npc_type_id
        WHERE npcs.id=?
        """
        npc_type=db.query(sql_get_npc_type,[combat_log["npc_id"]])[0]["npc_type"]
        match npc_type:
            case "Human":
                npc_speed=1
                npc_attack="Crush"
            case "Bear":
                npc_speed=2
                npc_attack=random.choice(["Slash","Stab"])
            case "Alligator":
                npc_speed=3
                npc_attack=random.choice(["Stab","Crush"])
            case "Dragon":
                npc_speed=3
                npc_attack=random.choice(["Slash","Crush","Stab","Fire","Frost","Shock"])
            case "Skeleton":
                npc_speed=1.5
                npc_attack="Crush"
        
        
    for i in range(int(npc_tick_time//npc_speed)):
        if npc_attack in ("Slash","Crush","Stab"):
            
            hit_chance=npc_stats["agility"]+5
            dodge_chance=player_stats["agility"]+5
            rolls=hit_chance+dodge_chance
            roll=random.randint(1,rolls)
            if roll<=hit_chance:
                if npc_weapon:
                    damage=int(((random.randint(npc_weapon["min_damage"],npc_weapon["max_damage"]))*npc_stats["physical_modifier"])//1)
                    if npc_attack==npc_weapon["secondary_style"]:
                        damage=damage*0.7
                else:
                    damage=1+npc_stats["strength"]*3
                armor_modifier=1
                match npc_attack:
                    case "Slash":
                        armor_modifier+=1+player_armor_types["metal"]*0.1
                        armor_modifier+=1-player_armor_types["cloth"]*0.1
                    case "Stab":
                        armor_modifier+=1+player_armor_types["metal"]*0.1
                        armor_modifier+=1-player_armor_types["leather"]*0.1
                    case "Crush":
                        armor_modifier+=1-player_armor_types["metal"]*0.1
                armor_absorption=1+player_stats["armor"]*armor_modifier/1000
                final_damage=int((damage/armor_absorption)//1)
                npc_damage+=final_damage
                print(f"Final damage: {final_damage}, damage: {damage}, armor abs: {armor_absorption}")
                sql_npc_hit="""
                INSERT INTO combat_log (player_id,npc_id,combat_action,damage,damage_style,attacker)
                VALUES (?,?,"Enemy hits you",?,(SELECT id
                    FROM damage_styles
                    WHERE style=?),"npc")
                """
                db.execute(sql_npc_hit,[combat_log["player_id"],combat_log["npc_id"],final_damage,npc_attack])
                
            else:
                sql_npc_miss="""
                INSERT INTO combat_log (player_id,npc_id,combat_action,attacker)
                VALUES (?,?,"Enemys attack misses","npc")
                """
                db.execute(sql_npc_miss,[combat_log["player_id"],combat_log["npc_id"]])
        else:
            hit_chance=npc_stats["magic"]+5
            dodge_chance=player_stats["agility"]+5
            rolls=hit_chance+dodge_chance
            roll=random.randint(1,rolls)
            if roll<=hit_chance:
                if npc_weapon:
                    damage=int(((random.randint(npc_weapon["min_damage"],npc_weapon["max_damage"]))*npc_stats["magical_modifier"])//1)
                    if attack==npc_weapon["secondary_style"]:
                        damage=damage*0.7
                else:
                    damage=1+npc_stats["magic"]*2
                armor_modifier=1
                match attack:
                    case "Fire":
                        armor_modifier+=1-player_armor_types["metal"]*0.1
                    case "Frost":
                        armor_modifier+=1-player_armor_types["cloth"]*0.1
                    case "Shock":
                        armor_modifier+=1+player_armor_types["metal"]*0.1
                        armor_modifier+=1-player_armor_types["leather"]*0.1
                final_damage=int((damage/armor_modifier)//1)
                npc_damage+=final_damage
                print(f"Final damage: {final_damage}, damage: {damage}")
                sql_npc_hit="""
                INSERT INTO combat_log (player_id,npc_id,combat_action,damage,damage_style,attacker)
                VALUES (?,?,"Enemy hits you",?,(SELECT id
                    FROM damage_styles
                    WHERE style=?),"npc")
                """
                db.execute(sql_npc_hit,[combat_log["player_id"],combat_log["npc_id"],final_damage,npc_attack])
                
            else:
                sql_npc_miss="""
                INSERT INTO combat_log (player_id,npc_id,combat_action,attacker)
                VALUES (?,?,"Enemys attack misses","npc")
                """
                db.execute(sql_npc_miss,[combat_log["player_id"],combat_log["npc_id"]])
    sql_get_player_health="""
    SELECT health
    FROM users
    WHERE id=?
    """
    health=db.query(sql_get_player_health,[combat_log["player_id"]])[0]["health"]
    if npc_damage>=health:
        sql_deal_damage_to_player="""
        UPDATE users
        SET health=1
        WHERE id=?
        """
        result=db.execute(sql_deal_damage_to_player,[combat_log["player_id"]])
        return "You are greatly wounded"
    sql_deal_damage_to_player="""
    UPDATE users
    SET health=health-?
    WHERE id=?
    """
    
    result=db.execute(sql_deal_damage_to_player,[npc_damage,combat_log["player_id"]])

    player_swing_timer=player_tick_time%player_speed
    npc_swing_timer=npc_tick_time%npc_speed

    end_of_round_sql="""
    INSERT INTO combat_log(player_id,npc_id,combat_action,player_swing_timer,npc_swing_timer)
    VALUES (?,?,"Select your next action!",?,?)
    """
    db.execute(end_of_round_sql,[combat_log["player_id"],combat_log["npc_id"],player_swing_timer,npc_swing_timer])

    return "Combat continues"