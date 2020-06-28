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
            grid = set()
            coin_grid = set()
            speed_ahead = 100
            if self.car_pos[0] <= 35: # left bound
                grid.add(1)
                grid.add(4)
                grid.add(7)
            elif self.car_pos[0] >= 595: # right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)

            for coin in scene_info["coins"]:
                x_coin = self.car_pos[0] - coin[0]
                y_coin = self.car_pos[1] - coin[1]
                if x_coin <= 40 and x_coin >= -40 :      
                    if y_coin > 0 and y_coin < 300:
                        coin_grid.add(2)
                        if y_coin < 200:
                            coin_grid.add(5) 
                    elif y_coin < 0 and y_coin > -200:
                        coin_grid.add(8)
                if x_coin > -100 and x_coin < -40 :
                    if y_coin >= 150 and y_coin < 250:
                        coin_grid.add(3)
                    elif y_coin <= -80 and y_coin > -200:
                        coin_grid.add(9)
                    elif y_coin < 150 and y_coin > -80:
                        coin_grid.add(6)
                if x_coin < 100 and x_coin > 40:
                    if y_coin >= 150 and y_coin < 250:
                        coin_grid.add(1)
                    elif y_coin <= -80 and y_coin > -200:
                        coin_grid.add(7)
                    elif y_coin < 150 and y_coin > -80:
                        coin_grid.add(4)
            for car in scene_info["cars_info"]:            
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    if x <= 40 and x >= -40 :      
                        if y > 0 and y < 300:
                            grid.add(2)
                            if y < 200:
                                speed_ahead = car["velocity"]
                                grid.add(5) 
                        elif y < 0 and y > -200:
                            grid.add(8)
                    if x > -100 and x < -40 :
                        if y >= 150 and y < 250:
                            grid.add(3)
                        elif y <= -80 and y > -200:
                            grid.add(9)
                        elif y < 150 and y > -80:
                            grid.add(6)
                    if x < 100 and x > 40:
                        if y >= 150 and y < 250:
                            grid.add(1)
                        elif y <= -80 and y > -200:
                            grid.add(7)
                        elif y < 150 and y > -80:
                            grid.add(4)
            return move(grid= grid, coin_grid=coin_grid, speed_ahead = speed_ahead)
            
        def move(grid, coin_grid, speed_ahead): 
            if self.player_no == 0:
                print(scene_info["frame"], grid)
            if len(grid) == 0:
                return ["SPEED"]
            else:
                if(1 not in grid and 4 not in grid and (1 in coin_grid or 4 in coin_grid)):
                    self.commands = ["SPEED", "MOVE_LEFT"]
                elif(3 not in grid and 6 not in grid and (3 in coin_grid or 6 in coin_grid)):
                    self.commands = ["SPEED", "MOVE_RIGHT"]
                elif (2 not in grid): # Check forward 
                    # Back to lane center
                    if self.car_pos[0] > self.lanes[self.car_lane]:
                        self.commands = ["SPEED", "MOVE_LEFT"]
                        return ["SPEED", "MOVE_LEFT"]
                    elif self.car_pos[0 ] < self.lanes[self.car_lane]:
                        self.commands = ["SPEED", "MOVE_RIGHT"]
                        return ["SPEED", "MOVE_RIGHT"]
                    else :return ["SPEED"]
                else:
                    if (5 in grid): # NEED to BRAKE
                        if (1 not in grid) and (4 not in grid) and (3 not in grid) and (6 not in grid):
                            return self.commands
                        elif (1 not in grid) and (4 not in grid) and (7 not in grid): # turn left 
                            if self.car_vel < speed_ahead:
                                self.commands = ["SPEED", "MOVE_LEFT"]
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_LEFT"]
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (3 not in grid) and (6 not in grid) and (9 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                self.commands = ["SPEED", "MOVE_RIGHT"]
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_RIGHT"]
                                return ["BRAKE", "MOVE_RIGHT"]
                        elif (1 not in grid) and (4 not in grid): # turn left 
                            if self.car_vel < speed_ahead:
                                self.commands = ["SPEED", "MOVE_LEFT"]
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_LEFT"]
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (3 not in grid) and (6 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                self.commands = ["SPEED", "MOVE_RIGHT"]
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_RIGHT"]
                                return ["BRAKE", "MOVE_RIGHT"]
                        elif (4 not in grid) and (7 not in grid): # turn left 
                            if self.car_vel < speed_ahead:
                                self.commands = ["MOVE_LEFT"]
                                return ["MOVE_LEFT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_LEFT"]
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid) and (9 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                self.commands = ["MOVE_RIGHT"]
                                return ["MOVE_RIGHT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_RIGHT"]
                                return ["BRAKE", "MOVE_RIGHT"]
                        elif (4 not in grid): # turn left 
                            if self.car_vel < speed_ahead:
                                self.commands = ["MOVE_LEFT"]
                                return ["MOVE_LEFT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_LEFT"]
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                self.commands = ["MOVE_RIGHT"]
                                return ["MOVE_RIGHT"]
                            else:
                                self.commands = ["BRAKE", "MOVE_LEFT"]
                                return ["BRAKE", "MOVE_RIGHT"]
                        else : 
                            if self.car_vel < speed_ahead:  # BRAKE
                                return ["SPEED"]
                            else:
                                self.commands = ["BRAKE"]
                                return ["BRAKE"]
                    if (self.car_pos[0] < 60 ):
                        return ["SPEED", "MOVE_RIGHT"]
                    if (1 not in grid) and (4 not in grid) and (3 not in grid) and (6 not in grid):
                        return self.commands
                    if (1 not in grid) and (4 not in grid) and (7 not in grid): # turn left 
                        self.commands = ["SPEED", "MOVE_LEFT"]
                        return ["SPEED", "MOVE_LEFT"]
                    if (3 not in grid) and (6 not in grid) and (9 not in grid): # turn right
                        self.commands = ["SPEED", "MOVE_RIGHT"]
                        return ["SPEED", "MOVE_RIGHT"]
                    if (1 not in grid) and (4 not in grid): # turn left 
                        self.commands = ["SPEED", "MOVE_LEFT"]
                        return ["SPEED", "MOVE_LEFT"]
                    if (3 not in grid) and (6 not in grid): # turn right
                        self.commands = ["SPEED", "MOVE_RIGHT"]
                        return ["SPEED", "MOVE_RIGHT"]
                    if (4 not in grid) and (7 not in grid): # turn left 
                        self.commands = ["MOVE_LEFT"]
                        return ["MOVE_LEFT"]    
                    if (6 not in grid) and (9 not in grid): # turn right
                        self.commands = ["MOVE_RIGHT"]
                        return ["MOVE_RIGHT"]
                                
                    
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
