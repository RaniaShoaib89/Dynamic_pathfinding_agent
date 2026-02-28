import math
from queue import PriorityQueue

class DistanceMetrics:
    @staticmethod
    def calc_manhattan(pt_a, pt_b):
        return abs(pt_a[0] - pt_b[0]) + abs(pt_a[1] - pt_b[1])

    @staticmethod
    def calc_euclidean(pt_a, pt_b):
        return math.sqrt((pt_a[0] - pt_b[0])**2 + (pt_a[1] - pt_b[1])**2)

    @staticmethod
    def resolve_metric(name):
        return DistanceMetrics.calc_euclidean if name == "Euclidean" else DistanceMetrics.calc_manhattan

class PathFinders:
    @staticmethod
    def _trace_back(curr_tile):
        route = []
        while curr_tile.prev_tile is not None:
            route.append(curr_tile)
            curr_tile = curr_tile.prev_tile
        route.reverse()
        for t in route:
            if not t.is_start_pt and not t.is_target_pt:
                t.mark_path()
        return route

    @staticmethod
    def search_astar(environment, heuristic_fn, run_diagonal=False, source_override=None):
        source = source_override if source_override else environment.origin
        target = environment.destination
        
        if not source or not target:
            yield {'status': 'error', 'message': 'Origin/Destination missing'}
            return

        seq = 0
        p_queue = PriorityQueue()
        p_queue.put((0, seq, source))
        
        source.cost_g = 0
        source.cost_f = heuristic_fn((source.r, source.c), (target.r, target.c))
        
        q_hash = {source}
        visited_count = 0

        while not p_queue.empty():
            curr = p_queue.get()[2]
            q_hash.remove(curr)

            if curr == target:
                final_route = PathFinders._trace_back(curr)
                yield {'status': 'success', 'path': final_route, 'nodes_visited': visited_count, 'cost': target.cost_g}
                return

            for adj in curr.fetch_adjacent(environment.matrix, run_diagonal):
                new_g = curr.cost_g + 1 

                if new_g < adj.cost_g:
                    adj.prev_tile = curr
                    adj.cost_g = new_g
                    adj.cost_h = heuristic_fn((adj.r, adj.c), (target.r, target.c))
                    adj.cost_f = adj.cost_g + adj.cost_h
                    
                    if adj not in q_hash:
                        seq += 1
                        p_queue.put((adj.cost_f, seq, adj))
                        q_hash.add(adj)
                        if not adj.is_target_pt and not adj.is_start_pt:
                            adj.mark_boundary()
            
            visited_count += 1
            if curr != source:
                curr.mark_explored()
                
            yield {'status': 'running', 'nodes_visited': visited_count}

        yield {'status': 'no_path', 'nodes_visited': visited_count}

    @staticmethod
    def search_greedy(environment, heuristic_fn, run_diagonal=False, source_override=None):
        source = source_override if source_override else environment.origin
        target = environment.destination
        
        if not source or not target:
            yield {'status': 'error', 'message': 'Origin/Destination missing'}
            return

        seq = 0
        p_queue = PriorityQueue()
        p_queue.put((0, seq, source))
        
        source.cost_h = heuristic_fn((source.r, source.c), (target.r, target.c))
        
        q_hash = {source}
        visited_count = 0

        while not p_queue.empty():
            curr = p_queue.get()[2]
            q_hash.remove(curr)

            if curr == target:
                final_route = PathFinders._trace_back(curr)
                yield {'status': 'success', 'path': final_route, 'nodes_visited': visited_count, 'cost': len(final_route)}
                return

            for adj in curr.fetch_adjacent(environment.matrix, run_diagonal):
                if adj.prev_tile is None and adj != source: 
                    adj.prev_tile = curr
                    adj.cost_h = heuristic_fn((adj.r, adj.c), (target.r, target.c))
                    
                    if adj not in q_hash:
                        seq += 1
                        p_queue.put((adj.cost_h, seq, adj))
                        q_hash.add(adj)
                        if not adj.is_target_pt and not adj.is_start_pt:
                            adj.mark_boundary()
            
            visited_count += 1
            if curr != source:
                curr.mark_explored()
                
            yield {'status': 'running', 'nodes_visited': visited_count}

        yield {'status': 'no_path', 'nodes_visited': visited_count}
