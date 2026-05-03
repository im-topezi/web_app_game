# web_app_game
The goal is to make a website that functions as a small text based RPG game.

Course requirements:
- [x] Players can register 
- [x] Players can login
- [x] Players can list items to the marketplace
- [x] Players can see listed items
- [x] Players can filter listed items with different parameters
- [x] Player page shows player listed items, players stats and equipped items
- [x] Items have categories on their own, but players can also choose if they want to receive trade offers for their listings when making a listing
- [x] players can make offers to other players marketplace listings if they have allowed it


The basic structure of the game is that you generate worlds that you can explore, using a tile based navigation system. Your inventory persist throught different worlds. In the world you will encounter NPC's and containers that you can interact with to gain items. Items can be traded to other players through a marketplace system.

Goals for the project:
- [x] Players can register 
- [x] Players can login
- [x] Players can see NPC's and containers in a tile
- [x] Players can loot containers
- [x] Players can view their inventory
- [x] Players can drop items from their inventory
- [x] Player attribute system
    - [x] Players have attributes
    - [x] Players get attributes from items
- [x] Player home page with stats about the player
- [x] World system
    - [x] Players can move in the world
    - [x] Worlds are automaticly generated
        - [x] NPC's are generated from certain parameters
        - [x] Items are generated from certain parameters
- [x] Players can interact with NPC's
    - [x] Combat system
        - [x] Players can fight NPC's
    - [x] Players can loot NPC's
    - [x] Players can pickpocket NPC's
- [x] Marketplace system
    - [x] Players can post trade offers to other players items
    - [x] Items have categories
    - [x] Marketplace has a search option
        - [x] Search can filter with categories
    - [x] Gold system
        - [x] Players can loot gold and sell items on the blackmarket
    - [x] Players can sell items they loot to other players through a marketplace system



How to install and use:

Make a clone of this repository (Easiest way is to create a folder on your own computer and use the git clone tool)

Navigate to the folder that contains your clone and install the virtual enviroment: `$ python3 -m venv venv` (This guide assumes you have python installed already)

Next activate the virtual enviroment with the command `$ source venv/bin/activate`

Now install the flask using command `$ pip install flask`

Install database schema with command `$ sqlite3 game_database.db < schema.sql`

Start hosting the web application `$ flask run`