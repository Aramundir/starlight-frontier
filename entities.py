import math
import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, faction, ship_class):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.angle = 0
        self.x_vector = 0
        self.y_vector = 0
        self.ship_stats = self.get_ship_stats(ship_class)
        self.color = self.get_color(faction)
        self.shoot_cooldown = 0
        self.base_image = None
        self.image = None
        self.rect = None
        self.mask= None
        self.get_image(self.ship_stats['size'])

    @classmethod
    def create(cls, x, y, faction, ship_class):
        return cls(x, y, faction, ship_class)

    def get_image(self, size):
        surface_size = {
            'small': 50,
            'medium': 100,
            'large': 200
        }
        self.base_image = pygame.Surface((surface_size[size], surface_size[size]), pygame.SRCALPHA)
        self.base_image.fill((250, 250, 250, 0))
        shape = [(x + surface_size[size] / 2, y + surface_size[size] / 2) for x, y in self.ship_stats['shape']]
        pygame.draw.polygon(self.base_image, self.color, shape)
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

    def get_ship_stats(self, ship_class):
        classes = {
            'scout': {
                'shoot_delay': 600,
                'hullpoints': 2,
                'hardpoints':  [(11, 0)],
                'max_speed': 12.0,
                'forward_thrust': 0.2,
                'side_thrust': 0.2,
                'turn_rate': 8.0,
                'shape': [(10, 0), (-10, -9), (-10, 9)],
                'size': 'small'
            },
            'fighter': {
                'shoot_delay': 300,
                'hullpoints': 4,
                'hardpoints': [(-10, 10), (-10, -10)],
                'max_speed': 10.0,
                'forward_thrust': 0.1,
                'side_thrust': 0.1,
                'turn_rate': 4.0,
                'shape': [(20, 0), (-10, -9), (-10, 9)],
                'size': 'small'
            },
            'heavy_fighter': {
                'shoot_delay': 150,
                'hullpoints': 6,
                'hardpoints': [(11,0),(-10,19),(-10,-19)],
                'max_speed': 8.0,
                'forward_thrust': 0.05,
                'side_thrust': 0.05,
                'turn_rate': 2.0,
                'shape': [(10,0),(-10,18),(-10,-18)],
                'size': 'small'
            }
        }
        return classes[ship_class]

    def accelerate(self, direction):
        ax = math.cos(math.radians(self.angle)) * self.ship_stats['forward_thrust']
        ay = -math.sin(math.radians(self.angle)) * self.ship_stats['forward_thrust']

        if direction == 'forward':
            self.x_vector += ax
            self.y_vector += ay
        if direction == 'backward':
            self.x_vector -= ax
            self.y_vector -= ay

        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > self.ship_stats['max_speed']:
            scale = self.ship_stats['max_speed'] / speed
            self.x_vector *= scale
            self.y_vector *= scale

    def accelerate_lateral(self, direction):
        ax = -math.sin(math.radians(self.angle)) * self.ship_stats['side_thrust']
        ay = -math.cos(math.radians(self.angle)) * self.ship_stats['side_thrust']

        if direction == 'left':
            self.x_vector += ax
            self.y_vector += ay
        if direction == 'right':
            self.x_vector -= ax
            self.y_vector -= ay

        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > self.ship_stats['max_speed']:
            scale = self.ship_stats['max_speed'] / speed
            self.x_vector *= scale
            self.y_vector *= scale

    def brake(self):
        speed = math.sqrt(self.x_vector ** 2 + self.y_vector ** 2)
        if speed > 0:
            reduction_factor = self.ship_stats['forward_thrust'] / speed
            self.x_vector -= self.x_vector * reduction_factor
            self.y_vector -= self.y_vector * reduction_factor

            if speed < self.ship_stats['forward_thrust']:
                self.x_vector = 0
                self.y_vector = 0

    def turn(self, direction):
        if direction == 'left':
            self.angle += self.ship_stats['turn_rate']
        if direction == 'right':
            self.angle -= self.ship_stats['turn_rate']

    def move(self):
        self.x += self.x_vector
        self.y += self.y_vector
        self.x = self.x % 1280
        self.y = self.y % 720

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

        return distance, alignment

    def fire_projectile(self):
        if self.shoot_cooldown > 0:
            return []
        projectiles = []
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        for hp_x, hp_y in self.ship_stats['hardpoints']:
            offset_x = hp_x * cos_a - hp_y * sin_a
            offset_y = hp_x * sin_a + hp_y * cos_a
            start_x = self.x + offset_x
            start_y = self.y - offset_y
            proj = Projectile(start_x, start_y, self.angle, self.x_vector, self.y_vector)
            projectiles.append(proj)
        self.shoot_cooldown = self.ship_stats['shoot_delay']
        return projectiles

    def update(self, dt=0):
        self.move()
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            if self.shoot_cooldown < 0:
                self.shoot_cooldown = 0

    @property
    def hullpoints(self):
        return self.ship_stats['hullpoints']

    @hullpoints.setter
    def hullpoints(self, value):
        self.ship_stats['hullpoints'] = max(0, value)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, x_vector, y_vector, speed=10):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.x_vector = x_vector
        self.y_vector = y_vector
        self.speed = speed
        self.base_image = None
        self.image = None
        self.rect = None
        self.mask = None
        self.get_image()
        self.add_speed_vector()

    @classmethod
    def create(cls, x, y, angle, x_vector, y_vector, speed=10):
        return cls(x, y, angle, x_vector, y_vector, speed)


    def get_image(self):
        self.base_image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.base_image.fill((0, 0, 0, 0))
        start_pos = (7.5, 5)
        end_pos = (2.5, 5)
        pygame.draw.line(self.base_image, (255, 255, 0), start_pos, end_pos, 2)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)


    def add_speed_vector(self):
        rad = math.radians(self.angle)
        self.x_vector += self.speed * math.cos(rad)
        self.y_vector -= self.speed * math.sin(rad)

    def move(self):
        self.x += self.x_vector
        self.y += self.y_vector

    def update(self):
        self.move()
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
