"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False

    s = 100
    def get_block_direction(block_x,block_pre_x):
        VectorX = block_x - block_pre_x
        if(VectorX>=0):
            return 1  #障礙物往右
        else:
            return 0  #障礙物往左

    def wall_correction(pred, limit_up, limit_down):
        if (pred > limit_up):
            x = (limit_up-scene_info["ball"][0]) // scene_info["ball_speed"][0]
            ball_wall_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            correction = ball_wall_x + scene_info["ball_speed"][0] - limit_up
            pred -= correction
            pred = limit_up - (pred - limit_up)
            if pred >= limit_down:
                return pred
            else:
                return wall_correction(pred, limit_up, limit_down)

        elif (pred < limit_down):
            x = (limit_down-scene_info["ball"][0]) // scene_info["ball_speed"][0]
            ball_wall_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            correction = ball_wall_x + scene_info["ball_speed"][0] - limit_down
            pred -= correction
            pred = abs(pred)
            if pred <= limit_up:
                return pred
            else:
                return wall_correction(pred, limit_up, limit_down)
        else:
            return pred

    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-1) and scene_info["platform_1P"][0]+20 < (pred+1): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-1) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-1) and scene_info["platform_2P"][0]+20 < (pred+1): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-1) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P():
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            x = (scene_info["platform_1P"][1]-5-scene_info["ball"][1] ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*(x+1))  # 預測最終位置 # pred means predict ball landing site 
            pred = wall_correction(pred, 195, 0)
            #print(pred, scene_info["ball"], scene_info["frame"]%100)
            if scene_info["ball"][1] <= 235:
                pred = hit_blocker_side(pred)
            return move_to(player = '1P',pred = pred)
        else : # 球正在向上 # ball goes up
            pred = 100
            if scene_info["ball"][1] >= 260:
                pred = hit_blocker_down()
            print(pred, scene_info["ball"], scene_info["frame"])
            return move_to(player = '1P',pred = pred)



    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0:
            pred = 100
            if scene_info["ball"][1] <= 235:
                pred = hit_blocker_up() 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*(x+1)) 
            pred = wall_correction(pred, 195, 0)
            if scene_info["ball"][1] >= 260:
                pred = hit_blocker_side2(pred)
            return move_to(player = '2P',pred = pred)

    def hit_blocker_side(pred):
        x = 100 - (scene_info["frame"]%100)
        block_frame = (scene_info["blocker"][1] - 5 - scene_info["ball"][1]) // (scene_info["ball_speed"][1])
        pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)
        flag = 0
        speed = scene_info["ball_speed"]
        if pred_y >= 235:
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*block_frame)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*block_frame)
        else:
            if scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,1])
            elif scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,-1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,-1])
            y = (scene_info["blocker"][1] - 5 - pred_y) // (speed[1])# 幾個frame以後會到障礙物的位置（
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)+(speed[0]*y)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)+(speed[1]*y)
            block_frame = x + y
            flag = 1

        block_direction = get_block_direction(scene_info["blocker"][0], s)
        if block_direction == 1:
            block_x = scene_info["blocker"][0] + 3*block_frame
        else:
            block_x = scene_info["blocker"][0] - 3*block_frame
        bound_block = block_x // 170
        if bound_block > 0:
            if bound_block % 2 == 0:
                block_x = block_x - (bound_block*170)
            else:
                block_x = 170 - (block_x - 170*bound_block)
                block_direction = 0
        elif bound_block < 0:
            if(bound_block % 2 == 1):
                block_x = abs(block_x - (bound_block+1)*170)
                block_direction = 1
            else:
                block_x = block_x + (abs(bound_block)*170)

        if block_direction == 1:
            block_x_next = block_x + 3
        else:
            block_x_next = block_x - 3
        if flag:
            pred_x_next = pred_x + speed[0]
            pred_y_next = pred_y + speed[1]
        else:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = pred_y + scene_info["ball_speed"][1]
        flag2 = 1
        for i in range(3):
            if pred_x_next < 0 or pred_x_next > 200:
                flag2 = -1
            pred_x_next2 = wall_correction(pred_x_next, 195, 0)
            pred = hit_side(pred_x_next2, pred_y_next, flag, block_direction, pred, block_x_next, speed)
            if block_direction == 1:
                block_x_next = block_x_next + 3
            else:
                block_x_next = block_x_next - 3
            if flag:
                pred_x_next = pred_x_next + speed[0]
                pred_y_next = pred_y_next + speed[1]
            else:
                pred_x_next = pred_x_next + scene_info["ball_speed"][0]
                pred_y_next = pred_y_next + scene_info["ball_speed"][1]
        return pred
    
    def hit_side(pred_x_next, pred_y_next, flag, block_direction, pred, block_x_next, speed):
        #print(pred_x_next, pred_y_next, scene_info["ball"], block_x_next, scene_info["blocker"])
        if pred_x_next > block_x_next - 5 and pred_x_next < block_x_next + 30 and pred_y_next >= 235 and pred_y_next <= 260:
            if block_direction == 1:
                pred_x_next = block_x_next - 5
            else:
                pred_x_next = block_x_next
            if not flag:
                pred_y_next = pred_y_next + scene_info["ball_speed"][1]
                frame = (scene_info["platform_1P"][1]-5-pred_y_next) // (scene_info["ball_speed"][1])
                pred2 = pred_x_next + scene_info["ball_speed"][0] * (frame+1)
            else:
                pred_y_next = pred_y_next + speed[1]
                frame = (scene_info["platform_1P"][1]-5-pred_y_next) // (speed[1])
                pred2 = pred_x_next + speed[0] * (frame+1)
            pred2 = wall_correction(pred, 195, 0)
            return pred2
        else:
            return pred

    def hit_blocker_side2(pred):
        x = 100 - (scene_info["frame"]%100)
        block_frame = (scene_info["blocker"][1] + 20 - scene_info["ball"][1]) // (scene_info["ball_speed"][1])
        pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)
        flag = 0
        speed = scene_info["ball_speed"]
        if pred_y <= 260:
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*block_frame)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*block_frame)
        else:
            if scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,1])
            elif scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,-1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,-1])
            y = (scene_info["blocker"][1] + 20 - pred_y) // (speed[1])# 幾個frame以後會到障礙物的位置（
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)+(speed[0]*y)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)+(speed[1]*y)
            block_frame = x + y
            flag = 1

        block_direction = get_block_direction(scene_info["blocker"][0], s)
        if block_direction == 1:
            block_x = scene_info["blocker"][0] + 3*block_frame
        else:
            block_x = scene_info["blocker"][0] - 3*block_frame
        bound_block = block_x // 170
        if bound_block > 0:
            if bound_block % 2 == 0:
                block_x = block_x - (bound_block*170)
            else:
                block_x = 170 - (block_x - 170*bound_block)
                block_direction = 0
        elif bound_block < 0:
            if(bound_block % 2 == 1):
                block_x = abs(block_x - (bound_block+1)*170)
                block_direction = 1
            else:
                block_x = block_x + (abs(bound_block)*170)

        if block_direction == 1:
            block_x_next = block_x + 3
        else:
            block_x_next = block_x - 3
        if flag:
            pred_x_next = pred_x + speed[0]
            pred_y_next = pred_y + speed[1]
        else:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = pred_y + scene_info["ball_speed"][1]
        flag2 = 1
        for i in range(3):
            if pred_x_next < 0 or pred_x_next > 200:
                flag2 = -1
            pred_x_next2 = wall_correction(pred_x_next, 195, 0)
            pred = hit_side2(pred_x_next2, pred_y_next, flag, block_direction, pred, block_x_next, speed)
            if block_direction == 1:
                block_x_next = block_x_next + 3
            else:
                block_x_next = block_x_next - 3
            if flag:
                pred_x_next = pred_x_next + speed[0]
                pred_y_next = pred_y_next + speed[1]
            else:
                pred_x_next = pred_x_next + scene_info["ball_speed"][0]
                pred_y_next = pred_y_next + scene_info["ball_speed"][1]
        return pred
    
    def hit_side2(pred_x_next, pred_y_next, flag, block_direction, pred, block_x_next, speed):
        #print(pred_x_next, pred_y_next, scene_info["ball"], block_x_next, scene_info["blocker"])
        if pred_x_next > block_x_next - 5 and pred_x_next < block_x_next + 30 and pred_y_next >= 235 and pred_y_next <= 260:
            if block_direction == 1:
                pred_x_next = block_x_next - 5
            else:
                pred_x_next = block_x_next
            if not flag:
                pred_y_next = pred_y_next + scene_info["ball_speed"][1]
                frame = (scene_info["platform_2P"][1]+30-pred_y_next) // (scene_info["ball_speed"][1])
                pred2 = pred_x_next + scene_info["ball_speed"][0] * (frame+1)
            else:
                pred_y_next = pred_y_next + speed[1]
                frame = (scene_info["platform_2P"][1]+30-pred_y_next) // (speed[1])
                pred2 = pred_x_next + speed[0] * (frame+1)
            pred2 = wall_correction(pred, 195, 0)
            return pred2
        else:
            return pred

    def hit_blocker_up():
        x = 100 - (scene_info["frame"]%100)
        block_frame = (scene_info["blocker"][1] - scene_info["ball"][1]) // (scene_info["ball_speed"][1])
        pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)
        flag = 0
        speed = scene_info["ball_speed"]
        if pred_y >= 235:
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*block_frame)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*block_frame)
        else:
            if scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,1])
            elif scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,-1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,-1])
            y = (scene_info["blocker"][1]+20 - pred_y) // (speed[1])
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)+(speed[0]*y)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)+(speed[1]*y)
            block_frame = x + y
            flag = 1

        block_direction = get_block_direction(scene_info["blocker"][0], s)
        if block_direction == 1:
            block_x = scene_info["blocker"][0] + 3*block_frame
        else:
            block_x = scene_info["blocker"][0] - 3*block_frame
        block_x = wall_correction(block_x, 170, 0)

        if block_direction == 1:
            block_x_next = block_x + 3
        else:
            block_x_next = block_x - 3

        if flag:
            pred_x_next = pred_x + speed[0]
            pred_y_next = pred_y + speed[1]
        else:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = pred_y + scene_info["ball_speed"][1]
        
        pred_x_next = wall_correction(pred_x_next, 195, 0)
        block_x_next = wall_correction(block_x_next, 170, 0)
        if pred_x_next > block_x_next - 5 and pred_x_next < block_x_next + 30:            
            pred = hit_up(pred_x, speed, flag)
            pred = wall_correction(pred, 195, 0)
            return pred
        
        else:
            return 80
        
    def hit_up(pred_x, speed, flag):
        if not flag:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = 235
            frame = (scene_info["platform_1P"][1]-5-260) // (-scene_info["ball_speed"][1])
            pred = pred_x_next + scene_info["ball_speed"][0] * (frame+1)
        else:
            pred_x_next = pred_x + speed[0]
            pred_y_next = 235
            frame = (scene_info["platform_1P"][1]-5-260) // (-speed[1])
            pred = pred_x_next + speed[0] * (frame+1)
        return pred

    def hit_blocker_down():
        x = 100 - (scene_info["frame"]%100)
        block_frame = (scene_info["blocker"][1]+20 - scene_info["ball"][1]) // (scene_info["ball_speed"][1])
        pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)
        flag = 0
        speed = scene_info["ball_speed"]
        if pred_y <= 260:
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*block_frame)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*block_frame)
        else:
            if scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,1])
            elif scene_info["ball_speed"][0] > 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [1,-1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] > 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,1])
            elif scene_info["ball_speed"][0] < 0 and scene_info["ball_speed"][1] < 0:
                speed = tuple(list(scene_info["ball_speed"]) + [-1,-1])
            y = (scene_info["blocker"][1]+20 - pred_y) // (speed[1])
            pred_x = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)+(speed[0]*y)
            pred_y = scene_info["ball"][1]+(scene_info["ball_speed"][1]*x)+(speed[1]*y)
            block_frame = x + y
            flag = 1

        block_direction = get_block_direction(scene_info["blocker"][0], s)
        if block_direction == 1:
            block_x = scene_info["blocker"][0] + 3*block_frame
        else:
            block_x = scene_info["blocker"][0] - 3*block_frame
        block_x = wall_correction(block_x, 170, 0)

        if block_direction == 1:
            block_x_next = block_x + 3
        else:
            block_x_next = block_x - 3
        if flag:
            pred_x_next = pred_x + speed[0]
            pred_y_next = pred_y + speed[1]
        else:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = pred_y + scene_info["ball_speed"][1]
        
        pred_x_next = wall_correction(pred_x_next, 195, 0)
        block_x_next = wall_correction(block_x_next, 170, 0)
        
        if pred_x_next > block_x_next - 5 and pred_x_next < block_x_next + 30:            
            pred = hit_down(pred_x, speed, flag)
            pred = wall_correction(pred, 195, 0)
            return pred
        
        else:
            return 80
        
    def hit_down(pred_x, speed, flag):
        if not flag:
            pred_x_next = pred_x + scene_info["ball_speed"][0]
            pred_y_next = 260
            frame = (scene_info["platform_1P"][1]-5-260) // (-scene_info["ball_speed"][1])
            pred = pred_x_next + scene_info["ball_speed"][0] * (frame+1)
        else:
            pred_x_next = pred_x + speed[0]
            pred_y_next = 260
            frame = (scene_info["platform_1P"][1]-5-260) // (-speed[1])
            pred = pred_x_next + speed[0] * (frame+1)
        return pred

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()
            s = scene_info['blocker'][0]

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
