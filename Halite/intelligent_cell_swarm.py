# for Debug/Train previous line should be commented out, uncomment to write submission.py

import numpy as np

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


def findNearestYard(my_shipyards_coords, x, y):
    """ find nearest shipyard to deposit there"""
    min_dist = conf.size * 2
    closest_yard = 0
    for yard_idx, yard in enumerate(my_shipyards_coords):
        dist = np.min( (  ((x - my_shipyards_coords[yard_idx][0]) % conf.size), 
                                (21 - ((x - my_shipyards_coords[yard_idx][0]) % conf.size))  ) ) \
          + np.min( (  ((y - my_shipyards_coords[yard_idx][1]) % conf.size), 
                     (21 - ((y - my_shipyards_coords[yard_idx][1]) % conf.size))  ) )
        if dist < min_dist:
            min_dist = dist;
            closest_yard = yard_idx
    return closest_yard, min_dist
            


def get_x(x):
    """ get x, considering donut type of the map """
    return (x % conf.size)

def get_y(y):
    """ get y, considering donut type of the map """
    return (y % conf.size)

def clear(x, y, player):
    """ check if cell is safe to move in """
    # if there is no shipyard, or there is player's shipyard
    # and there is no ship
    if ((game_map[x][y]["shipyard"] == player or game_map[x][y]["shipyard"] == None) and
            game_map[x][y]["ship"] == None):
        return True
    return False


def moveTo(x_initial, y_initial, x_target, y_target, ship_id, player, actions):
    """ move toward target as quickly as possible without collision (or later, bad collision)"""
    if (x_target - x_initial) % conf.size <=  ( 1 + conf.size) // 2 :
        # move down
        x_dir = 1;
        x_dist = (x_target - x_initial) % conf.size
    else:
        # move up
        x_dir = -1;
        x_dist = (x_initial - x_target) % conf.size
    
    if (y_target - y_initial) % conf.size <=  ( 1 + conf.size) // 2 :
        # move down
        y_dir = 1;
        y_dist = (y_target - y_initial) % conf.size
    else:
        # move up
        y_dir = -1;
        y_dist = (y_initial - y_target) % conf.size
    
    action = None
    if x_dist > y_dist:
        # move X first if can;
        if clear( ( x_initial + x_dir) % conf.size, y_initial, player):
            action = ('WEST' if x_dir <0 else 'EAST')
        elif clear( x_initial, ( y_initial + y_dir) % conf.size, player) :
            action = ('NORTH' if y_dir < 0 else 'SOUTH')
    else:
        # move Y first if can
        if clear( x_initial, ( y_initial + y_dir) % conf.size, player) :
            action = ('NORTH' if y_dir < 0 else 'SOUTH')
        elif clear( ( x_initial + x_dir) % conf.size, y_initial, player):
            action = ('WEST' if x_dir <0 else 'EAST')
            
    if action is not None:
        game_map[x_initial][y_initial]["ship"] = None
        actions[ship_id] = action
        
    if action == 'NORTH':
        game_map[x_initial][(y_initial - 1) % conf.size]["ship"] = player
    elif action == 'SOUTH':
        game_map[x_initial][(y_initial + 1) % conf.size]["ship"] = player
    elif action == 'EAST':
        game_map[(x_initial - 1) % conf.size][y_initial]["ship"] = player
    elif action == 'WEST':
        game_map[(x_initial + 1) % conf.size][y_initial]["ship"] = player
    
    return actions
    

def move_ship(x_initial, y_initial, ship_id, actions, player, ships_amount):
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
        if (((clear(x, y, player) or (ships_amount > 10 and game_map[x][y]["ship"] == None))
                 and not enemy_ship_near(x, y, player)) or
                (ships_amount > 30 and game_map[x][y]["ship"] != player)):
            ships_data[ship_id]["moves_done"] += 1
            
            # apply changes to game_map, to avoid collisions of player's ships next turn
            game_map[x_initial][y_initial]["ship"] = None
            game_map[x][y]["ship"] = player
            
            # if it was last move in this direction, change direction
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
            actions[ship_id] = directions[i]["direction"]
            break
        else:
            # loop through directions
            i += 1
            if i >= len(directions):
                i = 0
    return actions


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
    turns_to_next_wave_of_ships = conf.size // 2               # tunable and cappable late in game obviously
    convert_plus_spawn_cost = conf.convertCost + conf.spawnCost
    max_moves_amount = conf.size // 2                             # tunable
    globals_not_defined = False


