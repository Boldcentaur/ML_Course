import pickle
import os
import numpy as np

path = os.getcwd()
path = os.path.join(path,"games","RacingCar","ml","save")

allFile = os.listdir(path) # load log file
model = []

for file in allFile:
    with open(os.path.join(path,file),"rb") as f:
        model.append(pickle.load(f)) 
                
class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.commands = ['SPEED']
        pass

    def update(self, scene_info):
        """
        9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 |  c |  6 |
        |    |    |    |
        |  7 |  8 |  9 |
        |    |    |    |       
        """
        def check_grid():
            vel = [0,0,0,0,0,0,0,0,0,0,0]
            speed_ahead = 100
            if self.car_pos[0] <= 35: # left bound
                vel[0] = 10
                vel[3] = 10
                vel[6] = 10
            elif self.car_pos[0] >= 595: # right bound
                vel[2] = 10
                vel[5] = 10
                vel[8] = 10

            for car in scene_info["cars_info"]:
                if car["id"] == self.player_no:
                    vel[9] = car["velocity"]
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    if x <= 40 and x >= -40 :      
                        if y > 0 and y < 300:
                            vel[1] = car["velocity"]
                            if y < 200:
                                speed_ahead = car["velocity"]
                                vel[4] = car["velocity"]
                        elif y < 0 and y > -200:
                            vel[7] = car["velocity"]
                    if x > -100 and x < -40 :
                        if y > 80 and y < 250:
                            vel[2] = car["velocity"]
                        elif y < -80 and y > -200:
                            vel[8] = car["velocity"]
                        elif y < 80 and y > -80:
                            vel[5] = car["velocity"]
                    if x < 100 and x > 40:
                        if y > 80 and y < 250:
                            vel[0] = car["velocity"]
                        elif y < -80 and y > -200:
                            vel[6] = car["velocity"]
                        elif y < 80 and y > -80:
                            vel[3] = car["velocity"]
                vel[10] = speed_ahead
            return move(vel = (np.array(vel)).reshape(1, -1), speed_ahead = speed_ahead)
            
        def move(vel, speed_ahead):                         
            command = model[0].predict(vel)
            print(command)
            if command == 0:
                return ["SPEED"]
            elif command == 1:
                return ["BRAKE"]
            elif command == 2:
                return ["MOVE_LEFT"]
            elif command == 3:
                return ["MOVE_RIGHT"]
            elif command == 4:
                return ["SPEED", "MOVE_LEFT"]
            elif command == 5:
                return ["SPEED", "MOVE_RIGHT"]
            elif command == 6:
                return ["BRAKE", "MOVE_LEFT"]
            elif command == 7:
                return ["BRAKE", "MOVE_RIGHT"]


        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70
        return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass
