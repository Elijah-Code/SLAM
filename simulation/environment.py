"""
environment objects 
"""

from abc import ABC, abstractmethod
import numpy as np
import pygame
import math
import random

from config import *

class PygameElement(ABC):
    """
    base for pygame elem
    """
    objs = []

    def __init__(self):
        self.hitbox = None
        type(self).objs.append(self)

    def check_collision(self, elem):
        return self.hitbox.colliderect(elem.hitbox)

    @classmethod
    def spawn_random(cls, surface, margin):
        """
        spawn at random position on surface - margin
        """
        w,h = surface.get_size()
        pos = [random.randint(margin, w-margin), random.randint(margin, h-margin)]
        return cls(pos)

    @abstractmethod
    def draw(self, surface):
        pass


class Robot(PygameElement):
    objs = []

    def __init__(self, pos, speed=5, sight_radius=5, sight_angle=90, map_size=[10,10], render_kw={}):        
        """
        speed: float
            move speed of the robot
        sight_radius: float
            radius of the robot's sight
        sight_angle: float
            angle of the robot's sight
        render_kw: dict
            render arguments, need to contain: color(tuple) / size(tuple)
        """
        super().__init__()
        self.pos = pos
        self.last_pos = None
        self.orientation = np.array([0,1], dtype=np.float64)

        self.speed = speed
        self.sight_radius = sight_radius + render_kw['size']
        self.sight_angle = sight_angle
        self.render_kw = render_kw

        self.map = Map(size=map_size)

        self.radar_animations = [self.render_kw['size'] for _ in range(3)]
        self.radar_diff = (self.sight_radius - self.render_kw['size']) / len(self.radar_animations) 

        self.radar_hitbox = pygame.Rect(self.pos[0]-self.sight_radius, self.pos[1]-self.sight_radius, 2*self.sight_radius, 2*self.sight_radius)

        for ix in range(len(self.radar_animations)):
            self.radar_animations[ix] -= (self.radar_diff*ix)


    def check_collision_with_walls(self):
        for wall in Wall.objs:
            if self.check_collision(wall):
                self.bounce(wall.normal_vec())
                return True
        return False

    def in_sight(self):
        in_sight = []
        if self.hitbox is None or self.radar_hitbox is None:
            return []
        for f_cls in furnitures:
            for elem in f_cls.objs:
                if elem.hitbox is None:
                    continue
                if self.radar_hitbox.colliderect(elem.hitbox):
                    in_sight.append(elem)
                    self.map.add(elem.hitbox.topleft, elem.hitbox.bottomright)


        return in_sight

    def turn(self, angle):
        angle = math.degrees(angle)
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        self.orientation = np.dot(rotation_mat, self.orientation)

    def move(self):

        self.last_pos = self.pos.copy()
        self.pos += self.orientation * self.speed
    
    def bounce(self, direction):
        self.pos = self.last_pos

    def draw(self, surface):
        s = self.render_kw['size']

        for ix in range(len(self.radar_animations)):
            pygame.draw.circle(surface, YELLOW, self.pos, self.radar_animations[ix] , width=1)
            self.radar_animations[ix] += 0.1
            if self.radar_animations[ix] >= self.sight_radius:
                self.radar_animations[ix] = s

        pygame.draw.circle(surface, self.render_kw['color'], self.pos, s)
        pygame.draw.line(surface, self.render_kw['color_second'], self.pos, self.pos+s*self.orientation)
        self.hitbox = pygame.Rect(self.pos[0]-s, self.pos[1]-s, 2*s, 2*s)

        self.radar_hitbox = pygame.Rect(self.pos[0]-self.sight_radius, self.pos[1]-self.sight_radius, 2*self.sight_radius, 2*self.sight_radius)

class Trash(PygameElement):
    objs = []

    def __init__(self, pos, size=5, color=RED):
        super().__init__()
        self.pos = pos
        self.size = size
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.size)
        self.hitbox = pygame.Rect(self.pos[0]-self.size, self.pos[1]-self.size, 2*self.size, 2*self.size)

class Wall(PygameElement):

    objs = []

    def __init__(self, top_left, bot_right, color=WALL_COLOR):
        super().__init__()
        self.top_left = top_left
        self.bot_right = bot_right
        self.width = bot_right[0] - top_left[0]
        self.height = bot_right[1] - top_left[1]
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.color_random_counter = random.randint(0, 100)

    @classmethod
    def spawn_random(cls, surface, margin):
        """
        spawn at random position on surface - margin
        """
        w,h = surface.get_size()
        topleft = [random.randint(margin, w-margin), random.randint(margin, h-margin)]
        botright = [topleft[0]+ random.randint(0,50), topleft[1]+ random.randint(0,50)]

        x1, y1 = topleft[1], topleft[0]
        x2, y2 = botright[1], botright[0]
        walls = []
        walls.append(cls([x1, y1], [x2, y1]))
        walls.append(cls([x2, y1], [x2, y2]))
        walls.append(cls([x1, y2], [x2, y2]))
        walls.append(cls([x1, y1], [x1, y2]))

        return walls


    def draw(self, surface):
        # rect = pygame.Rect(self.top_left, (self.width, self.height))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        rect = pygame.draw.line(surface, self.color, self.top_left, self.bot_right, width=5)
        self.hitbox = rect
        self.color_random_counter += 1
        if self.color_random_counter == 100:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.color_random_counter = 0

    def unit_vec(self):
        vec = np.array([self.bot_right[0] - self.top_left[0], self.bot_right[1] - self.top_left[1]], dtype=np.float64)
        normalized = vec / np.sqrt(vec[0]**2  + vec[1]**2)
        return normalized
    
    def normal_vec(self):
        unit = self.unit_vec()
        return np.array([-unit[1], unit[0]])





class Map:

    def __init__(self, size):
        self.size  = size
        self.grid  = np.zeros((size[0], size[1], 3))
    
    def add(self, tl, br):
        # self.grid[tl[1]:br[1], tl[0]:br[0]] = (255, 255, 255)
        self.grid[tl[0]:br[0], tl[1]:br[1]] = (255, 255, 255)

    





furnitures = [
    Wall,
    Trash,
]
