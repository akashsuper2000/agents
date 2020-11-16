
import random
from sklearn.naive_bayes import MultinomialNB
import numpy as np

# Idea: save the last N rounds in a ringbuffer.
#   FIXME: (Looking at the size of the problem, one could probably store the complete timeline, which would be more elegant ..)

num_of_rounds = 6 # Used in buffer
# Has to be an even number, as I log my moves and the opponent move

ringbuffer = [0]*num_of_rounds
ringbuffer_full = 0
ringbuffer_idx = 0

switch_to_predictive_mode = 200 # Round in which you move over from strategy 1 to the predictive strategy

my_last_move = -1

clf = MultinomialNB()

def ml(observation, configuration):
    global my_last_move, num_of_rounds, switch_to_predictive_mode
    global ringbuffer, ringbuffer_full, ringbuffer_idx
    global clf
    
    if observation.step > 0:
        ringbuffer_idx_old = ringbuffer_idx 
        ringbuffer[ringbuffer_idx] = my_last_move
        ringbuffer_idx = ringbuffer_idx+1
        ringbuffer[ringbuffer_idx] = observation.lastOpponentAction
        ringbuffer_idx = (ringbuffer_idx+1)%num_of_rounds
        
        if ringbuffer_idx == 0:
            ringbuffer_full = True
        
        if ringbuffer_full:
            # define X and y
            idx = ringbuffer_idx
            X   = np.array([0]*(num_of_rounds-2))
            i=0
            while True:
                X[i]=ringbuffer[idx]
                X[i+1]=ringbuffer[idx+1]
                i += 2
                idx = (idx+2)%num_of_rounds
                
                if idx == ringbuffer_idx_old:
                    break
            
            X=X.reshape(1, -1)
            y=[observation.lastOpponentAction]
            
            clf.partial_fit(X, y, classes=[0,1,2])
        
        if observation.step > switch_to_predictive_mode:
            # define latest
            idx = (ringbuffer_idx+2)%num_of_rounds
            X   = np.array([0]*(num_of_rounds-2))
            i=0
            while True:
                X[i]=ringbuffer[idx]
                X[i+1]=ringbuffer[idx+1]
                i += 2
                idx = (idx+2)%num_of_rounds
                
                if i == num_of_rounds-2:
                    break
            
            X=X.reshape(1, -1)
            pred = clf.predict(X)
            pred=int(pred[0])
            my_last_move = (pred+1)%3
            return my_last_move
    
    my_last_move = random.randint(0,2)
    
    return my_last_move
