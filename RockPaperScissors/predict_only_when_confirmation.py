import random
import numpy as np
import lightgbm as lgb
import pandas as pd

USE_BACK = 10
CONT_WINS_THRES = 10
PRED_USE_STEP_THRES = 200
PRED_USE_SCORE_THRES = 0.9
my_actions = []
op_actions = []
pr_actions = []
cont_wins = 0
solutions   = []

## ============== LIGHT GBM PREDICTION ============== ## 
def predict(my_actions, op_actions):
    size = len(my_actions)
    
    d = dict()
    for u in range(USE_BACK):
        d[f"OP_{u}"] = op_actions[u: size - (USE_BACK - u)]
        d[f"MY_{u}"] = my_actions[u: size - (USE_BACK - u)]
    
    X_train = pd.DataFrame(d)
    y_train = op_actions[USE_BACK: size]
    y_train = pd.DataFrame(y_train, columns=["y"])
    
    n = dict()
    for u in range(USE_BACK):
        n[f"OP_{u}"] = [op_actions[size - (USE_BACK - u)]]
        n[f"MY_{u}"] = [my_actions[size - (USE_BACK - u)]]
    
    X_test = pd.DataFrame(n)

    classifier = lgb.LGBMClassifier(
        random_state=0, 
        n_estimators=10, 
    )
    
    classifier.fit(X_train, y_train)
    return classifier.predict_proba(X_test).tolist()[0], int(classifier.predict(X_test)[0])

## ============== RANDOM(NASH EQUILIBRIUM) ============== ##
def randomize():
    return int(random.randint(0, 2))

## ============== PREDICT ONLY CONFIRM, OTHER RANDOM ============== ##
def predict_only_when_confirmation(observation, configuration):
    global my_actions
    global op_actions
    global pr_actions
    global cont_wins
    
    if observation.step != 0:
        op_actions.append(observation.lastOpponentAction)
        if observation.step > PRED_USE_STEP_THRES + 1:
            if op_actions[-1] == pr_actions[-1]:
                cont_wins += 1
            else:
                cont_wins = 0
                
    
    if observation.step > PRED_USE_STEP_THRES:
        pred_proba, pred = predict(my_actions, op_actions)
        pr_actions.append(pred)
        if (max(pred_proba) > PRED_USE_SCORE_THRES) or (cont_wins > CONT_WINS_THRES):
            my_action = pred
            my_action = (my_action + 1) % 3
        
        else:
            my_action = randomize()
        
    else:    
        my_action = randomize()
    
    my_actions.append(my_action)
    
    return my_action
