# web_app_game
The goal is to make a website that functions as a small text based RPG game.

The basic structure of the game is that you generate worlds that you can explore, using a tile based navigation system. Your inventory persist throught different worlds. In the world you will encounter NPC's and containers that you can interact with to gain items. Items can be traded to other players through a marketplace system.

Goals for the project:
- [x] Players can register 
- [x] Players can login
- [x] Players can see NPC's and containers in a tile
- [x] Players can loot containers
- [x] Players can view their inventory
- [x] Players can drop items from their inventory
- [ ] Player attribute system
    - [ ] Players have attributes
    - [ ] Players get attributes from items
- [ ] Player home page with stats about the player
- [ ] World system
    - [ ] Players can move in the world
    - [ ] Worlds are automaticly generated
        - [ ] NPC's are generated from certain parameters
        - [ ] Items are generated from certain parameters
- [ ] Players can interact with NPC's
    - [ ] Combat system
        - [ ] Players can fight NPC's
    - [ ] Players can loot NPC's
    - [ ] Players can pickpocket NPC's
- [ ] Marketplace system
    - [ ] Gold system
        - [ ] Players can loot gold and sell items to certain NPC's
    - [ ] Players can sell items they loot to other players through a marketplace system



How to install and use:

Make a clone of this repository (Easiest way is to create a folder on your own computer and use the git clone tool)

Navigate to the folder that contains your clone and install the virtual enviroment: `$ python3 -m venv venv` (This guide assumes you have python installed already)

Next activate the virtual enviroment with the command `$ source venv/bin/activate`

Now install the flask using command `$ pip install flask`

Install database schema with command `$ sqlite3 game_database.db < schema.sql`

Start hosting the web application `$ flask run`