
import numpy as np
import pandas as pd
import random

T = np.zeros((3, 3, 3))

self_actions = np.full(1001, -1, dtype=int)
oppo_actions = np.full(1001, -1, dtype=int)

observe_until = 600

def observe_and_predict(observation, configuration):
    
    step = observation.step
    global T, P
    global self_actions, oppo_actions
    global observe_until
    
    if step == 0:
        self_act = np.random.randint(3)
        self_actions[step] = self_act
        return self_act
    
    self_1s_bef = self_actions[step - 1]
    oppo_1s_bef = observation.lastOpponentAction
    oppo_actions[step - 1] = oppo_1s_bef
    
    if 2 <= step < observe_until:
        self_2s_bef = self_actions[step - 2]
        oppo_2s_bef = oppo_actions[step - 2]
        T[self_2s_bef][oppo_2s_bef][oppo_1s_bef] += 1

    P = T / np.maximum(1, T.sum(axis=2)[..., None])    
    p = P[self_1s_bef][oppo_1s_bef]
    
    if observe_until <= step and np.sum(p) == 1:
        self_act = int((np.random.choice([0, 1, 2], p=p) + 1)) % 3
    else:
        self_act = np.random.randint(3)
    
    self_actions[step] = self_act
    return self_act
