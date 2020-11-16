# for Debug/Train previous line should be commented out, uncomment to write submission.py

def reset_game_map(obs):
    """ redefine game_map as two dimensional array of objects and set amounts of halite in each cell """
    global game_map
    game_map = []
    for x in range(conf.size):
        game_map.append([])
        for y in range(conf.size):
            game_map[x].append({
                # value will be ID of owner
                "shipyard": None,
                # value will be ID of owner
                "ship": None,
                # amount of halite
                "halite": obs.halite[conf.size * y + x]
            })

def get_my_units_coords_and_update_game_map(obs):
    """ get lists of coords of my units and update locations of ships and shipyards on the map """
    # arrays of (x, y) coords
    my_shipyards_coords = []
    my_ships_coords = []
    
    for player in range(len(obs.players)):
        shipyards = list(obs.players[player][1].values())
        for shipyard in shipyards:
            x = shipyard % conf.size
            y = shipyard // conf.size
            # place shipyard on the map
            game_map[x][y]["shipyard"] = player
            if player == obs.player:
                my_shipyards_coords.append((x, y))
        
        ships = list(obs.players[player][2].values())
        for ship in ships:
            x = ship[0] % conf.size
            y = ship[0] // conf.size
            # place ship on the map
            game_map[x][y]["ship"] = player
            if player == obs.player:
                my_ships_coords.append((x, y))
    return my_shipyards_coords, my_ships_coords

def get_x(x):
    """ get x, considering donut type of the map """
    if x >= conf.size:
        x -= conf.size
    elif x < 0:
        x += conf.size
    return x

def get_y(y):
    """ get y, considering donut type of the map """
    if y >= conf.size:
        y -= conf.size
    elif y < 0:
        y += conf.size
    return y

def clear(x, y, player):
    """ check if cell is safe to move in """
    # if there is no shipyard, or there is player's shipyard
    # and there is no ship
    if ((game_map[x][y]["shipyard"] == player or game_map[x][y]["shipyard"] == None) and
            game_map[x][y]["ship"] == None):
        return True
    return False

def move_ship(x_initial, y_initial, ship_id, action, player, ships_amount):
    """ 
        ship will move in expanding circles clockwise or counterclockwise
        until reaching maximum radius, then radius will be minimal again
    """
    directions = ships_data[ship_id]["directions"]
    # set index of direction
    i = ships_data[ship_id]["directions_index"]
    for j in range(len(directions)):
        x = directions[i]["x"](x_initial)
        y = directions[i]["y"](y_initial)
        # if cell is ok to move in
        if (((clear(x, y, player) or (ships_amount > 10 and game_map[x][y]["ship"] == None)) and not enemy_ship_near(x, y, player)) or
                (ships_amount > 30 and game_map[x][y]["ship"] != player)):
            ships_data[ship_id]["moves_done"] += 1
            # apply changes to game_map, to avoid collisions of player's ships next turn
            game_map[x_initial][y_initial]["ship"] = None
            game_map[x][y]["ship"] = player
            # if it was last move in this direction
            if ships_data[ship_id]["moves_done"] >= ships_data[ship_id]["ship_max_moves"]:
                ships_data[ship_id]["moves_done"] = 0
                ships_data[ship_id]["directions_index"] += 1
                # if it is last direction in a list
                if ships_data[ship_id]["directions_index"] >= len(directions):
                    ships_data[ship_id]["directions_index"] = 0
                    ships_data[ship_id]["ship_max_moves"] += 1
                    # if ship_max_moves reached maximum radius expansion
                    if ships_data[ship_id]["ship_max_moves"] >= max_moves_amount:
                        ships_data[ship_id]["ship_max_moves"] = 1
            action[ship_id] = directions[i]["direction"]
            break
        else:
            # loop through directions
            i += 1
            if i >= len(directions):
                i = 0
    return action

def get_directions(i0, i1, i2, i3):
    """ get list of directions in a certain sequence """
    return [directions[i0], directions[i1], directions[i2], directions[i3]]

def enemy_ship_near(x, y, player):
    """ check if enemy ship is in one move away from game_map[x][y] """
    if (
            (game_map[x][get_y(y - 1)]["ship"] != player and game_map[x][get_y(y - 1)]["ship"] != None) or
            (game_map[x][get_y(y + 1)]["ship"] != player and game_map[x][get_y(y + 1)]["ship"] != None) or
            (game_map[get_x(x + 1)][y]["ship"] != player and game_map[get_x(x + 1)][y]["ship"] != None) or
            (game_map[get_x(x - 1)][y]["ship"] != player and game_map[get_x(x - 1)][y]["ship"] != None)
        ): return True
    return False

def define_some_globals(config):
    """ define some of the global variables """
    global conf
    global turns_to_next_wave_of_ships
    global convert_plus_spawn_cost
    global max_moves_amount
    global globals_not_defined
    conf = config
    turns_to_next_wave_of_ships = conf.size // 2
    convert_plus_spawn_cost = conf.convertCost + conf.spawnCost
    max_moves_amount = conf.size // 2
    globals_not_defined = False


