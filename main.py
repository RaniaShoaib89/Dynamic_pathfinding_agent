import pygame
import pygame_gui
import time
from grid import MapEnvironment
from algorithms import DistanceMetrics, PathFinders

THEME_COLORS = {
    'BG_MAIN': (240, 240, 240),     
    'CELL_DEFAULT': (255, 255, 255),          
    'CELL_BLOCK': (0, 0, 0),         
    'CELL_ORIGIN': (0, 200, 0),        
    'CELL_DEST': (200, 0, 0),          
    'CELL_ROUTE': (255, 215, 0),        
    'CELL_MARGIN': (173, 216, 230),    
    'CELL_SEEN': (220, 220, 220),     
    'NAVIGATOR': (255, 0, 255),       
}

class InterfaceBuilder:
    def __init__(self, manager, p_width, grid_offset_x):
        self.mgr = manager
        rect = pygame.Rect(grid_offset_x + 20, 20, p_width - grid_offset_x - 40, 728)
        
        y_pos = 20
        self.l_algo = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(rect.x, y_pos, 200, 30), text="Algorithm", manager=self.mgr)
        y_pos += 35
        self.drop_algo = pygame_gui.elements.UIDropDownMenu(
            options_list=['A* Search', 'Greedy Best-First Build'],
            starting_option='A* Search',
            relative_rect=pygame.Rect(rect.x, y_pos, 200, 30),
            manager=self.mgr
        )
        
        y_pos += 50
        self.l_heur = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(rect.x, y_pos, 200, 30), text="Heuristic", manager=self.mgr)
        y_pos += 35
        self.drop_heur = pygame_gui.elements.UIDropDownMenu(
            options_list=['Manhattan', 'Euclidean'],
            starting_option='Manhattan',
            relative_rect=pygame.Rect(rect.x, y_pos, 200, 30),
            manager=self.mgr
        )
        
        y_pos += 50
        self.b_maze = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect.x, y_pos, 200, 40), text='Generate Maze (30%)', manager=self.mgr)
        
        y_pos += 50
        self.b_execute = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect.x, y_pos, 200, 40), text='Start Search', manager=self.mgr)
        
        y_pos += 50
        self.b_wipe_all = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect.x, y_pos, 200, 40), text='Reset Grid', manager=self.mgr)
        
        y_pos += 50
        self.b_wipe_route = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect.x, y_pos, 200, 40), text='Clear Path', manager=self.mgr)
        
        y_pos += 60
        self.b_toggle_dyn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect.x, y_pos, 200, 40), text='Dynamic Mode: OFF', manager=self.mgr)

        bottom_y = 620
        self.lbl_head = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(200, bottom_y, 200, 30), text="Metrics:", manager=self.mgr)
        
        self.disp_nodes = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(150, bottom_y + 35, 300, 30), text="Nodes Visited: 0", manager=self.mgr)
        
        self.disp_cost = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(150, bottom_y + 70, 300, 30), text="Path Cost: 0", manager=self.mgr)
        
        self.disp_time = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(150, bottom_y + 105, 300, 30), text="Execution Time: 0 ms", manager=self.mgr)

    def refresh_stats(self, explored, expense, ms_time):
        self.disp_nodes.set_text(f"Nodes Visited: {explored}")
        self.disp_cost.set_text(f"Path Cost: {expense}")
        self.disp_time.set_text(f"Execution Time: {ms_time:.2f} ms")


