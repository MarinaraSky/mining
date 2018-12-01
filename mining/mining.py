import random
import tkinter
import heapq
import collections




class Zerg:
    returns = list()            # List of zergs for return
    starting_locations = dict()     # Dict of starting locations by map id
    landing_clear = {0: True, 1: True, 2: True}      # Dict of bools signaling clear landing pads
    deploying = dict()          # Dict of zergs being deployed by id
    map_graphs = dict()         # Dict of graph objects by map id
    map_display = dict()   # Dict of frames for map displays
    minerals = {0: set(), 1: set(), 2: set()}
    map_viable = {-1: False, 0: True, 1: True, 2: True}    # Dict of minerals per map by id

    def __init__(self, health):
        self.health = health

    def action(self, context=None):
        pass

'''
    Graph, PriorityQueue, heuristic, and a_star_search was implemented
    based on the following website. Code was modified in places to fit
    the needs of the program.

    Source:
    https://www.redblobgames.com/pathfinding/a-star/implementation.html
'''


class Graph():
    def __init__(self):
        self.width = 200    # Twice as big as needed to accomodate odd coords
        self.height = 200
        self.weights = {}   # Dict of weights for nodes, Acid = 4, ground = 1
        self.walls = []     # List of walls to avoid
        self.acid = []      # List of acid tiles for weights
        self.visited = set()    # Set of visited tiles
        self.unvisited = list()  # List of visitable tiles yet to be explored

    def cost(self, from_node, to_node):
        weight = 1
        if to_node in self.acid:
            weight = 4
        return self.weights.get(to_node, weight)

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
    '''
    Combined a_star_search and reconstruct path from above source
    '''
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

    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


