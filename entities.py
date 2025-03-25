import math
import pygame


class Ship(object):
    def __init__(self, x, y, angle, speed, max_speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.max_speed = max_speed
        self.points = self.get_points()

    @classmethod
    def create(cls, x, y, angle, speed, max_speed):
        return cls(x, y, angle, speed, max_speed)

    def get_points(self):
        return [
            (self.x + 20 * math.cos(math.radians(self.angle)), self.y - 20 * math.sin(math.radians(self.angle))),
            (self.x + 10 * math.cos(math.radians(self.angle + 135)), self.y - 10 * math.sin(math.radians(self.angle + 135))),
            (self.x + 10 * math.cos(math.radians(self.angle - 135)), self.y - 10 * math.sin(math.radians(self.angle - 135)))
        ]

    def accelerate(self, direction):
        if direction == 'forward':
            self.speed = min(self.speed + 0.1, self.max_speed)
        if direction == 'backward':
            self.speed = max(self.speed - 0.1, (self.max_speed * -1))

    def turn(self, direction):
        if direction == 'left':
            self.angle += 5
        if direction == 'right':
            self.angle -= 5

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed

        self.x = self.x % 800
        self.y = self.y % 600
        self.points = self.get_points()

    def render(self, screen):
        pygame.draw.polygon(screen, (0, 0, 255), self.points)


