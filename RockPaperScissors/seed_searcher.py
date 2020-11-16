
# Importing important imports
import numpy as np
import random

# Global Variables
seeds = list(range(2000))
previous_moves = []

def seed_searcher(obs, config):
    
    ''' An agent that searches for the seed of the opponent '''
    
    # Global Variables
    global previous_moves
    global seeds
    
    # Saving the current state
    init_state = random.getstate()
    
    # Initializing a backup move
    next_move = int(np.random.randint(3))
    
    # If there still are multiple canditates
    if obs.step and len(seeds) > 1:
        
        # Saving previous moves
        previous_moves.append(obs.lastOpponentAction)
        
        # Checking each possible seed
        for i in range(len(seeds) - 1, -1, -1):
            
            # Running for previous moves
            random.seed(seeds[i])
            for _ in range(obs.step):
                move = random.randint(0, 2)
           
            # Testing their move order
            if move != previous_moves[-1]:
                seeds.pop(i)
                
    # Seed found: Get the next move
    elif len(seeds) == 1:
        random.seed(seeds[0])
        for _ in range(obs.step):
            move = random.randint(0, 2)
        next_move = random.randint(0, 2)
            
    # Reseting the state to not interfer with the opponent
    random.setstate(init_state)
    
    # Returning an action
    return (next_move + 1) % 3