class Overlord(Zerg):
    def __init__(self, total_ticks, refined_minerals, dashboard=None):
        super().__init__(100)
        self.dashboard = dashboard      # Display object
        self.total_ticks = total_ticks  # Keeps track of ticks remaining
        self.maps = {}                  # Dict of maps by id
        self.drones = {}                # Dict of drones by id
        self.miners = {}
        self.deploy = list()            # List of drones to deploy
        self.random_map_id = 0          # Which map to deploy to
        self.map_dashboards = list()    # List of Tkinter windows for maps
        self.last_discovery = 0         # Variance for discovery
        self.ticks_remaining = total_ticks

        screen_position = "300x200+{}+{}"   # Screen placement for map windows
        screen_x = 300
        screen_y = 500
        for x in range(3):  # Initializes the map windows
            self.map_dashboards.append(Dashboard(self.dashboard))
            self.map_dashboards[x].geometry(
                    screen_position.format(screen_x, screen_y))
            screen_x += 300

            dash_title = "MAP {}".format(x)
            self.map_dashboards[x].title(dash_title)
            self.map_dashboards[x].log.forget()
            del self.map_dashboards[x].log
            self.map_dashboards[x].log = tkinter.Text(
                    self.map_dashboards[x], height=10,  width=30)
            self.map_dashboards[x].log.grid(row=110, column=0, columnspan=100)
        # TODO make logic to create zerg horde
        drone_count = int(refined_minerals / 9)
        while refined_minerals > 9:
            if len(self.drones) != 3:
                z = Scout()
                self.drones[id(z)] = z
                refined_minerals -= 9
            else:
                break
        while refined_minerals > 24:
            z = Miner()
            self.miners[id(z)] = z
            refined_minerals -= 24
        self.deployable = list(self.drones)
        self.mining_units = set(self.miners)
        self.drones.update(self.miners)

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary
        Zerg.map_graphs[map_id] = Graph()
        width, height = 100, 100
        Zerg.map_display[map_id] = [[
            tkinter.Frame(
                self.map_dashboards[map_id], height=12, width=12, bg='black')
            for x in range(width)] for y in range(height)]

    def action(self, context=None):
        super().action(context)
        self.ticks_remaining -= 1
        tmp_drones = self.drones.copy()
        for zerg_id, zerg in tmp_drones.items():
            if zerg.health < 1:
                del self.drones[zerg_id]
            elif zerg.deployed == True and zerg.context:
                self.get_drone_info(zerg)
            elif zerg.deployed == False and isinstance(zerg, Miner):
                self.mining_units.add(id(zerg))
        #print("Deploy: ", self.deployable)
        #print("Mining Units: ", self.mining_units)
        #print("Returns: ", Zerg.returns)
        #print("Landings: ", Zerg.landing_clear)
        #print("Viable: ", Zerg.map_viable)
        #print("Unvisted(0): ", Zerg.map_graphs[0].unvisited)
        #print("Visted(0): ", Zerg.map_graphs[0].visited)
        #print("Unvisted(1): ", Zerg.map_graphs[1].unvisited)
        #print("Visted(1): ", Zerg.map_graphs[1].visited)
        #print("Unvisted(2): ", Zerg.map_graphs[2].unvisited)
        #print("Visted(2): ", Zerg.map_graphs[2].visited)
        result = "NONE"
        if Zerg.returns:
            for drone in Zerg.returns:
                drone_tile = (self.drones[drone].context.x, self.drones[drone].context.y)
                if drone_tile == Zerg.starting_locations[self.drones[drone].map]:
                    returning = drone
                    Zerg.returns.remove(returning)
                    result = "RETURN {}".format(returning)
                    Zerg.landing_clear[self.drones[returning].map] = True
                    if isinstance(self.drones[returning], Miner):
                        self.mining_units.add(returning)
                    elif isinstance(self.drones[returning], Scout):
                        self.deployable.append(returning)
                    self.drones[returning].deployed = False
        elif self.ticks_remaining > 15:
            for landing_zone in Zerg.landing_clear:
                if Zerg.map_viable[landing_zone] and Zerg.landing_clear[landing_zone] is True and self.deployable:
                    deploy = self.deployable.pop()
                    result = "DEPLOY {} {}".format(deploy, landing_zone)
                    Zerg.landing_clear[self.drones[deploy].map] = False
                    self.drones[deploy].map = landing_zone
                    self.drones[deploy].deployed = True
                    return result
                #elif Zerg.landing_clear[landing_zone] is False:
                    #print("Landing for {} is not clear.".format(landing_zone))
                elif Zerg.landing_clear[landing_zone] is True and Zerg.minerals[landing_zone] and self.mining_units:
                    gatherer = self.mining_units.pop()
                    result = "DEPLOY {} {}".format(gatherer, landing_zone)
                    self.drones[gatherer].map = landing_zone
                    mineral = Zerg.minerals[landing_zone].pop()
                    path = a_star_search(
                            Zerg.map_graphs[landing_zone], Zerg.starting_locations[landing_zone],
                            mineral)
                    path.pop(0)
                    self.drones[gatherer].commands.update({'Mine': path})
                    Zerg.landing_clear[self.drones[gatherer].map] = False
                    self.drones[gatherer].deployed = True
                    return result

        #self.update_dashboard(self.dashboard, result)


        return result


    def update_dashboard(self, dashboard, result):
        for dash in range(3):
            self.map_dashboards[dash].log.config(state=tkinter.NORMAL)
            self.map_dashboards[dash].log.delete('1.0', tkinter.END)
            self.map_dashboards[dash].log.config(state=tkinter.DISABLED)
        for drone_id, drone in self.drones.items():
            if drone.deployed is True:
                drone_string = "{}({}): {}".format(
                        drone_id, drone.map, drone.commands)
                self.map_dashboards[drone.map].log.config(state=tkinter.NORMAL)
                self.map_dashboards[drone.map].log.insert(
                        tkinter.END, drone_string)
                self.map_dashboards[drone.map].log.insert(tkinter.END, "\n")
                self.map_dashboards[drone.map].log.see(tkinter.END)
                self.map_dashboards[drone.map].log.config(
                        state=tkinter.DISABLED)
                self.map_dashboards[drone.map].log.grid()

        self.dashboard.log.config(state=tkinter.NORMAL)
        self.dashboard.log.delete('1.0', tkinter.END)
        self.dashboard.log.insert(tkinter.END, result)
        self.dashboard.log.insert(tkinter.END, "\n")
        self.dashboard.log.see(tkinter.END)
        self.dashboard.log.config(state=tkinter.DISABLED)

    def update_display(self, drone, north, south, east, west):
        x_coord = drone.context.x
        y_coord = drone.context.y
        print_north = Zerg.map_display[drone.map][north[1]][north[0]]
        print_south = Zerg.map_display[drone.map][south[1]][south[0]]
        print_east = Zerg.map_display[drone.map][east[1]][east[0]]
        print_west = Zerg.map_display[drone.map][west[1]][west[0]]
        print_zerg = Zerg.map_display[drone.map][y_coord][x_coord]

        '''
        TILE_MAP = {
            '#': 'gray50',
            '~': 'lawn green'
        }
        print_north.config(bg=TILE_MAP[drone.context.north])
        print_north.config(bg=TILE_MAP[drone.context.north])
        print_north.config(bg=TILE_MAP[drone.context.north])
        print_north.config(bg=TILE_MAP[drone.context.north])
        '''

        if drone.context.north == "#":
            print_north.config(bg='gray50')
        elif drone.context.north == "~":
            print_north.config(bg='lawn green')
        elif drone.context.north == "*":
            print_north.config(bg='blue')
        elif drone.context.north == "_":
            print_north.config(bg='gold')
        elif drone.context.north == " ":
            print_north.config(bg='grey60')

        if drone.context.south == "#":
            print_south.config(bg='gray50')
        elif drone.context.south == "~":
            print_south.config(bg='lawn green')
        elif drone.context.south == "*":
            print_south.config(bg='blue')
        elif drone.context.south == "_":
            print_south.config(bg='gold')
        elif drone.context.south == " ":
            print_south.config(bg='grey60')

        if drone.context.east == "#":
            print_east.config(bg='gray50')
        elif drone.context.east == "~":
            print_east.config(bg='lawn green')
        elif drone.context.east == "*":
            print_east.config(bg='blue')
        elif drone.context.east == "_":
            print_east.config(bg='gold')
        elif drone.context.east == " ":
            print_east.config(bg='grey60')

        if drone.context.west == "#":
            print_west.config(bg='gray50')
        elif drone.context.west == "~":
            print_west.config(bg='lawn green')
        elif drone.context.west == "*":
            print_west.config(bg='blue')
        elif drone.context.west == "_":
            print_west.config(bg='gold')
        elif drone.context.west == " ":
            print_west.config(bg='grey60')

        print_north.grid(row=north[1], column=north[0], sticky='NW')
        print_south.grid(row=south[1], column=south[0], sticky='NW')
        print_east.grid(row=east[1], column=east[0], sticky='NW')
        print_west.grid(row=west[1], column=west[0], sticky='NW')
        print_zerg.config(bg='magenta2')

    def get_drone_info(self, drone):
        path = None
        tile = (drone.context.x, drone.context.y)
        north = (drone.context.x, int(drone.context.y) + 1)
        south = (drone.context.x, int(drone.context.y) - 1)
        east = (int(drone.context.x) + 1, drone.context.y)
        west = (int(drone.context.x) - 1, drone.context.y)
        drone.last_tile = tile

        self.update_display(drone, north, south, east, west)

        Zerg.map_graphs[drone.map].visited.add(tile)


        if drone.context.north == "#":
            Zerg.map_graphs[drone.map].walls.append(north)
        if drone.context.south == "#":
            Zerg.map_graphs[drone.map].walls.append(south)
        if drone.context.east == "#":
            Zerg.map_graphs[drone.map].walls.append(east)
        if drone.context.west == "#":
            Zerg.map_graphs[drone.map].walls.append(west)

        if drone.context.north == "~":
            Zerg.map_graphs[drone.map].acid.append(north)
        if drone.context.south == "~":
            Zerg.map_graphs[drone.map].acid.append(south)
        if drone.context.east == "~":
            Zerg.map_graphs[drone.map].acid.append(east)
        if drone.context.west == "~":
            Zerg.map_graphs[drone.map].acid.append(west)


