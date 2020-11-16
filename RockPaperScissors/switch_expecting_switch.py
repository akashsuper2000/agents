
import numpy as np
import pandas as pd
import random

from kaggle_environments.envs.rps.utils import get_score

my_prev_move = None

def dont_always_copy_opponent_move(observation, configuration):
    """
    Implemented research logic.
    
    Info:
    Rock = 0, Paper = 1, Scissors = 2...
    """
    global my_prev_move
    N = configuration.signs
    curr_move = random.randrange(0, N)
    
    if observation.step == 0:
        my_prev_move = curr_move
        return curr_move
    else:
        opponent_prev_move = observation.lastOpponentAction
        
        result = get_score(my_prev_move, opponent_prev_move)
        
        if result == -1:    ##If we lose in the previous round
            curr_move = (opponent_prev_move + 1) % N
        elif result == 1:      ##If we win in previous round
            curr_move = opponent_prev_move
        else:               ##If there's a draw, we choose to go with random for now
            curr_move = random.randrange(0, N)
        
    my_prev_move = curr_move
    
    return curr_move