############################################################################
conf = None
# game_map will be two dimensional array of objects
game_map = []
# object with ship ids and their data
ships_data = {}
# amount of turns to pass before spawning new ships
turns_to_next_wave_of_ships = None
# initial tactics index
tactics_index = 0
# amount of halite, that is considered to be low
low_amount_of_halite = 200
# sum of conf.convertCost and conf.spawnCost
convert_plus_spawn_cost = None
# number of the turn at which new wave of ships will be spawned
ship_spawn_turn = 0
# max amount of moves in one direction before turning
max_moves_amount = None
# not all global variables are defined
globals_not_defined = True

# list of directions
directions = [
    {
        "direction": "NORTH",
        "x": lambda z: z,
        "y": lambda z: get_y(z - 1)
    },
    {
        "direction": "EAST",
        "x": lambda z: get_x(z + 1),
        "y": lambda z: z
    },
    {
        "direction": "SOUTH",
        "x": lambda z: z,
        "y": lambda z: get_y(z + 1)
    },
    {
        "direction": "WEST",
        "x": lambda z: get_x(z - 1),
        "y": lambda z: z
    }
]

# list of tactics
tactics = [
    # N -> E -> S -> W
    {"directions": get_directions(0, 1, 2, 3)},
    # S -> E -> N -> W
    {"directions": get_directions(2, 1, 0, 3)},
    # N -> W -> S -> E
    {"directions": get_directions(0, 3, 2, 1)},
    # S -> W -> N -> E
    {"directions": get_directions(2, 3, 0, 1)},
    # E -> N -> W -> S
    {"directions": get_directions(1, 0, 3, 2)},
    # W -> S -> E -> N
    {"directions": get_directions(3, 2, 1, 0)},
    # E -> S -> W -> N
    {"directions": get_directions(1, 2, 3, 0)},
    # W -> N -> E -> S
    {"directions": get_directions(3, 0, 1, 2)},
]
tactics_amount = len(tactics)

def swarm_agent(obs, config):
    global ship_spawn_turn
    global tactics_index
    if globals_not_defined:
        define_some_globals(config)
    action = {}
    my_halite = obs.players[obs.player][0]
    
    reset_game_map(obs)
    my_shipyards_coords, my_ships_coords = get_my_units_coords_and_update_game_map(obs)

    ships_keys = list(obs.players[obs.player][2].keys())
    ships_values = list(obs.players[obs.player][2].values())
    shipyards_keys = list(obs.players[obs.player][1].keys())
    
    # if there is no shipyards
    if len(shipyards_keys) == 0 and (my_halite >= conf.convertCost or ships_values[0][1] >= convert_plus_spawn_cost):
        action[ships_keys[0]] = "CONVERT"
    else:
        # if there is no ships or only one shipyard and enough halite to spawn at least one ship
        if (len(ships_keys) == 0 or len(shipyards_keys) == 1) and my_halite >= conf.spawnCost:
            ship_spawn_turn = obs.step + turns_to_next_wave_of_ships
            for i in range(len(my_shipyards_coords)):
                if my_halite >= conf.spawnCost:
                    x = my_shipyards_coords[i][0]
                    y = my_shipyards_coords[i][1]
                    if clear(x, y, obs.player):
                        my_halite -= conf.spawnCost
                        action[shipyards_keys[i]] = "SPAWN"
                        game_map[x][y]["ship"] = obs.player
        # if it is time to spawn another wave of ships and there is enough halite to spawn at least one ship
        elif obs.step >= ship_spawn_turn and my_halite >= conf.spawnCost:
            for i in range(len(my_shipyards_coords)):
                if my_halite >= conf.spawnCost:
                    x = my_shipyards_coords[i][0]
                    y = my_shipyards_coords[i][1]
                    if clear(x, y, obs.player):
                        my_halite -= conf.spawnCost
                        action[shipyards_keys[i]] = "SPAWN"
                        game_map[x][y]["ship"] = obs.player
                else:
                    ship_spawn_turn += turns_to_next_wave_of_ships
                    break
        
        # actions of ships
        for i in range(len(my_ships_coords)):
            x = my_ships_coords[i][0]
            y = my_ships_coords[i][1]
            # if this is a new ship
            if ships_keys[i] not in ships_data:
                ships_data[ships_keys[i]] = {
                    "moves_done": 0,
                    "ship_max_moves": 1,
                    "directions": tactics[tactics_index]["directions"],
                    "directions_index": 0
                }
                tactics_index += 1
                if tactics_index >= tactics_amount:
                    tactics_index = 0
            # if ship has enough halite to convert to shipyard and not at halite source
            # or ship has two times convert_plus_spawn_cost amount of halite
            elif ((ships_values[i][1] >= convert_plus_spawn_cost and game_map[x][y]["halite"] == 0) or
                    ships_values[i][1] >= (convert_plus_spawn_cost * 2)):
                action[ships_keys[i]] = "CONVERT"
                game_map[x][y]["ship"] = None
            else:
                # if this cell has low amount of halite or enemy ship is near
                if game_map[x][y]["halite"] < low_amount_of_halite or enemy_ship_near(x, y, obs.player):
                    action = move_ship(x, y, ships_keys[i], action, obs.player, len(ships_keys))
    return action
