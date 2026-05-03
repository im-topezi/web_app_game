CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
set_stats BOOLEAN DEFAULT FALSE,
health INTEGER DEFAULT 100,
max_health INTEGER DEFAULT 100,
gold INTEGER DEFAULT 0 NOT NULL,
CHECK (gold >= 0),
CHECK (health >= 0 AND health<=max_health));


CREATE TABLE worlds (
id TEXT UNIQUE,
player INTEGER,
difficulty INTEGER,
world_name TEXT,
visited BOOLEAN DEFAULT FALSE,
FOREIGN KEY (player) REFERENCES users(id)
);

CREATE TABLE tile_types(
type_name TEXT UNIQUE,
difficulty INTEGER
);

CREATE TABLE npc_types (
    id INTEGER PRIMARY KEY,
    npc_type TEXT,
    biome TEXT,
    FOREIGN KEY (biome) REFERENCES tile_types(type_name)
);


CREATE TABLE tiles (
id INTEGER PRIMARY KEY,
world_id TEXT,
x_coordinate INTEGER,
y_coordinate INTEGER,
tile_type TEXT,
FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
FOREIGN KEY (tile_type) REFERENCES tile_types(type_name)
UNIQUE (world_id,x_coordinate,y_coordinate)
);

CREATE TABLE damage_types (
    id INTEGER PRIMARY KEY,
    damage_type TEXT
);

CREATE TABLE damage_styles (
    id INTEGER PRIMARY KEY,
    type_id INTEGER,
    style TEXT,
    FOREIGN KEY (type_id) REFERENCES damage_types(id)
);

CREATE TABLE paths (
id INTEGER PRIMARY KEY,
first_tile INTEGER,
second_tile INTEGER,
FOREIGN KEY (first_tile) REFERENCES tiles(id) ON DELETE CASCADE,
FOREIGN KEY (second_tile) REFERENCES tiles(id) ON DELETE CASCADE
);

CREATE TABLE npcs (
id INTEGER PRIMARY KEY,
npc_name TEXT,
tile INTEGER,
npc_type_id INTEGER,
health INTEGER DEFAULT 100,
max_health INTEGER DEFAULT 100,
alive BOOLEAN DEFAULT TRUE,
gold INTEGER DEFAULT 0 NOT NULL,
FOREIGN KEY (tile) REFERENCES tiles(id) ON DELETE CASCADE,
FOREIGN KEY (npc_type_id) REFERENCES npc_types(id),
CHECK (gold >= 0)
);

CREATE TABLE containers (
id INTEGER PRIMARY KEY,
container_type TEXT,
gold INTEGER DEFAULT 0 NOT NULL,
tile INTEGER,
FOREIGN KEY (tile) REFERENCES tiles(id) ON DELETE CASCADE,
CHECK (gold >= 0)
);

CREATE TABLE item_categories (
    id INTEGER PRIMARY KEY,
    category_name TEXT
);


CREATE TABLE item_subcategories (
id INTEGER PRIMARY KEY,
category_id INTEGER,
subcategory_name TEXT UNIQUE,
item_material TEXT,
FOREIGN KEY (category_id) REFERENCES item_categories(id)
);

CREATE TABLE item_slots (
id INTEGER PRIMARY KEY,
slot_name TEXT UNIQUE
);

CREATE TABLE items (
id INTEGER PRIMARY KEY,
item_name TEXT,
npc INTEGER,
player INTEGER,
container INTEGER,
FOREIGN KEY (npc) REFERENCES npcs(id) ON DELETE CASCADE,
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (container) REFERENCES containers(id) ON DELETE CASCADE,
CHECK (
    player IS NULL
    OR player IS NOT NULL AND (npc IS NULL AND container IS NULL)
),
CHECK (
    npc IS NULL
    OR npc IS NOT NULL AND (player IS NULL AND container IS NULL)
),
CHECK (
    container IS NULL
    OR container IS NOT NULL AND (player IS NULL AND npc IS NULL)
)
);


CREATE TABLE trade_offers (
id INTEGER PRIMARY KEY,
sold_item INTEGER NOT NULL,
buyer_id INTEGER NOT NULL,
gold_offer INTEGER,
FOREIGN KEY (sold_item) REFERENCES items(id) ON DELETE CASCADE,
FOREIGN KEY (buyer_id) REFERENCES users(id)
);

CREATE TABLE offered_items (
id INTEGER PRIMARY KEY,
offer_id INTEGER NOT NULL,
item_id INTEGER NOT NULL UNIQUE,
FOREIGN KEY (item_id) REFERENCES items(id),
FOREIGN KEY (offer_id) REFERENCES trade_offers(id) ON DELETE CASCADE
);

CREATE TABLE marketplace_categories(
    id INTEGER PRIMARY KEY,
    category TEXT
);

