CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
set_stats BOOLEAN DEFAULT FALSE,
health INTEGER DEFAULT 100,
gold INTEGER DEFAULT 0 NOT NULL,
CHECK (gold >= 0),
CHECK (health >= 0));


CREATE TABLE worlds (
id TEXT UNIQUE,
player INTEGER,
difficulty INTEGER,
world_name TEXT,
visited BOOLEAN DEFAULT FALSE,
FOREIGN KEY (player) REFERENCES users(id)
);

CREATE TABLE tile_types(
type_name TEXT PRIMARY KEY,
difficulty INTEGER
);

CREATE TABLE npc_types (
    id INTEGER PRIMARY KEY,
    npc_type TEXT,
    biome INTEGER,
    FOREIGN KEY (biome) REFERENCES tile_types(type_name)
);


CREATE TABLE tiles (
id INTEGER PRIMARY KEY,
world_id TEXT,
x_coordinate INTEGER,
y_coordinate INTEGER,
tile_type TEXT,
FOREIGN KEY (world_id) REFERENCES worlds(id),
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
FOREIGN KEY (first_tile) REFERENCES tiles(id),
FOREIGN KEY (second_tile) REFERENCES tiles(id)
);

CREATE TABLE npcs (
id INTEGER PRIMARY KEY,
npc_name TEXT,
tile INTEGER,
npc_type_id INTEGER,
FOREIGN KEY (tile) REFERENCES tiles(id),
FOREIGN KEY (npc_type_id) REFERENCES npc_types(id)
);

CREATE TABLE containers (
id INTEGER PRIMARY KEY,
container_type TEXT,
tile INTEGER,
FOREIGN KEY (tile) REFERENCES tiles(id)
);

CREATE TABLE item_categories (
    id INTEGER PRIMARY KEY,
    category_name TEXT
);

CREATE TABLE item_slots (
id INTEGER PRIMARY KEY,
slot TEXT
);

CREATE TABLE item_subcategories (
id INTEGER PRIMARY KEY,
category_id INTEGER,
subcatergory_name TEXT,
item_material TEXT,
FOREIGN KEY (category_id) REFERENCES item_categories(id)
);



CREATE TABLE items (
id INTEGER PRIMARY KEY,
item_name TEXT,
npc INTEGER,
player INTEGER,
container INTEGER,
FOREIGN KEY (npc) REFERENCES npcs(id),
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (container) REFERENCES containers(id),
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

CREATE TABLE marketplace_listings (
id INTEGER PRIMARY KEY,
item_id INTEGER NOT NULL,
seller_id INTEGER NOT NULL,
marketplace_price INTEGER,
FOREIGN KEY (item_id) REFERENCES items(id),
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
FOREIGN KEY (player_id) REFERENCES users(id),
FOREIGN KEY (npc_id) REFERENCES npcs(id),
FOREIGN KEY (item_id) REFERENCES items(id),

CHECK (
    player_id IS NULL
    OR player_id IS NOT NULL AND (npc_id IS NULL AND item_id IS NULL) AND ((stamina+strength+agility+magic)<16) AND (armor=0)
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


CREATE TABLE item_details (
item_id INTEGER UNIQUE,
item_type INTEGER,
slot INTEGER,
trader_price INTEGER,
FOREIGN KEY (item_id) REFERENCES items(id),
FOREIGN KEY (item_type) REFERENCES item_subcategories(id),
FOREIGN KEY (slot) REFERENCES item_slot(id)
);


CREATE TABLE weapon_details (
item_id INTEGER UNIQUE,
damage_style INTEGER,
min_base_damage INTEGER,
max_base_damage INTEGER,
base_speed FLOAT,
FOREIGN KEY (item_id) REFERENCES items(id),
FOREIGN KEY (damage_style) REFERENCES damage_styles(id)
);

CREATE TABLE item_conditions (
condition_name TEXT,
material TEXT,
modifier FLOAT,
FOREIGN KEY (material) REFERENCES item_subcategories(item_material)
);





INSERT INTO tile_types(type_name,difficulty) VALUES ("Swamp",50);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Dungeon",100);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Forest",30);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Village",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Mountain",300);

INSERT INTO npc_types(npc_type,biome) VALUES ("Human","Village");
INSERT INTO npc_types(npc_type,biome) VALUES ("Bear","Forest");
INSERT INTO npc_types(npc_type,biome) VALUES ("Alligator","Swamp");
INSERT INTO npc_types(npc_type,biome) VALUES ("Dragon","Mountain");

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
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Metal Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Metal");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Leather Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Leather");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Cloth Armor",(SELECT id FROM item_categories WHERE category_name="Armor"),"Cloth");
INSERT INTO item_subcategories(subcatergory_name,category_id) VALUES ("Health Potion",(SELECT id FROM item_categories WHERE category_name="Consumable"));
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Dagger",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Axe",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Mace",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Sword",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Metal");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Staff",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Wood");
INSERT INTO item_subcategories(subcatergory_name,category_id,item_material) VALUES ("Wand",(SELECT id FROM item_categories WHERE category_name="Weapon"),"Wood");


INSERT INTO item_conditions (condition_name,material,modifier) VALUES ("Rusty","Metal",0.3)


INSERT INTO users (username,gold) VALUES ("Test user",1000);
INSERT INTO users (username,gold) VALUES ("Test user2",1000);
INSERT INTO items (item_name,player) VALUES ("Rusty sword",1);
INSERT INTO items (item_name,player) VALUES ("Super sword",2);
INSERT INTO marketplace_listings (item_id,seller_id,marketplace_price) VALUES (1,1,100);
INSERT INTO trade_offers (sold_item,buyer_id,gold_offer) VALUES (1,2,40);
INSERT INTO offered_items (offer_id,item_id) VALUES (1,2);