#        if tile == Zerg.starting_locations[drone.map] and 'Return' in drone.commands:
#            print("OVerlord RETURNING")
#            Zerg.returns.append(id(drone))
#            drone.depoyed = False
#            return


        if isinstance(drone, Miner) and 'Mine' not in drone.commands:
            path = a_star_search(
                    Zerg.map_graphs[drone.map], tile,
                    Zerg.starting_locations[drone.map])
            path.pop(0)
            drone.commands.update({"Return": path})
        elif isinstance(drone, Scout) and Zerg.map_graphs[drone.map].unvisited:
            unexplored = Zerg.map_graphs[drone.map].unvisited.pop()
            path = a_star_search(
                    Zerg.map_graphs[drone.map], tile,
                    unexplored)
            path.pop(0)
            drone.commands.update({"Discover": path})
#        elif 'Return' not in drone.commands:
#            path = a_star_search(
#                    Zerg.map_graphs[drone.map], tile,
#                    Zerg.starting_locations[drone.map])
#            path.pop(0)
#            drone.commands.update({"Return": path})

        elif isinstance(drone, Scout):
            drone.commands.update({"Discover": None})
        if len(Zerg.map_graphs[drone.map].unvisited) == 0:
            print("Out of nodes")
            Zerg.map_viable[drone.map] = False
        else:
            Zerg.map_viable[drone.map] = True


class Drone(Zerg):

    last_bias = 0

    def __init__(self):
        super().__init__(40)


    def action(self, context):
        pass

