import numpy as np
def win_last_opponent (observation, configuration):
    if observation.step > 0:
        opp_hand = observation.lastOpponentAction
        return (opp_hand + 1) % 3
    else:
        return np.random.randint(3)
