import pygame
import pymunk
import math
from pymunk import Vec2d
from config import *

class Bird:
    def __init__(self, x, y, impulse):
        # create body
        mass = 5
        radius = bird_radius
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, inertia)
        body.position = x, y

        # create shape
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = BIRD_COLLISION_TYPE

        # apply impulse
        body.apply_impulse_at_local_point(impulse)


        self.shape = shape
        self.body = body

    def draw(self, screen):
        x, y = to_pygame(self.body.position)
        # draw circle border
        #pygame.draw.circle(screen, BLUE, (x, y), bird_radius, 2)
        x -= bird_radius
        y -= bird_radius
        # draw bird
        screen.blit(bird, (x, y))

class Pig:
    def __init__(self, x, y):
        # create body
        mass = 5
        radius = pig_radius
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, inertia)
        body.position = x, y

        # create shape
        shape = pymunk.Circle(body, pig_radius)
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = PIG_COLLISION_TYPE

        self.body = body
        self.shape = shape

    def draw(self, screen):
        x, y = to_pygame(self.body.position)
        # draw circle border
        #pygame.draw.circle(screen, YELLOW, (x, y), pig_radius, 2)
        x -= pig_radius
        y -= pig_radius
        # draw bird
        screen.blit(pig, (x, y))


class Wood:
    def __init__(self, x, y, width, height, type='beam'):
        # create body
        mass = 2
        inertia = 10000
        body = pymunk.Body(mass, inertia)
        body.position = Vec2d(x, y)

        # create shape
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = 1.05
        shape.collision_type = WOOD_COLLISION_TYPE

        self.shape = shape
        self.body = body
        self.type = type


    def draw(self, screen):
        # Draw rectangle around wood
        # vertices = self.shape.get_vertices()
        # new_vertices = []
        # for v in vertices:
        #     x, y = v.rotated(self.body.angle) + self.body.position
        #     x, y = to_pygame(Vec2d(x, y))
        #     new_vertices.append((x, y))
        # new_vertices.append(new_vertices[0])    # To make a closed rectangle
        # pygame.draw.lines(screen, RED, True, new_vertices, 2)

        angle = math.degrees(self.body.angle) + 180
        if self.type == 'beam':
            img = beam
        else:
            img = column
        img = pygame.transform.rotate(img, angle)
        x, y = to_pygame(self.body.position)
        offset = Vec2d(img.get_size()) // 2
        screen.blit(img, (x - offset[0], y - offset[1]))

