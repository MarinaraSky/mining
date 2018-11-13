import random
import tkinter

class Zerg:
    returns = list()
    starting_locations = dict()
    landing_clear = dict()
    deploying = dict()

    def __init__(self, health):
        self.health = health

    def action(self):
        pass

class Overlord(Zerg):
    def __init__(self, total_ticks, refined_minerals, dashboard=None):
        super().__init__(100)
        self.dashboard = dashboard
        self.maps = {}
        self.drones = {}
        self.deploy = list()
        self.random_map_id = 0
        self.return_count = 0
        self.drop_zone_count = 0
        #TODO make logic to create zerg horde
        drone_count = int(refined_minerals / 9)
        for value in range(drone_count):
            z = Drone()
            self.drones[id(z)] = z
            self.deploy.append(id(z))

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        print("Zergs", self.drones.keys())
        print("Returns", Zerg.returns)
        print("Deploy", self.deploy)
        self.delete = []
        print(Zerg.starting_locations)
        for zerg in self.drones:
            if self.drones[zerg].health <= 0:
                self.delete.append(zerg)
        for zerg in self.delete:
            self.drones.pop(zerg)
        if Zerg.returns:
            returning = Zerg.returns.pop()
            result = 'RETURN {}'.format(returning)
            Zerg.landing_clear[self.drones[returning].map] = True
            self.deploy.append(returning)
            self.return_count += 1
        elif self.deploy:
            deploying = self.deploy.pop()
            self.drones[deploying].map = self.random_map_id
            if self.random_map_id not in Zerg.landing_clear:
                Zerg.landing_clear[self.random_map_id] = True
            if self.random_map_id not in Zerg.deploying:
                Zerg.deploying[self.random_map_id] = False
            if Zerg.landing_clear[self.random_map_id] == True:
                result = 'DEPLOY {} {}'.format(deploying, self.random_map_id)
                if self.random_map_id < 2:
                    self.random_map_id += 1
                else:
                    self.random_map_id = 0
                Zerg.deploying[self.random_map_id] = True
            else:
                self.deploy.append(deploying)
                result = "NONE"
        else:
            result = "NONE"
        self.dashboard.log.config(state=tkinter.NORMAL)
        self.dashboard.log.insert(tkinter.END, result)
        self.dashboard.log.insert(tkinter.END, "\n")
        self.dashboard.log.see(tkinter.END)
        self.dashboard.log.config(state=tkinter.DISABLED)
        print("Return count: ", self.return_count)
        return result

class Drone(Zerg):
    def __init__(self):
        super().__init__(40)
        self.moves = 1
        self.capacity = 10
        self.carry = 0
        self.steps = 0
        self.map = 0

    def action(self, context):
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        print(self.carry)
        if self.steps == 0 and self.map not in Zerg.starting_locations:
            Zerg.starting_locations[self.map] = "{}, {}".format(context.x, context.y)
        '''
        print("North: ", context.north)
        print("South: ", context.south)
        print("East: ", context.east)
        print("West: ", context.west)
        print("X: ", context.x)
        print("Y: ", context.y)
        '''
        if Zerg.starting_locations[self.map] == "{}, {}".format(context.x, context.y):
            Zerg.landing_clear[self.map] = False
        else:
            Zerg.landing_clear[self.map] = True
        if context.north == "*" and self.carry < 10:
            self.carry += 1
            return directions.get(0)
        elif context.south == "*" and self.carry < 10:
            self.carry += 1
            return directions.get(1)
        elif context.east == "*" and self.carry < 10:
            self.carry += 1
            return directions.get(2)
        elif context.east == "*" and self.carry < 10:
            self.carry += 1
            return directions.get(3)
        if context.north == "_" and self.carry > 5:
            self.carry = 0
            self.steps += 1
            Zerg.returns.append(id(self))
            return directions.get(0)
        elif context.south == "_" and self.carry > 5:
            self.carry = 0
            self.steps += 1
            Zerg.returns.append(id(self))
            return directions.get(1)
        elif context.east == "_" and self.carry > 5:
            self.carry = 0
            self.steps += 1
            Zerg.returns.append(id(self))
            return directions.get(2)
        elif context.east == "_" and self.carry > 5:
            self.carry = 0
            self.steps += 1
            Zerg.returns.append(id(self))
            return directions.get(3)
        if context.north == "#":
            self.steps += 1
            return directions.get(1)
        elif context.south == "#":
            self.steps += 1
            return directions.get(0)
        elif context.east == "#":
            self.steps += 1
            return directions.get(3)
        elif context.east == "#":
            self.steps += 1
            return directions.get(2)
        random_choice = random.randint(0, 3)  # both arguments are inclusive
        return directions.get(random_choice, "CENTER")

class Dashboard(tkinter.Toplevel):
     def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x200+300+0")
        self.title("Overlord's Dashboard")
        self.log = tkinter.Text(self, height=10,  width=30)
        self.log.pack()
