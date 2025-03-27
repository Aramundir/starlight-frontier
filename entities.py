import math
import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, turn_rate, faction):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.angle = 0
        self.x_vector = 0
        self.y_vector = 0
        self.max_speed = 10
        self.forward_thrust = 0.1
        self.side_thrust = 0.1
        self.turn_rate = turn_rate
        self.color = self.get_color(faction)
        self.base_image = None
        self.image = None
        self.rect = None
        self.mask= None
        self.get_image()



    @classmethod
    def create(cls, x, y, turn_rate, faction):
        return cls(x, y, turn_rate, faction)

    def get_image(self):
        self.base_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.base_image.fill((250, 250, 250, 0))
        base_points = [
            (45, 25),
            (20, 18),
            (20, 32)
        ]
        pygame.draw.polygon(self.base_image, self.color, base_points)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

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
        # self.rect.center = (self.x, self.y)

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
            if alignment <= 0.5:
                self.accelerate('forward')
            if alignment > 0.5:
                if 45 < abs(angle_diff) < 135:
                    if angle_diff > 100:
                        self.accelerate_lateral('right')
                    if angle_diff < 100:
                        self.accelerate_lateral('left')

        return

    def update(self):
        self.move()
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