############################################################################
conf = None
game_map = [] 
ships_data = {}  
turns_to_next_wave_of_ships = None   
tactics_index = 0   
convert_plus_spawn_cost = None  
ship_spawn_turn = 0  
max_moves_amount = None  
globals_not_defined = True 

low_amount_of_halite = 200          

MIN_FINAL_DROPOFF = 200   
PCTILE_DROPOFF = 80   
RETURN_HOME = 350 
MUST_DROPOFF = 1200

SHIP_TO_BASE_MULT = 2   



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
    actions = {}
    my_halite = obs.players[obs.player][0]
    
    reset_game_map(obs)
    my_shipyards_coords, my_ships_coords = get_my_units_coords_and_update_game_map(obs)

    ships_keys = list(obs.players[obs.player][2].keys())
    ships_values = list(obs.players[obs.player][2].values())
    shipyards_keys = list(obs.players[obs.player][1].keys())

#     return {ships_keys[0]: "CONVERT"}


    
    # if there is no shipyards
    if len(shipyards_keys) == 0 and (my_halite >= conf.convertCost or ships_values[0][1] >= convert_plus_spawn_cost):
        actions[ships_keys[0]] = "CONVERT"

    else:
        # if (there are no ships or only one shipyard)     and         enough halite to spawn at least one ship
        #         then spawn a ship out of there
        
        if (len(ships_keys) == 0 or len(shipyards_keys) == 1) and my_halite >= conf.spawnCost:
            ship_spawn_turn = obs.step + turns_to_next_wave_of_ships
            for i in range(len(my_shipyards_coords)):
                if my_halite >= conf.spawnCost:
                    x = my_shipyards_coords[i][0]
                    y = my_shipyards_coords[i][1]
                    if clear(x, y, obs.player):
                        my_halite -= conf.spawnCost
                        actions[shipyards_keys[i]] = "SPAWN"
                        game_map[x][y]["ship"] = obs.player
                        
        # if it is time to spawn another wave of ships and there is enough halite to spawn at least one ship
        elif obs.step >= ship_spawn_turn and my_halite >= conf.spawnCost and obs.step < RETURN_HOME:
            for i in range(len(my_shipyards_coords)):
                if my_halite >= conf.spawnCost:
                    x = my_shipyards_coords[i][0]
                    y = my_shipyards_coords[i][1]
                    if clear(x, y, obs.player):
                        my_halite -= conf.spawnCost
                        actions[shipyards_keys[i]] = "SPAWN"
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
                    "moves_done": 0, "ship_max_moves": 1,
                    "directions": tactics[tactics_index]["directions"], "directions_index": 0 }
                tactics_index = (tactics_index + 1) % tactics_amount
                    
            # if ship has enough halite to convert to shipyard and not at halite source
            # or ship has two times convert_plus_spawn_cost amount of halite
            #   then turn it into a shipyard
            #    (add exception: if late game and have plenty of shipyards, or shipyards beyond necessary ratio, don't)
            elif ((ships_values[i][1] >= convert_plus_spawn_cost and game_map[x][y]["halite"] == 0) or
                    ships_values[i][1] >= (convert_plus_spawn_cost * SHIP_TO_BASE_MULT)):
                actions[ships_keys[i]] = "CONVERT"
                
                game_map[x][y]["ship"] = None
                
            # if this cell has low amount of halite or enemy ship is near
            elif game_map[x][y]["halite"] < low_amount_of_halite or enemy_ship_near(x, y, obs.player): 
                actions = move_ship(x, y, ships_keys[i], actions, obs.player, len(ships_keys))
            
            # IF TIME TO RETURN HOME AND DEPOSIT

                      
            if ( (obs.step > RETURN_HOME) and 
                  (  (ships_values[i][1] > MIN_FINAL_DROPOFF) or 
                           (ships_values[i][1] >  np.percentile( [s[1] for s in ships_values], PCTILE_DROPOFF) ) )
               or    (ships_values[i][1] > MUST_DROPOFF  ) ):
#                 print()
                # locate nearest shipyard
                if len(my_shipyards_coords) > 0:
                    closest_yard, min_dist = findNearestYard(my_shipyards_coords, x, y)
                    # move that way as long as don't collide with a ship
                    actions = moveTo(x, y, *my_shipyards_coords[closest_yard], ships_keys[i], obs.player, actions)

                    
#     if obs.step % 50 == 0:
#                 print(obs.step)
    return actions