class Scout(Drone):

    last_bias = 0

    def __init__(self):
        super().__init__()
        self.moves = 1
        self.last_tile = None
        self.capacity = 5
        self.health = 50
        self.carry = 0
        self.steps = 0
        self.map = -1
        self.context = None
        self.bias = Scout.last_bias % 4
        self.deployed = False
        Scout.last_bias += 1
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
        tile = (context.x, context.y)
        north = (context.x, int(context.y) + 1)
        south = (context.x, int(context.y) - 1)
        east = (int(context.x) + 1, context.y)
        west = (int(context.x) - 1, context.y)

        Zerg.map_graphs[self.map].visited.add(tile)
        Zerg.map_graphs[self.map].unvisited = sorted(
                list(set(Zerg.map_graphs[self.map].unvisited).difference(
                    Zerg.map_graphs[self.map].visited)))

        if context.north != "#":
            Zerg.map_graphs[self.map].unvisited.append(north)
        if context.south != "#":
            Zerg.map_graphs[self.map].unvisited.append(south)
        if context.east != "#":
            Zerg.map_graphs[self.map].unvisited.append(east)
        if context.west != "#":
            Zerg.map_graphs[self.map].unvisited.append(west)

        if context.north == "#":
            Zerg.map_graphs[self.map].walls.append(north)
        if context.south == "#":
            Zerg.map_graphs[self.map].walls.append(south)
        if context.east == "#":
            Zerg.map_graphs[self.map].walls.append(east)
        if context.west == "#":
            Zerg.map_graphs[self.map].walls.append(west)

        if context.north == "*":
            Zerg.minerals[self.map].add(north)
        if context.south == "*":
            Zerg.minerals[self.map].add(south)
        if context.east == "*":
            Zerg.minerals[self.map].add(east)
        if context.west == "*":
            Zerg.minerals[self.map].add(west)

        #print("TEST: {} {} {}".format(id(self), self.map, (context.x, context.y)))
        #print("Minerals: ", Zerg.minerals)
        #print("Carry: {}".format(self.carry))
        #print("Command: ", self.commands)
        #print("Landings: ", Zerg.starting_locations)
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        neighbors = {0: context.north, 1: context.south,
                     2: context.east, 3: context.west}
        if self.deployed is True and self.map not in Zerg.starting_locations:
            #print("Updating starting loc")
            Zerg.starting_locations.update({self.map: tile})
            Zerg.map_graphs[self.map].visited.add(tile)
        if (context.x, context.y) == Zerg.starting_locations[self.map]:
            Zerg.landing_clear[self.map] = False
        else:
            Zerg.landing_clear[self.map] = True

        self.steps += 1
        if self.steps % 25 == 0:
            self.bias = random.randint(0, 3)
        self.context = context
        goto = "Center"
        if self.commands:
            if 'Discover' in self.commands:
                if self.commands['Discover']:
                    to_tile = self.commands['Discover'].pop(0)
                    if to_tile == (context.x, context.y)\
                            and len(self.commands['Discover']) > 0:
                        to_tile = self.commands['Discover'].pop(0)
                    goto = self.get_direction(to_tile, (context.x, context.y))

                self.commands.pop('Discover')
                allowed = " ~"
                if self.bias == 0:
                    return Scout.north_bias(
                            self.last_tile, context, directions, allowed)
                elif self.bias == 1:
                    return Scout.south_bias(
                            self.last_tile, context, directions, allowed)
                elif self.bias == 2:
                    return Scout.east_bias(
                            self.last_tile, context, directions, allowed)
                elif self.bias == 3:
                    return Scout.west_bias(
                            self.last_tile, context, directions, allowed)

        return goto

    def north_bias(last_tile, context, directions, allowed):
        if context.north in allowed and context.y + 1 != last_tile[1]:
            return directions.get(0)
        elif context.east in allowed and context.x + 1 != last_tile[0]:
            return directions.get(2)
        elif context.south in allowed and context.y - 1 != last_tile[1]:
            return directions.get(1)
        elif context.west in allowed and context.x - 1 != last_tile[0]:
            return directions.get(3)
        else:
            return "CENTER"

    def south_bias(last_tile, context, directions, allowed):
        if context.south in allowed and context.y - 1 != last_tile[1]:
            return directions.get(1)
        elif context.west in allowed and context.x - 1 != last_tile[0]:
            return directions.get(3)
        elif context.north in allowed and context.y + 1 != last_tile[1]:
            return directions.get(0)
        elif context.east in allowed and context.x + 1 != last_tile[0]:
            return directions.get(2)
        else:
            return "CENTER"

    def east_bias(last_tile, context, directions, allowed):
        if context.east in allowed and context.x + 1 != last_tile[0]:
            return directions.get(2)
        elif context.north in allowed and context.y + 1 != last_tile[1]:
            return directions.get(0)
        elif context.west in allowed and context.x - 1 != last_tile[0]:
            return directions.get(3)
        elif context.south in allowed and context.y - 1 != last_tile[1]:
            return directions.get(1)
        else:
            return "CENTER"

    def west_bias(last_tile, context, directions, allowed):
        if context.west in allowed and context.x - 1 != last_tile[0]:
            return directions.get(3)
        elif context.south in allowed and context.y - 1 != last_tile[1]:
            return directions.get(1)
        elif context.east in allowed and context.x + 1 != last_tile[0]:
            return directions.get(2)
        elif context.north in allowed and context.y + 1 != last_tile[1]:
            return directions.get(0)
        else:
            return "CENTER"



