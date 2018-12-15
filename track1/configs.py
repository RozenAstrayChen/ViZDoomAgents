import numpy as np
# coding: utf-8

IMG_SHAPE = (80, 80)
a_size = 3
model_path = './check_point/my_way_home/'
#model_file = 'model-51000.ckpt'
model_file = 'model-3400.ckpt'
#model_file = 'model-30150.ckpt'
#model_file = 'model-41050.ckpt'

SCENARIO_PATH = '../scenarios/basic.cfg'

IS_SUPREME_VERSION = True
IS_TRAIN = True
LOAD_MODEL = False
AGENTS_NUM = 32
# 32
HIST_LEN = 4

'''
def button_combinations():
    actions = []
    m_forward = [[True], [False]]  # move forward
    m_right_left = [[True, False], [False, True], [False, False]]  # move right and move left
    t_right_left = [[True, False], [False, True], [False, False]]  # turn right and turn left
    attack = [[True], [False]]
    #speed = [[True], [False]]

    for i in m_forward:
        for j in m_right_left:
            for k in t_right_left:
                for m in attack:
                    #for n in speed:
                    actions.append(i+j+k+m)
    return actions
'''

'''
7 action type
    0. forward
    1. backward
    2. left forward
    3. right forward
    4. turn left
    5. turn right
    6. speed
'''


def button_combinations():
    actions = np.identity(6, dtype=int).tolist()
    return actions

ACTION_DIM = len(button_combinations())
SKIP_FRAME_NUM = 4

AGENT_PREFIX = 'Agent_'
AGENT_MONITOR = AGENT_PREFIX + '0'


starter_entropy_rate = 0.1
decay_steps = 1000
decay_rate = 0.96


left = 'images/left.png'
left_back = 'images/left_back.png'

right = 'images/right.png'
right_back = 'images/right_back.png'

forward = 'images/forward.png'
forward_back = 'images/forward_back.png'

turn_left = 'images/turn_left.png'
turn_left_back = 'images/turn_left_back.png'

turn_right = 'images/turn_right.png'
turn_right_back = 'images/turn_right_back.png'

attack = 'images/attack.png'
attack_back = 'images/attack_back.png'

speed = 'images/speed.png'
speed_back = 'images/speed_back.png'

MAX_TIME_OUT_STEP = 2100
