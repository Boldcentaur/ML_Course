"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process
    This loop is run in a separate process, and communicates with the game process.
    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    final_x = 100
    s = [93,93]
    def get_direction(ball_x,ball_y,ball_pre_x,ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if(VectorX>=0 and VectorY>=0):
            return 0
        elif(VectorX>0 and VectorY<0):
            return 1
        elif(VectorX<0 and VectorY>0):
            return 2
        elif(VectorX<0 and VectorY<0):
            return 3

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        direction = get_direction(scene_info.ball[0],scene_info.ball[1],s[0],s[1])
        if s[0] != scene_info.ball[0]:
            gradient = (s[1] - scene_info.ball[1])/(s[0] - scene_info.ball[0])

            if gradient != 0:
                final_x = scene_info.ball[0] + (400 - scene_info.ball[1])/gradient
                if final_x < 0 or final_x > 200:
                    if direction == 0:
                        wall_y = gradient*(200 - scene_info.ball[0]) + scene_info.ball[1]
                        final_x = 200 - (400 - wall_y)/gradient
                    elif direction == 2:
                        wall_y = gradient*(0 - scene_info.ball[0]) + scene_info.ball[1]
                        final_x = 0 - (400 - wall_y)/gradient
        
        s = [scene_info.ball[0],scene_info.ball[1]]

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        elif direction == 1 or direction == 3:
            if scene_info.platform[0] < 79:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif scene_info.platform[0] > 81:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        elif direction == 2 or direction == 0:
            if scene_info.platform[0] > final_x - 16:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif scene_info.platform[0] < final_x - 24:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            
