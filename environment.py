from abc import ABC, abstractmethod
import numpy as np
import pygame
import math
import random

from config import *

class PygameElement(ABC):

    @classmethod
    def spawn_random(cls, surface, margin):
        w,h = surface.get_size()
        pos = [random.randint(margin, w-margin), random.randint(margin, h-margin)]
        return cls(pos)


    @abstractmethod
    def draw(self, surface):
        pass


class Robot(PygameElement):
    def __init__(self, pos, speed=5, sight_radius=5, sight_angle=90, render_kw={}):        
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
        self.pos = pos
        self.orientation = np.array([0,1], dtype=np.float64)

        self.speed = speed
        self.sight_radius = sight_radius
        self.sight_angle = sight_angle
        self.render_kw = render_kw

    def turn(self, angle):
        angle = math.degrees(angle)
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        self.orientation = np.dot(rotation_mat, self.orientation)

    def move(self):
        self.pos += self.orientation * self.speed

    def draw(self, surface):
        s = self.render_kw['size']
        pygame.draw.circle(surface, self.render_kw['color'], self.pos, s)
        pygame.draw.line(surface, self.render_kw['color_second'], self.pos, self.pos+s*self.orientation)


class Trash(PygameElement):
    def __init__(self, pos, size=5, color=RED):
        self.pos = pos
        self.size = size
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.size)

class Map:
    pass
