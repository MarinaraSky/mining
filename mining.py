import random
import tkinter
import heapq


class Zerg:
    returns = list()
    starting_locations = dict()
    landing_clear = dict()
    deploying = dict()
    map_graphs = dict()
    map_minerals = dict()

    def __init__(self, health):
        self.health = health

    def action(self):
        pass


class Graph():
    def __init__(self):
        self.width = 100
        self.height = 100
        self.edges = {}
        self.weights = {}
        self.walls = []

    def cost(self, from_node, to_node):
        return self.weights.get(to_node, 1)

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        return id not in self.walls

    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        if (x+y) % 2 == 0:
            results.reverse()
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

    def __str__(self):
        output = ""
        for edge in self.edges:
            output += str(edge)
        return output

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 + y2)

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current!= start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


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
        Zerg.map_graphs[map_id] = Graph()

    def action(self):
        print("Zergs", self.drones.keys())
        print("Returns", Zerg.returns)
        print("Deploy", self.deploy)
        self.delete = []
        print(Zerg.starting_locations)
        for zerg in self.drones:
            drone = self.drones[zerg]
            if drone.context:
                path = None
                tile = (drone.context.x, drone.context.y)
                north = (drone.context.x, int(drone.context.y) + 1)
                south = (drone.context.x, int(drone.context.y) - 1)
                east = (int(drone.context.x) + 1, drone.context.y)
                west = (int(drone.context.x) - 1, drone.context.y)
                if drone.context.north == "*":
                    Zerg.map_minerals[drone.map] = north
                if drone.context.south == "*":
                    Zerg.map_minerals[drone.map] = south
                if drone.context.east == "*":
                    Zerg.map_minerals[drone.map] = east
                if drone.context.west == "*":
                    Zerg.map_minerals[drone.map] = west
                if drone.map in Zerg.map_minerals and Zerg.map_minerals[drone.map]:
                    print("Starting", Zerg.starting_locations[drone.map])
                    came_from,  cost_so_far = a_star_search(
                            Zerg.map_graphs[drone.map],
                            Zerg.starting_locations[drone.map],
                            Zerg.map_minerals[drone.map]
                        )
                    path = reconstruct_path(came_from,
                                     Zerg.starting_locations[drone.map],
                                     Zerg.map_minerals[drone.map])
                    print("Map: ", drone.map, "\nPath: ", path)
                #Zerg.map_graphs[drone.map].edges.update({tile: [north, south, east, west]})
                drone.commands = dict()
                if path:
                    drone.commands.update({"Mine": path})
                elif drone.context.north == "_" and drone.carry > 5:
                    drone.commands.update({"Return": 0})
                elif drone.context.south == "_" and drone.carry > 5:
                    drone.commands.update({"Return": 1})
                elif drone.context.east == "_" and drone.carry > 5:
                    drone.commands.update({"Return": 2})
                elif drone.context.west == "_" and drone.carry > 5:
                    drone.commands.update({"Return": 3})
                elif drone.context.north == "~" or drone.context.north == "#":
                    drone.commands.update({"Avoid": 1})
                elif drone.context.south == "~" or drone.context.south == "#":
                    drone.commands.update({"Avoid": 0})
                elif drone.context.east == "~" or drone.context.east == "#":
                    drone.commands.update({"Avoid": 3})
                elif drone.context.west == "~" or drone.context.west == "#":
                    drone.commands.update({"Avoid": 2})
                if drone.health <= 0:
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
        self.context = None
        self.path_step = 0
        self.commands = dict()

    def get_direction(self, starting, ending):
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        if starting[0] < ending[0]:
            return directions[3]
        elif starting[0] > ending[0]:
            return directions[2]
        elif starting[1] < ending[1]:
            return directions[1]
        elif starting[1] > ending[1]:
            return directions[0]

    def action(self, context):
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        print(self.carry)
        if self.steps == 0 and self.map not in Zerg.starting_locations:
            Zerg.starting_locations[self.map] = (context.x, context.y)
        if Zerg.starting_locations[self.map] == (context.x, context.y):
            Zerg.landing_clear[self.map] = False
        else:
            Zerg.landing_clear[self.map] = True
        self.context = context
        print(self.commands)
        if self.commands:
            if 'Mine' in self.commands:
                if self.commands['Mine'][-2] == (context.x, context.y):
                    self.carry += 1
                    return self.get_direction((context.x, context.y), self.commands['Mine'][-2])
                else:
                    self.path_step += 1
                    return self.get_direction((context.x, context.y), self.commands['Mine'][self.path_step])
                '''
                direction = self.commands['Mine']
                self.commands.pop('Mine')
                return directions.get(direction)
            '''
            elif 'Return' in self.commands:
                self.carry = 0
                direction = self.commands['Return']
                self.commands.pop('Return')
                Zerg.returns.append(id(self))
                return directions.get(direction)
            elif 'Avoid' in self.commands:
                direction = self.commands['Avoid']
                self.commands.pop('Avoid')
                return directions.get(direction)
        '''
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
        '''
        random_choice = random.randint(0, 3)  # both arguments are inclusive
        return directions.get(random_choice, "CENTER")

class Dashboard(tkinter.Toplevel):
     def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x200+300+0")
        self.title("Overlord's Dashboard")
        self.log = tkinter.Text(self, height=10,  width=30)
        self.log.pack()
