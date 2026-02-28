import random

class Tile:
    def __init__(self, r, c, total_r):
        self.r = r
        self.c = c
        self.total_r = total_r
        
        self.is_start_pt = False
        self.is_target_pt = False
        self.is_blocked = False
        self.part_of_path = False
        self.is_explored = False
        self.is_boundary = False
        
        self.prev_tile = None
        self.cost_g = float("inf")
        self.cost_h = float("inf")
        self.cost_f = float("inf")

    def clear_all(self):
        self.is_start_pt = False
        self.is_target_pt = False
        self.is_blocked = False
        self.part_of_path = False
        self.is_explored = False
        self.is_boundary = False
        self.clear_routing()

    def clear_routing(self):
        self.prev_tile = None
        self.cost_g = float("inf")
        self.cost_h = float("inf")
        self.cost_f = float("inf")
        if not self.is_start_pt and not self.is_target_pt and not self.is_blocked:
            self.part_of_path = False
            self.is_explored = False
            self.is_boundary = False

    def mark_start(self):
        self.clear_all()
        self.is_start_pt = True

    def mark_target(self):
        self.clear_all()
        self.is_target_pt = True

    def mark_blocked(self):
        self.clear_all()
        self.is_blocked = True

    def mark_path(self):
        self.part_of_path = True
        
    def mark_explored(self):
        self.is_explored = True

    def mark_boundary(self):
        self.is_boundary = True

    def fetch_adjacent(self, matrix, diag_allowed=False):
        adj = []
        tot_r = len(matrix)
        tot_c = len(matrix[0]) if tot_r > 0 else 0
        
        if self.r < tot_r - 1 and not matrix[self.r + 1][self.c].is_blocked:
            adj.append(matrix[self.r + 1][self.c])
        if self.r > 0 and not matrix[self.r - 1][self.c].is_blocked:
            adj.append(matrix[self.r - 1][self.c])
        if self.c < tot_c - 1 and not matrix[self.r][self.c + 1].is_blocked:
            adj.append(matrix[self.r][self.c + 1])
        if self.c > 0 and not matrix[self.r][self.c - 1].is_blocked:
            adj.append(matrix[self.r][self.c - 1])

        if diag_allowed:
            if self.r < tot_r - 1 and self.c < tot_c - 1 and not matrix[self.r + 1][self.c + 1].is_blocked:
                adj.append(matrix[self.r + 1][self.c + 1])
            if self.r < tot_r - 1 and self.c > 0 and not matrix[self.r + 1][self.c - 1].is_blocked:
                adj.append(matrix[self.r + 1][self.c - 1])
            if self.r > 0 and self.c < tot_c - 1 and not matrix[self.r - 1][self.c + 1].is_blocked:
                adj.append(matrix[self.r - 1][self.c + 1])
            if self.r > 0 and self.c > 0 and not matrix[self.r - 1][self.c - 1].is_blocked:
                adj.append(matrix[self.r - 1][self.c - 1])

        return adj

class MapEnvironment:
    def __init__(self, r_count, c_count):
        self.r_count = r_count
        self.c_count = c_count
        self.matrix = self.build_matrix(r_count, c_count)
        self.origin = None
        self.destination = None

    def build_matrix(self, r_count, c_count):
        return [[Tile(i, j, r_count) for j in range(c_count)] for i in range(r_count)]

    def place_origin(self, r, c):
        if self.origin:
            self.origin.clear_all()
        self.origin = self.matrix[r][c]
        self.origin.mark_start()

    def place_destination(self, r, c):
        if self.destination:
            self.destination.clear_all()
        self.destination = self.matrix[r][c]
        self.destination.mark_target()

    def wipe_routing(self):
        for row in self.matrix:
            for tile in row:
                tile.clear_routing()

    def wipe_board(self):
        for row in self.matrix:
            for tile in row:
                tile.clear_all()
        self.origin = None
        self.destination = None

    def populate_obstacles(self, density=0.3):
        for row in self.matrix:
            for tile in row:
                if not tile.is_start_pt and not tile.is_target_pt:
                    if random.random() < density:
                        tile.mark_blocked()
                    else:
                        tile.clear_all()

    def create_dynamic_barrier(self, prob=0.05):
        if random.random() < prob:
            free_tiles = []
            for row in self.matrix:
                for t in row:
                    if not t.is_start_pt and not t.is_target_pt and \
                       not t.is_blocked and not t.part_of_path:
                         free_tiles.append(t)
            
            if free_tiles:
                selection = random.choice(free_tiles)
                selection.mark_blocked()
                return selection
        return None