class Miner(Drone):

    last_bias = 0

    def __init__(self):
        super().__init__()
        self.moves = 1
        self.last_tile = None
        self.capacity = 15
        self.health = 190
        self.carry = 0
        self.steps = 0
        self.map = -1
        self.context = None
        self.deployed = False
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
        tile = (context.x, context.y)
        north = (context.x, int(context.y) + 1)
        south = (context.x, int(context.y) - 1)
        east = (int(context.x) + 1, context.y)
        west = (int(context.x) - 1, context.y)

        Zerg.map_graphs[self.map].visited.add(tile)
        Zerg.map_graphs[self.map].unvisited = sorted(
                list(set(Zerg.map_graphs[self.map].unvisited).difference(
                    Zerg.map_graphs[self.map].visited)))

        if context.north != "#":
            Zerg.map_graphs[self.map].unvisited.append(north)
        if context.south != "#":
            Zerg.map_graphs[self.map].unvisited.append(south)
        if context.east != "#":
            Zerg.map_graphs[self.map].unvisited.append(east)
        if context.west != "#":
            Zerg.map_graphs[self.map].unvisited.append(west)

        #print("TEST: {} {} {}".format(id(self), self.map, (context.x, context.y)))
        #print("Carry: {}".format(self.carry))
        #print("Commad: ", self.commands)
        #print("Landings: ", Zerg.starting_locations)
        directions = {0: 'NORTH', 1: 'SOUTH', 2: 'EAST', 3: 'WEST'}
        neighbors = {'NORTH': context.north, 'SOUTH': context.south,
                     'EAST': context.east, 'WEST': context.west,
                     'Center': ""}
        if (context.x, context.y) == Zerg.starting_locations[self.map]:
            Zerg.landing_clear[self.map] = False
        else:
            Zerg.landing_clear[self.map] = True

        self.steps += 1
        self.context = context
        goto = "Center"
        if self.carry < self.capacity:
            if context.north == "*" and self.carry < self.capacity:
                self.carry += 1
                return directions.get(0)
            elif context.south == "*" and self.carry < self.capacity:
                self.carry += 1
                return directions.get(1)
            elif context.east == "*" and self.carry < self.capacity:
                self.carry += 1
                return directions.get(2)
            elif context.west == "*" and self.carry < self.capacity:
                self.carry += 1
                return directions.get(3)
        if self.commands:
            if 'Mine' in self.commands:
                if len(self.commands['Mine']) > 0:
                    goto = self.get_direction(
                        self.commands['Mine'].pop(0), (context.x, context.y))
                else:
                    self.commands.pop('Mine')

            elif 'Return' in self.commands:
                if len(self.commands['Return']) > 0:
                    to_tile = self.commands['Return'].pop(0)
                    if to_tile == (context.x, context.y)\
                            and len(self.commands['Return']) > 0:
                        to_tile = self.commands['Return'].pop(0)
                    goto = self.get_direction(to_tile, (context.x, context.y))

                elif tile == Zerg.starting_locations[self.map]:
                    Zerg.returns.append(id(self))
                    self.commands.pop('Return')
                    self.carry = 0
     
        if goto and neighbors[goto] == "#":
            if 'Mine' in self.commands:
                Zerg.minerals[self.map].add(self.commands['Mine'][-1])
            self.commands = dict()
        if goto and neighbors[goto] == "_":
            Zerg.returns.append(id(self))
            Zerg.landing_clear[self.map] = False
        return goto


class Dashboard(tkinter.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x200+300+200")
        self.title("Overlord's Dashboard")
        self.log = tkinter.Text(self, height=10,  width=30)
        self.log.pack()