CREATE TABLE marketplace_listings (
id INTEGER PRIMARY KEY,
item_id INTEGER NOT NULL,
seller_id INTEGER NOT NULL,
marketplace_price INTEGER,
marketplace_category INTEGER,
FOREIGN KEY (marketplace_category) REFERENCES marketplace_categories(id),
FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
FOREIGN KEY (seller_id) REFERENCES users(id)
);


CREATE TABLE location (
player INTEGER UNIQUE NOT NULL,
tile INTEGER,
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (tile) REFERENCES tiles(id)
);

CREATE TABLE stat_sheet (
id INTEGER PRIMARY KEY,
stamina INTEGER DEFAULT 0,
strength INTEGER DEFAULT 0,
agility INTEGER DEFAULT 0,
magic INTEGER DEFAULT 0,
armor INTEGER DEFAULT 0,
player_id INTEGER UNIQUE,
npc_id INTEGER UNIQUE,
item_id INTEGER UNIQUE,
FOREIGN KEY (player_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,

CHECK (
    player_id IS NULL
    OR player_id IS NOT NULL AND (npc_id IS NULL AND item_id IS NULL) AND ((stamina+strength+agility+magic)<16 AND (armor=0))
),
CHECK (
    npc_id IS NULL
    OR npc_id IS NOT NULL AND (player_id IS NULL AND item_id IS NULL)
),
CHECK (
    item_id IS NULL
    OR item_id IS NOT NULL AND (player_id IS NULL AND npc_id IS NULL)
)
);

CREATE TABLE equipped_items (
player_id INTEGER,
npc_id INTEGER,
item_id INTEGER UNIQUE,
slot INTEGER,
UNIQUE (player_id,npc_id,slot),
FOREIGN KEY (slot) REFERENCES item_slots(id),
FOREIGN KEY (player_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (npc_id) REFERENCES npcs(id) ON DELETE CASCADE,
FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,

CHECK (
    player_id IS NULL
    OR player_id IS NOT NULL AND (npc_id IS NULL)
),
CHECK (
    npc_id IS NULL
    OR npc_id IS NOT NULL AND (player_id IS NULL)
)
);


CREATE TABLE item_details (
item_id INTEGER UNIQUE,
item_type INTEGER,
trader_price INTEGER,
slot INTEGER,
item_level INTEGER,
rarity TEXT,
FOREIGN KEY (slot) REFERENCES item_slots(id),
FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
FOREIGN KEY (item_type) REFERENCES item_subcategories(id)
);


CREATE TABLE weapon_details (
item_id INTEGER UNIQUE,
damage_style INTEGER,
secondary_style INTEGER,
min_damage INTEGER,
max_damage INTEGER,
weapon_speed FLOAT,
FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
FOREIGN KEY (damage_style) REFERENCES damage_styles(id)
FOREIGN KEY (secondary_style) REFERENCES damage_styles(id)
);


CREATE TABLE item_conditions (
condition_name TEXT,
material TEXT,
modifier FLOAT,
FOREIGN KEY (material) REFERENCES item_subcategories(item_material)
);

CREATE TABLE armor_names (
    armor_name TEXT,
    slot TEXT,
    item_type TEXT,
    FOREIGN KEY (slot) REFERENCES item_slots(slot_name),
    FOREIGN KEY (item_type) REFERENCES item_subcategories(subcatergory_name)
);

CREATE TABLE weapon_speeds (
    weapon_type TEXT,
    speed FLOAT,
    FOREIGN KEY (weapon_type) REFERENCES item_subcategories(subcategory_name)
);

CREATE TABLE armor_multipliers (
    armor_slot TEXT,
    multiplier FLOAT,
    FOREIGN KEY (armor_slot) REFERENCES item_slots(slot_name)
);

CREATE TABLE combat_log(
id INTEGER PRIMARY KEY,
player_id INTEGER,
npc_id INTEGER,
combat_action TEXT,
damage INTEGER,
damage_style INTEGER,
player_swing_timer FLOAT DEFAULT 0,
npc_swing_timer FLOAT DEFAULT 0,
attacker TEXT,
FOREIGN KEY (damage_style) REFERENCES damage_styles(id),
FOREIGN KEY (player_id) REFERENCES users(id),
FOREIGN KEY (npc_id) REFERENCES npcs(id) ON DELETE CASCADE
);




INSERT INTO marketplace_categories(category) VALUES ("Want offers");
INSERT INTO marketplace_categories(category) VALUES ("Dont want offers");


INSERT INTO tile_types(type_name,difficulty) VALUES ("Swamp",50);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Dungeon",100);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Forest",30);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Village",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Mountain",300);

