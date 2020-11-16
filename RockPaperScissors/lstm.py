import tensorflow as tf
import queue
import numpy as np
import random
import time

inputs = tf.keras.Input((8, 9))
x = tf.keras.layers.LSTM(32, return_sequences=True)(inputs)
x = tf.keras.layers.LSTM(32, return_sequences=True)(x)
x = tf.keras.layers.LSTM(32)(x)
x = tf.keras.layers.Dense(32, activation='relu')(x)
out = tf.keras.layers.Dense(3, activation='softmax')(x)
model = tf.keras.models.Model(inputs = inputs, outputs = out)
opt = tf.keras.optimizers.Adam(lr = 1e-3)
model.compile(loss = tf.keras.losses.CategoricalCrossentropy(), optimizer = opt, metrics = ['accuracy'])

def queue(src, a):
    dst = np.roll(src, -1)
    dst[-1] = a
    return dst

opponent_hand = np.array([0,2,1,0,2,1,2,0])
my_hand = np.array([0,2,1,0,2,1,2,0])
win_loss = np.array([2,2,2,2,2,2,2,2])
my_last_hand = 0
mem_len = len(opponent_hand)

def copy_opponent_agent(observation, configuration):
    global opponent_hand, my_hand, win_loss
    global model
    global my_last_hand
    if observation.step > mem_len*2:
        l = observation.lastOpponentAction
        
        r = np.eye(3)[l]
        r = r.reshape(1, 3)
        smooth = np.eye(3)[(l+2)%3]
        smooth = smooth.reshape(1, 3)
        eps = np.random.rand()*0.1
        #r = r*(1-eps) + smooth*eps
        opp = np.array(opponent_hand)
        opp = np.eye(3)[opp]
        opp = opp.reshape(1, mem_len, 3)
        
        my = np.array(my_hand)
        my = np.eye(3)[my]
        my = my.reshape(1, mem_len, 3)
        
        wld = np.array(win_loss)
        wld = np.eye(3)[wld]
        wld = wld.reshape(1, mem_len, 3)
        
        b = np.concatenate([opp, my, wld], axis=-1)
        
        h = model.train_on_batch(b, r)
        print(f'loss:{h[0]}, acc:{h[1]}')
        
        opponent_hand = queue(opponent_hand, l)
        opp = np.array(opponent_hand)
        opp = np.eye(3)[opp]
        opp = opp.reshape(1, mem_len, 3)
        
        my_hand = queue(my_hand, my_last_hand)
        my = np.array(my_hand)
        my = np.eye(3)[my]
        my = my.reshape(1, mem_len, 3)
        
        win_loss = queue(win_loss, (my_last_hand-l)%3)
        wld = np.array(win_loss)
        wld = np.eye(3)[wld]
        wld = wld.reshape(1, mem_len, 3)
        
        b = np.concatenate([opp, my, wld], axis=-1)
        
        t = model.predict(b)
        print(f'predict:{t}')
        p = np.argmax(t)
        if t[0][p] > 0.4:
            my_last_hand = (int(p) + 1) % 3
            return my_last_hand
        else:
            my_last_hand = random.randint(0, 2)
            return my_last_hand
        
    elif observation.step > mem_len:
        l = observation.lastOpponentAction
        r = np.eye(3)[l]
        r = r.reshape(1,3)
        smooth = np.eye(3)[(l+2)%3]
        smooth = smooth.reshape(1, 3)
        eps = np.random.rand()*0.1
        #r = r*(1-eps) + smooth*eps
        opp = np.array(opponent_hand)
        opp = np.eye(3)[opp]
        opp = opp.reshape(1, mem_len, 3)
        
        my = np.array(my_hand)
        my = np.eye(3)[my]
        my = my.reshape(1, mem_len, 3)
        
        wld = np.array(win_loss)
        wld = np.eye(3)[wld]
        wld = wld.reshape(1, mem_len, 3)
        
        b = np.concatenate([opp, my, wld], axis=-1)
        
        h = model.train_on_batch(b, r)
        print(f'loss:{h[0]}, acc:{h[1]}')

        opponent_hand = queue(opponent_hand, l)
        my_hand = queue(my_hand, my_last_hand)
        win_loss = queue(win_loss, (my_last_hand-l)%3)
        print(opponent_hand[-1],my_hand[-1],win_loss[-1])
        my_last_hand = random.randint(0, 2)
        return my_last_hand
    elif observation.step > 0:
        l = observation.lastOpponentAction
        opponent_hand = queue(opponent_hand, l)
        my_hand = queue(my_hand, my_last_hand)
        win_loss = queue(win_loss, (my_last_hand-l)%3)
        my_last_hand = random.randint(0, 2)
        return my_last_hand
    else:
        my_last_hand = random.randint(0, 2)
        return my_last_hand

    
# dummy to prevent Time Limit Exceed
l = 1
r = np.eye(3)[l]
r = r.reshape(1,3)
smooth = np.eye(3)[(l+2)%3]
smooth = smooth.reshape(1, 3)
eps = np.random.rand()*0.1
#r = r*(1-eps) + smooth*eps

opp = np.array(opponent_hand)
opp = np.eye(3)[opp]
opp = opp.reshape(1, mem_len, 3)

my = np.array(my_hand)
my = np.eye(3)[my]
my = my.reshape(1, mem_len, 3)

wld = np.array(win_loss)
wld = np.eye(3)[wld]
wld = wld.reshape(1, mem_len, 3)

b = np.concatenate([opp, my, wld], axis=-1)
h = model.train_on_batch(b,r)
t = model.predict(b)