class PathfindingSimulator:
    def __init__(self, w=1024, h=768):
        pygame.init()
        self.screen_w = w
        self.screen_h = h
        self.surface = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Smart Navigator Probe")
        
        self.board_dim = 600
        self.row_cnt = 30
        self.col_cnt = 30
        self.tile_w = self.board_dim // self.col_cnt
        self.tile_h = self.board_dim // self.row_cnt
        
        self.env = MapEnvironment(self.row_cnt, self.col_cnt)
        
        self.is_active = True
        self.is_calculating = False
        self.step_generator = None
        self.t_start = 0
        self.t_elapsed = 0
        self.stat_explored = 0
        self.stat_expense = 0
        self.active_route = []
        
        self.past_path = []
        self.past_explored = 0
        self.past_expense = 0
        
        self.realtime_flag = False
        self.probe_tile = None
        self.probe_idx = 0
        self.t_last_step = 0
        self.step_interval = 0.2 
        
        # UI Setup with basic standard pygame_gui default
        self.ui_mgr = pygame_gui.UIManager((w, h), 'light_theme.json')
        self.interface = InterfaceBuilder(self.ui_mgr, w, self.board_dim)

    def render_entities(self):
        for r_idx in range(self.row_cnt):
            for c_idx in range(self.col_cnt):
                t = self.env.matrix[r_idx][c_idx]
                clr = THEME_COLORS['CELL_DEFAULT']
                if t.is_start_pt:
                    clr = THEME_COLORS['CELL_ORIGIN']
                elif t.is_target_pt:
                    clr = THEME_COLORS['CELL_DEST']
                elif t.is_blocked:
                    clr = THEME_COLORS['CELL_BLOCK']
                elif t.part_of_path:
                    clr = THEME_COLORS['CELL_ROUTE']
                elif t.is_boundary:
                    clr = THEME_COLORS['CELL_MARGIN']
                elif t.is_explored:
                    clr = THEME_COLORS['CELL_SEEN']
                
                pad = 2
                poly = (t.c * self.tile_w + pad, 
                        t.r * self.tile_h + pad, 
                        self.tile_w - pad * 2, 
                        self.tile_h - pad * 2)
                
                pygame.draw.rect(self.surface, clr, poly)

        if self.probe_tile:
            pygame.draw.circle(self.surface, THEME_COLORS['NAVIGATOR'], 
                             (self.probe_tile.c * self.tile_w + self.tile_w // 2, 
                              self.probe_tile.r * self.tile_h + self.tile_h // 2), 
                             self.tile_w // 2 - 2)

    def screen_to_grid(self, coord):
        y, x = coord
        return y // self.tile_w, x // self.tile_h

    def launch(self):
        clk = pygame.time.Clock()
        self.env.place_origin(2, 2)
        self.env.place_destination(self.row_cnt - 3, self.col_cnt - 3)

        while self.is_active:
            dt = clk.tick(60) / 1000.0
            
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    self.is_active = False
                
                self.ui_mgr.process_events(evt)
                
                if evt.type == pygame_gui.UI_BUTTON_PRESSED:
                    if evt.ui_element == self.interface.b_execute:
                        self.trigger_search()
                    elif evt.ui_element == self.interface.b_wipe_all:
                        self.env.wipe_board()
                        self.env.place_origin(2, 2)
                        self.env.place_destination(self.row_cnt - 3, self.col_cnt - 3)
                        self.is_calculating = False
                        self.step_generator = None
                        self.probe_tile = None
                        self.past_path = []
                        self.active_route = []
                    elif evt.ui_element == self.interface.b_wipe_route:
                        self.env.wipe_routing()
                        self.is_calculating = False
                        self.step_generator = None
                        self.probe_tile = None
                        self.past_path = []
                        self.active_route = []
                    elif evt.ui_element == self.interface.b_maze:
                        self.env.wipe_routing()
                        self.env.populate_obstacles(0.3)
                        self.past_path = []
                        self.active_route = []
                    elif evt.ui_element == self.interface.b_toggle_dyn:
                        self.realtime_flag = not self.realtime_flag
                        self.interface.b_toggle_dyn.set_text('Dynamic Mode: ON' if self.realtime_flag else 'Dynamic Mode: OFF')

            if pygame.mouse.get_pressed()[0] and not self.is_calculating:  
                loc = pygame.mouse.get_pos()
                if loc[0] < self.board_dim and loc[1] < self.board_dim:
                    r_val, c_val = self.screen_to_grid((loc[1], loc[0]))
                    if 0 <= r_val < self.row_cnt and 0 <= c_val < self.col_cnt:
                        selected = self.env.matrix[r_val][c_val]
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_s]:
                            self.env.place_origin(r_val, c_val)
                            self.past_path = []
                        elif keys[pygame.K_e]:
                            self.env.place_destination(r_val, c_val)
                            self.past_path = []
                        elif selected != self.env.origin and selected != self.env.destination:
                            selected.mark_blocked()
                            if self.realtime_flag and self.probe_tile and selected in self.active_route[self.probe_idx:]:
                                print("User Interference detected! Recalculating...")
                                self.past_path = self.active_route[:self.probe_idx + 1]
                                self.past_explored = self.stat_explored
                                self.past_expense = len(self.past_path)
                                self.trigger_search(override_source=self.probe_tile)
            elif pygame.mouse.get_pressed()[2] and not self.is_calculating:
                loc = pygame.mouse.get_pos()
                if loc[0] < self.board_dim and loc[1] < self.board_dim:
                    r_val, c_val = self.screen_to_grid((loc[1], loc[0]))
                    if 0 <= r_val < self.row_cnt and 0 <= c_val < self.col_cnt:
                        selected = self.env.matrix[r_val][c_val]
                        if selected != self.env.origin and selected != self.env.destination:
                             selected.clear_all()

            self.ui_mgr.update(dt)

            if self.is_calculating and self.step_generator:
                try:
                    res = next(self.step_generator)
                    if 'nodes_visited' in res:
                        self.stat_explored = self.past_explored + res['nodes_visited']
                    
                    if res['status'] in ('success', 'no_path', 'error'):
                        self.t_elapsed = (time.time() - self.t_start) * 1000
                        self.is_calculating = False
                        if res['status'] == 'success':
                            self.stat_expense = self.past_expense + res['cost']
                            self.active_route = self.past_path + res['path']
                            print("Routing successful!")
                            if self.realtime_flag:
                                start_idx = len(self.past_path) - 1 if self.past_path else 0
                                self.init_probe_transit(start_idx=max(0, start_idx))
                        else:
                            print("Routing failed.")
                    self.interface.refresh_stats(self.stat_explored, self.stat_expense, self.t_elapsed)
                except StopIteration:
                    self.is_calculating = False
            
            if not self.is_calculating and self.probe_tile and self.realtime_flag:
                self.advance_probe()

            self.surface.fill(THEME_COLORS['BG_MAIN'])
            self.render_entities()
            self.ui_mgr.draw_ui(self.surface)
            pygame.display.flip()

        pygame.quit()

    def trigger_search(self, override_source=None):
        if override_source is None:
            self.past_path = []
            self.past_explored = 0
            self.past_expense = 0
            
        self.env.wipe_routing()
        
        for t in self.past_path:
            t.mark_path()
            
        self.is_calculating = True
        self.t_start = time.time()
        self.t_elapsed = 0
        self.stat_explored = self.past_explored
        self.stat_expense = self.past_expense
        self.active_route = []
        self.probe_tile = override_source
        
        algo_choice = self.interface.drop_algo.selected_option
        h_choice = self.interface.drop_heur.selected_option
        fn_h = DistanceMetrics.resolve_metric(h_choice)
        
        if algo_choice == 'A* Search':
            self.step_generator = PathFinders.search_astar(self.env, fn_h, source_override=override_source)
        else:
            self.step_generator = PathFinders.search_greedy(self.env, fn_h, source_override=override_source)
            
        self.interface.refresh_stats(self.stat_explored, self.stat_expense, self.t_elapsed)

    def init_probe_transit(self, start_idx=0):
        self.probe_idx = start_idx
        if len(self.active_route) > self.probe_idx:
            self.probe_tile = self.active_route[self.probe_idx]
            self.t_last_step = time.time()
        else:
            self.probe_tile = None

    def advance_probe(self):
        t_now = time.time()
        if t_now - self.t_last_step > self.step_interval:
            obstacle = self.env.create_dynamic_barrier(prob=0.03)
            
            if obstacle and obstacle in self.active_route[self.probe_idx:]:
                print("Interference detected! Recalculating...")
                self.past_path = self.active_route[:self.probe_idx + 1]
                self.past_explored = self.stat_explored
                self.past_expense = len(self.past_path)
                self.trigger_search(override_source=self.probe_tile)
                return 
                
            self.probe_idx += 1
            if self.probe_idx < len(self.active_route):
                self.probe_tile = self.active_route[self.probe_idx]
                self.t_last_step = t_now
            else:
                print("Destination arrived.")
                self.probe_tile = None 
            
if __name__ == "__main__":
    app_instance = PathfindingSimulator()
    app_instance.launch()
