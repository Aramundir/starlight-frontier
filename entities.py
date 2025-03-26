import math
import pygame


class Ship(object):
    def __init__(self, x, y, turn_rate, faction):
        self.x = x
        self.y = y
        self.angle = 0
        self.x_vector = 0
        self.y_vector = 0
        self.max_speed = 10
        self.points = self.get_points()
        self.forward_thrust = 0.1
        self.side_thrust = 0.1
        self.turn_rate = turn_rate
        self.color = self.get_color(faction)

    @classmethod
    def create(cls, x, y, turn_rate, faction):
        return cls(x, y, turn_rate, faction)

    def get_points(self):
        return [
            (self.x + 20 * math.cos(math.radians(self.angle)), self.y - 20 * math.sin(math.radians(self.angle))),
            (self.x + 10 * math.cos(math.radians(self.angle + 135)), self.y - 10 * math.sin(math.radians(self.angle + 135))),
            (self.x + 10 * math.cos(math.radians(self.angle - 135)), self.y - 10 * math.sin(math.radians(self.angle - 135)))
        ]

    def get_color(self, faction):
        factions = {
            'player': (0, 0, 255),
            'enemy': (255, 0, 0),
            'ally': (0, 255, 0),
                 }
        return factions[faction]

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
            self.angle += self.turn_rate
        if direction == 'right':
            self.angle -= self.turn_rate

    def move(self):
        self.x += self.x_vector
        self.y += self.y_vector

        self.x = self.x % 800
        self.y = self.y % 600
        self.points = self.get_points()

    def approach_target(self, target_x, target_y, tolerance=200):
        delta_x = target_x - self.x
        delta_y = target_y - self.y
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        if distance < tolerance:
            self.brake()

        target_angle = math.degrees(math.atan2(-delta_y, delta_x)) + 180
        if target_angle < 0:
            target_angle += 360

        angle_diff = (target_angle - self.angle + 180) % 360

        if angle_diff > 180:
            self.turn('right')
        if angle_diff < 180:
            self.turn('left')

        self.angle = self.angle % 360

        alignment = abs(angle_diff) / 180

        if distance > tolerance:
            if alignment < 0.5:
                self.accelerate('forward')
            if alignment > 0.5:
                if 45 < abs(angle_diff) < 135:
                    if angle_diff > 180:
                        self.accelerate_lateral('right')
                    if angle_diff < 180:
                        self.accelerate_lateral('left')
        return

    def render(self, screen):
        pygame.draw.polygon(screen, self.color, self.points)
