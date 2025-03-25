import math
import pygame


class Ship(object):
    def __init__(self):
        self.x = 400
        self.y = 300
        self.angle = 0
        self.x_vector = 0
        self.y_vector = 0
        self.max_speed = 1000
        self.points = self.get_points()
        self.forward_thrust = 0.2
        self.side_thrust = 0.2

    @classmethod
    def create(cls):
        return cls()

    def get_points(self):
        return [
            (self.x + 20 * math.cos(math.radians(self.angle)), self.y - 20 * math.sin(math.radians(self.angle))),
            (self.x + 10 * math.cos(math.radians(self.angle + 135)), self.y - 10 * math.sin(math.radians(self.angle + 135))),
            (self.x + 10 * math.cos(math.radians(self.angle - 135)), self.y - 10 * math.sin(math.radians(self.angle - 135)))
        ]

    def accelerate(self, direction):
        ax = math.cos(math.radians(self.angle)) * self.forward_thrust
        ay = -math.sin(math.radians(self.angle)) * self.forward_thrust

        if direction == 'forward':
            self.x_vector += ax
            self.y_vector += ay
        if direction == 'backward':
            self.x_vector -= ax
            self.y_vector -= ay

        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.x_vector *= scale
            self.y_vector *= scale

    def accelerate_lateral(self, direction):
        ax = -math.sin(math.radians(self.angle)) * self.side_thrust
        ay = -math.cos(math.radians(self.angle)) * self.side_thrust

        if direction == 'left':
            self.x_vector += ax
            self.y_vector += ay
        if direction == 'right':
            self.x_vector -= ax
            self.y_vector -= ay

        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.x_vector *= scale
            self.y_vector *= scale

    def brake(self):
        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > 0:
            reduction_factor = self.forward_thrust / speed
            self.x_vector -= self.x_vector * reduction_factor
            self.y_vector -= self.y_vector * reduction_factor

            if speed < self.forward_thrust:
                self.x_vector = 0
                self.y_vector = 0

    def turn(self, direction):
        if direction == 'left':
            self.angle += 5
        if direction == 'right':
            self.angle -= 5

    def move(self):
        self.x += self.x_vector
        self.y += self.y_vector

        self.x = self.x % 800
        self.y = self.y % 600
        self.points = self.get_points()

    def render(self, screen):
        pygame.draw.polygon(screen, (0, 0, 255), self.points)


