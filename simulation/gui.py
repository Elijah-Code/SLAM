import pygame
import random
import sys
import time
from functools import partial
from ops import get_surrounding_walls
from config import *
from environment import Robot, Trash, Wall
from pygame.surfarray import blit_array

def convert_to_rect(sprite, pos):
    """
    Convert sprite to rectangle
    """
    rect = sprite.get_rect()
    rect.x = pos[0]
    rect.y = pos[1] 

    return rect

class Rect:
    def __init__(self, sprite, pos):
        self.rect = convert_to_rect(sprite, pos)

class ScreenManager:
    def __init__(self, screen):
        self.win_size = WINDOW_SIZE
        self.screen = screen
        self.surfaces = {
            "left": pygame.Surface((WINDOW_SIZE[0]//2, WINDOW_SIZE[1])),
            "right": pygame.Surface((WINDOW_SIZE[0]//2, WINDOW_SIZE[1]))
        }

        self.elems = {
            "left": [],
            "right": []
        }


    def add_elem(self, elem, surface, layer=0):
        """
        Add an element on the screen
        param elem: PygameElement object
            Object to add
        param surface: str
            Name of the surface, need to be in self.surface, can be chained in this format: surface1-surface2-surface3
        param layer int
            Layer number (top ones are higher ones)
        """
        surfaces = surface.split('-')
        for surface in surfaces:
            assert surface in self.surfaces.keys(), f"Surface {surface} doesn't exist"
            self.elems[surface].append((elem, layer))
        
        self.elems[surface].sort(key=lambda e: e[1])

    def blitarray_right(self, array):
        blit_array(self.surfaces['right'], array)

    def del_element(self, elem, surface):
        surfaces = surface.split('-')
        for surface in surfaces: # TODO Keep trace of objs
            assert surface in self.surfaces.keys(), f"Surface {surface} doesn't exist"
            for e in self.elems[surface]:
                if e[0] == elem:
                    self.elems[surface].remove(e)

    def draw(self):

        self.screen.blit(self.surfaces['left'], (0,0))
        self.screen.blit(self.surfaces['right'], (WINDOW_SIZE[0]//2, 0))
        self.surfaces['left'].fill(WHITE)
        self.surfaces['right'].fill(BLACK)
        for surface_name, elems in self.elems.items():
            surface = self.surfaces[surface_name]
            for elem, layer in elems:
                elem.draw(surface)


class MovingManager:
    def __init__(self):
        self.elems = {}
        self.elems_states = {}  
        self.elems_funcs = {}
        self.elems_constraints = {}
        self._template_state = {"moving":False, "turning_right":False, "turning_left":False}
        self._template_functions = {'moving': None, 'turning_right': None, 'turning_left':False}
        self._template_constraints = {'moving': None, 'turning_right': None, 'turning_left':False}
    
    def add_elem(self, name, elem, functions={}, constraints={}):

        assert functions.keys() == self._template_functions.keys(), "Functions need to contains those ones: {}".format(self._template_functions)

        self.elems[name] = elem
        self.elems_states[name]  = self._template_state.copy()
        self.elems_funcs[name]  = functions
        self.elems_constraints[name]  = constraints
    
    def run(self):
        for elem_name, elem in self.elems.items():
            for action, do in self.elems_states[elem_name].items():
                if not do:
                    continue

                constraint = self.elems_constraints[elem_name][action]
                f = self.elems_funcs[elem_name][action]

                if constraint is None or constraint() == False:
                    f()

    
    def set_state(self, name, state, value):
        self.elems_states[name][state] = value
        

pygame.init() 
screen = pygame.display.set_mode(WINDOW_SIZE)
screen_mgr = ScreenManager(screen)
robot = Robot(pos=ROBOT_POS, speed=ROBOT_SPEED, sight_radius=30, sight_angle=90, render_kw={'color': GREEN, 'size': ROBOT_SIZE, 'color_second':BLACK}, map_size=[WINDOW_SIZE[0] //2, WINDOW_SIZE[1]])

screen_mgr.add_elem(robot, 'left-right', layer=1)

for wall in get_surrounding_walls(screen_mgr.surfaces['left'], size=5):
    screen_mgr.add_elem(wall, 'left')


# trashes = []
# # for _ in range(9):
# #     t = Trash.spawn_random(screen_mgr.surfaces['left'], 20)
# #     screen_mgr.add_elem(t, 'left')
# #     trashes.append(t)

walls = []
for _ in range(RANDOM_WALL_NB):
    for wall in Wall.spawn_random(screen_mgr.surfaces['left'], 20):
        screen_mgr.add_elem(wall, 'left')
        walls.append(wall)


mv_mgr = MovingManager()
mv_mgr.add_elem(
    'robot', 
    robot, 
    {
        'moving':robot.move,
        'turning_right': partial(robot.turn, angle=ROBOT_TURNANGLE),
        'turning_left': partial(robot.turn, angle=-ROBOT_TURNANGLE),
    },
    {
        'moving':robot.check_collision_with_walls,
        'turning_right': robot.check_collision_with_walls,
        'turning_left': robot.check_collision_with_walls,
    },
)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
   
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                mv_mgr.set_state('robot', 'moving', True)
            if event.key == pygame.K_LEFT:
                mv_mgr.set_state('robot', 'turning_left', True)
            if event.key == pygame.K_RIGHT:
                mv_mgr.set_state('robot', 'turning_right', True)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                mv_mgr.set_state('robot', 'moving', False)
            if event.key == pygame.K_LEFT:
                mv_mgr.set_state('robot', 'turning_left', False)
            if event.key == pygame.K_RIGHT:
                mv_mgr.set_state('robot', 'turning_right', False)

    mv_mgr.run()
    ##


    # # TODO: Add to MAP
    # for t in trashes:
    #     dst = np.sqrt((robot.pos[0] - t.pos[0])**2 + (robot.pos[1] - t.pos[1])**2)
    #     if dst <= robot.render_kw['size']:
    #         screen_mgr.del_element(t, 'left') # TODO call it elem


    ##################



    screen_mgr.draw()
    pygame.display.flip()

    screen_mgr.blitarray_right(robot.map.grid)

    robot.in_sight()