INSERT INTO npc_types(npc_type,biome) VALUES ("Human","Village");
INSERT INTO npc_types(npc_type,biome) VALUES ("Bear","Forest");
INSERT INTO npc_types(npc_type,biome) VALUES ("Alligator","Swamp");
INSERT INTO npc_types(npc_type,biome) VALUES ("Dragon","Mountain");
INSERT INTO npc_types(npc_type,biome) VALUES ("Skeleton","Dungeon");

INSERT INTO damage_types(damage_type) VALUES ("Magic");
INSERT INTO damage_types(damage_type) VALUES ("Physical");

INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Magic"),"Frost");
INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Magic"),"Fire");
INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Magic"),"Shock");

INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Physical"),"Stab");
INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Physical"),"Crush");
INSERT INTO damage_styles(type_id,style) VALUES ((SELECT id FROM damage_types WHERE damage_type="Physical"),"Slash");


INSERT INTO item_categories(category_name) VALUES ("Consumable");
INSERT INTO item_categories(category_name) VALUES ("Weapon");
INSERT INTO item_categories(category_name) VALUES ("Armor");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Metal Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Metal");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Leather Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Leather");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Cloth Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Cloth");
INSERT INTO item_subcategories(subcategory_name,category_id) VALUES ("Health Potion",(SELECT id FROM item_categories WHERE category_name="Consumable"));
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Dagger",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Axe",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Mace",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Sword",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Staff",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Wood");
INSERT INTO item_subcategories(subcategory_name,category_id,item_material) VALUES ("Wand",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Wood");

INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Dagger",0.8);
INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Axe",1.7);
INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Mace",2);
INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Sword",1.2);
INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Staff",1.5);
INSERT INTO weapon_speeds(weapon_type,speed) VALUES ("Wand",0.7);

INSERT INTO item_slots (slot_name) VALUES ("Weapon");
INSERT INTO item_slots (slot_name) VALUES ("Head");
INSERT INTO item_slots (slot_name) VALUES ("Shoulders");
INSERT INTO item_slots (slot_name) VALUES ("Chest");
INSERT INTO item_slots (slot_name) VALUES ("Legs");
INSERT INTO item_slots (slot_name) VALUES ("Hands");
INSERT INTO item_slots (slot_name) VALUES ("Feet");
INSERT INTO item_slots (slot_name) VALUES ("Potion");

INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Head",5);
INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Shoulders",6);
INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Chest",10);
INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Legs",7);
INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Hands",4);
INSERT INTO armor_multipliers (armor_slot,multiplier) VALUES ("Feet",3);

INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Rerebraces","Shoulders","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Pauldrons","Shoulders","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Spaulders","Shoulders","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Gardbrace","Shoulders","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Shoulder pads","Shoulders","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Shoulder pads","Shoulders","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Mantle","Shoulders","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Coif","Head","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Arming Cap","Head","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Hauberk","Chest","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Great Helm","Head","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Saller","Head","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Robe","Chest","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Tunic","Chest","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Blouse","Chest","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Body","Chest","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Jacket","Chest","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Pants","Legs","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Leggings","Legs","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Legs","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Kilt","Legs","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Skirt","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Trousers","Legs","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Shorts","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Hood","Head","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Helmet","Head","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Helmet","Head","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Gloves","Hands","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Gloves","Hands","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Vambraces","Hands","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Mittens","Hands","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Gauntlets","Hands","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Chaps","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Gloves","Hands","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Boots","Feet","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Greaves","Legs","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Cuisses","Legs","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Tasset","Legs","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Boots","Feet","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Sandals","Feet","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Sandals","Feet","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Tasset","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Sabaton","Feet","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Hosen","Legs","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Chausses","Legs","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Shoes","Feet","Cloth Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Turnshoes","Feet","Leather Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Cuirass","Chest","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Plackart","Chest","Metal Armor");
INSERT INTO armor_names (armor_name,slot,item_type) VALUES ("Hat","Head","Cloth Armor");

INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Rusty","Metal",0.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Iron","Metal",0.7);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Steel","Metal",0.8);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Reinforced Steel","Metal",1.0);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Bronze","Metal",0.5);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Mithril","Metal",1.1);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Stethril","Metal",1.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Copper","Metal",0.4);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Rugged","Leather",0.5);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Scrap Leather","Leather",0.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Snake Skin","Leather",0.6);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Alligator Hide","Leather",1.0);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Studded","Leather",0.8);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Dragonhide","Leather",1.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Rotten Wood","Wood",0.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Pine","Wood",0.4);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Birch","Wood",0.5);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Oak","Wood",0.7);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Teak","Wood",0.8);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Maple","Wood",1.0);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Torn","Cloth",0.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Cotton","Cloth",0.5);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Linen","Cloth",0.8);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Silk","Cloth",1.3);
INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Wool","Cloth",1.0);





