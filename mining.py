import random
import tkinter

class Zerg:
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
        #TODO make logic to create zerg horde
        drone_count = int(refined_minerals / 9)
        for value in range(drone_count):
            z = Drone()
            self.drones[id(z)] = z

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        action_choice = random.randint(0, 3)  # both arguments are inclusive
        random_drone_id = random.choice(list(self.drones.keys()))
        random_map_id = random.choice(list(self.maps.keys()))
        if action_choice == 0:
            result = "NONE"
        elif action_choice == 1:
            result = 'RETURN {}'.format(random_drone_id)
        else:
            result = 'DEPLOY {} {}'.format(random_drone_id, random_map_id)
        self.dashboard.log.config(state=tkinter.NORMAL)
        self.dashboard.log.insert(tkinter.END, result)
        self.dashboard.log.insert(tkinter.END, "\n")
        self.dashboard.log.see(tkinter.END)
        self.dashboard.log.config(state=tkinter.DISABLED)
        return result

class Drone(Zerg):
    def __init__(self):
        super().__init__(40)
        self.moves = 1
        self.capacity = 10
        self.carry = 0

    def action(self, context):
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        print(self.carry)
        print(context.north, context.south, context.east, context.west)
        if context.north == "*":
            self.carry += 1
            return directions.get(0)
        elif context.south == "*":
            self.carry += 1
            return directions.get(1)
        elif context.east == "*":
            self.carry += 1
            return directions.get(2)
        elif context.east == "*":
            self.carry += 1
            return directions.get(3)
        if context.north == "_" and self.carry > 5:
            self.carry = 0
            return directions.get(0)
        elif context.south == "_" and self.carry > 5:
            self.carry = 0
            return directions.get(1)
        elif context.east == "_" and self.carry > 5:
            self.carry = 0
            return directions.get(2)
        elif context.east == "_" and self.carry > 5:
            self.carry = 0
            return directions.get(3)
        if context.north == "~":
            return directions.get(1)
        elif context.south == "~":
            return directions.get(0)
        elif context.east == "~":
            return directions.get(3)
        elif context.east == "~":
            return directions.get(2)
        if context.north == "#":
            return directions.get(1)
        elif context.south == "#":
            return directions.get(0)
        elif context.east == "#":
            return directions.get(3)
        elif context.east == "#":
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
