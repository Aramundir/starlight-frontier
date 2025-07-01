import math
import pygame
from abc import ABC, abstractmethod


class ShipFactory:
    @staticmethod
    def create_ship(x, y, faction, ship_class):
        ship = Ship(x, y, faction)
        components = {
            'scout': {
                'main_thrusters': ScoutMainThrusters,
                'maneuvering_thrusters': ScoutManeuveringThrusters,
                'cannon': ScoutCannon,
                'hull': ScoutHull,
                'auto_pilot': AutoPilot
            },
            'fighter': {
                'main_thrusters': FighterMainThrusters,
                'maneuvering_thrusters': FighterManeuveringThrusters,
                'cannon': FighterCannon,
                'hull': FighterHull,
                'auto_pilot': AutoPilot
            },
            'heavy_fighter': {
                'main_thrusters': HeavyFighterMainThrusters,
                'maneuvering_thrusters': HeavyFighterManeuveringThrusters,
                'cannon': HeavyFighterCannon,
                'hull': HeavyFighterHull,
                'auto_pilot': AutoPilot
            }
        }
        ship.hull = components[ship_class]['hull'].create_for_ship()
        ship.main_thrusters = components[ship_class]['main_thrusters'].create_for_ship()
        ship.maneuvering_thrusters = components[ship_class]['maneuvering_thrusters'].create_for_ship()
        ship.cannon = components[ship_class]['cannon'].create_for_ship()
        ship.auto_pilot = components[ship_class]['auto_pilot'].create_for_ship()
        ship._get_image()
        return ship


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, faction):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.angle = 0
        self.x_vector = 0
        self.y_vector = 0
        self.angular_velocity = 0.0  # New: rotational speed (degrees per frame)
        self.faction = faction
        self.color = self._get_color()
        self.main_thrusters = None
        self.maneuvering_thrusters = None
        self.cannon = None
        self.hull = None
        self.auto_pilot = None
        self.base_image = None
        self.image = None
        self.rect = None
        self.mask = None

    def _get_color(self):
        factions = {
            'player': (0, 0, 255),
            'enemy': (255, 0, 0),
            'ally': (0, 255, 0)
        }
        return factions[self.faction]

    def _get_image(self):
        surface_size = {'small': 50, 'medium': 100, 'large': 200}
        size = self.hull.get_size()
        self.base_image = pygame.Surface((surface_size[size], surface_size[size]), pygame.SRCALPHA)
        self.base_image.fill((250, 250, 250, 0))
        shape = [(x + surface_size[size] / 2, y + surface_size[size] / 2) for x, y in self.hull.get_shape()]
        pygame.draw.polygon(self.base_image, self.color, shape)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    @classmethod
    def create(cls, x, y, faction, ship_class):
        return ShipFactory.create_ship(x, y, faction, ship_class)

    def get_total_mass(self):
        total_mass = self.hull.max_hullpoints
        if self.main_thrusters:
            total_mass += self.main_thrusters.mass
        if self.maneuvering_thrusters:
            total_mass += self.maneuvering_thrusters.mass
        if self.cannon:
            total_mass += self.cannon.mass
        return total_mass

    def accelerate(self, direction):
        self.main_thrusters.accelerate(self, direction, self.get_total_mass())

    def accelerate_lateral(self, direction):
        self.maneuvering_thrusters.accelerate_lateral(self, direction, self.get_total_mass())

    def brake(self):
        self.maneuvering_thrusters.brake(self, self.get_total_mass())

    def brake_rotation(self):
        self.maneuvering_thrusters.brake_rotation(self, self.get_total_mass())

    def turn(self, direction):
        self.maneuvering_thrusters.turn(self, direction, self.get_total_mass())

    def move(self):
        self.x += self.x_vector
        self.y += self.y_vector
        self.angle += self.angular_velocity
        self.angle %= 360

    def approach_target(self, target_x, target_y, tolerance=200):
        return self.auto_pilot.navigate_to_target(self, target_x, target_y, tolerance)

    def fire(self):
        return self.cannon.fire(self)

    def update(self, dt=0):
        self.move()
        self.cannon.update(dt)
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def hullpoints(self):
        return self.hull.hullpoints

    @hullpoints.setter
    def hullpoints(self, value):
        self.hull.hullpoints = value

    @property
    def ship_stats(self):
        return {
            'hardpoints': self.hull.hardpoints,
            'max_hullpoints': self.hull.max_hullpoints,
            'total_mass': self.get_total_mass()
        }


class MainThrusters(ABC):
    def __init__(self, forward_thrust, max_speed, mass):
        self.forward_thrust = forward_thrust
        self.max_speed = max_speed
        self.mass = mass

    @classmethod
    @abstractmethod
    def create_for_ship(cls):
        pass

    def accelerate(self, ship, direction, total_mass):
        ax = math.cos(math.radians(ship.angle)) * self.forward_thrust
        ay = -math.sin(math.radians(ship.angle)) * self.forward_thrust
        resistance_factor = 1.0 / (1.0 + total_mass)
        ax *= resistance_factor
        ay *= resistance_factor
        if direction == 'forward':
            ship.x_vector += ax
            ship.y_vector += ay
        if direction == 'backward':
            ship.x_vector -= ax
            ship.y_vector -= ay
        self._clamp_speed(ship)

    def _clamp_speed(self, ship):
        speed = math.sqrt(ship.x_vector ** 2 + ship.y_vector ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            ship.x_vector *= scale
            ship.y_vector *= scale


class ScoutMainThrusters(MainThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(forward_thrust=0.6, max_speed=12.0, mass=1.0)


class FighterMainThrusters(MainThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(forward_thrust=0.5, max_speed=10.0, mass=2.0)


class HeavyFighterMainThrusters(MainThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(forward_thrust=0.6, max_speed=8.0, mass=3.0)


class ManeuveringThrusters(ABC):
    def __init__(self, side_thrust, turn_rate, mass):
        self.side_thrust = side_thrust
        self.turn_rate = turn_rate
        self.mass = mass

    @classmethod
    @abstractmethod
    def create_for_ship(cls):
        pass

    def accelerate_lateral(self, ship, direction, total_mass):
        ax = -math.sin(math.radians(ship.angle)) * self.side_thrust
        ay = -math.cos(math.radians(ship.angle)) * self.side_thrust
        resistance_factor = 1.0 / (1.0 + total_mass)
        ax *= resistance_factor
        ay *= resistance_factor
        if direction == 'left':
            ship.x_vector += ax
            ship.y_vector += ay
        if direction == 'right':
            ship.x_vector -= ax
            ship.y_vector -= ay
        speed = math.sqrt(ship.x_vector ** 2 + ship.y_vector ** 2)
        if speed > ship.main_thrusters.max_speed:
            scale = ship.main_thrusters.max_speed / speed
            ship.x_vector *= scale
            ship.y_vector *= scale

    def turn(self, ship, direction, total_mass):
        resistance_factor = 1.0 / (1.0 + total_mass)
        angular_acceleration = self.turn_rate * resistance_factor * 0.1
        if direction == 'left':
            ship.angular_velocity = min(ship.angular_velocity + angular_acceleration, self.turn_rate)
        if direction == 'right':
            ship.angular_velocity = max(ship.angular_velocity - angular_acceleration, -self.turn_rate)

    def brake_rotation(self, ship, total_mass):
        resistance_factor = 1.0 / (1.0 + total_mass)
        angular_deceleration = self.turn_rate * resistance_factor * 0.1
        if ship.angular_velocity > 0:
            ship.angular_velocity = max(ship.angular_velocity - angular_deceleration, 0)
        if ship.angular_velocity < 0:
            ship.angular_velocity = min(ship.angular_velocity + angular_deceleration, 0)

    def brake(self, ship, total_mass):
        speed = math.sqrt(ship.x_vector ** 2 + ship.y_vector ** 2)
        if speed > 0:
            resistance_factor = 1.0 / (1.0 + total_mass)
            reduction_factor = (self.side_thrust * 5.0 / speed) * resistance_factor
            ship.x_vector -= ship.x_vector * reduction_factor
            ship.y_vector -= ship.y_vector * reduction_factor
            if speed < self.side_thrust * resistance_factor * 2.0:
                ship.x_vector = 0
                ship.y_vector = 0


class ScoutManeuveringThrusters(ManeuveringThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(side_thrust=0.1, turn_rate=2.0, mass=1.0)


class FighterManeuveringThrusters(ManeuveringThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(side_thrust=0.3, turn_rate=6.0, mass=2.0)


class HeavyFighterManeuveringThrusters(ManeuveringThrusters):
    @classmethod
    def create_for_ship(cls):
        return cls(side_thrust=0.2, turn_rate=3.0, mass=3.0)


class Cannon(ABC):
    def __init__(self, shoot_delay, projectile_speed, mass):
        self.shoot_delay = shoot_delay
        self.projectile_speed = projectile_speed
        self.mass = mass
        self.shoot_cooldown = 0

    @classmethod
    @abstractmethod
    def create_for_ship(cls):
        pass

    def fire(self, ship):
        if self.shoot_cooldown > 0:
            return []
        projectiles = []
        rad = math.radians(ship.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        for hp_x, hp_y in ship.hull.hardpoints:
            offset_x = hp_x * cos_a - hp_y * sin_a
            offset_y = hp_x * sin_a + hp_y * cos_a
            start_x = ship.x + offset_x
            start_y = ship.y - offset_y
            proj = Projectile.create(start_x, start_y, ship.angle, ship.x_vector, ship.y_vector, self.projectile_speed)
            projectiles.append(proj)
        self.shoot_cooldown = self.shoot_delay
        return projectiles

    def update(self, dt):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            if self.shoot_cooldown < 0:
                self.shoot_cooldown = 0


class ScoutCannon(Cannon):
    @classmethod
    def create_for_ship(cls):
        return cls(shoot_delay=600, projectile_speed=30.0, mass=3.0)


class FighterCannon(Cannon):
    @classmethod
    def create_for_ship(cls):
        return cls(shoot_delay=300, projectile_speed=20.0, mass=2.0)


class HeavyFighterCannon(Cannon):
    @classmethod
    def create_for_ship(cls):
        return cls(shoot_delay=150, projectile_speed=10.0, mass=1.0)


class Hull(ABC):
    def __init__(self, hullpoints, hardpoints, shape, size):
        self._hullpoints = hullpoints
        self.max_hullpoints = hullpoints
        self.hardpoints = hardpoints
        self.shape = shape
        self.size = size

    @classmethod
    @abstractmethod
    def create_for_ship(cls):
        pass

    def get_shape(self):
        return self.shape

    def get_size(self):
        return self.size

    @property
    def hullpoints(self):
        return self._hullpoints

    @hullpoints.setter
    def hullpoints(self, value):
        self._hullpoints = max(0, value)


class ScoutHull(Hull):
    @classmethod
    def create_for_ship(cls):
        return cls(
            hullpoints=2,
            hardpoints=[(11, 0)],
            shape=[(10, 0), (-10, -9), (-10, 9)],
            size='small'
        )


class FighterHull(Hull):
    @classmethod
    def create_for_ship(cls):
        return cls(
            hullpoints=4,
            hardpoints=[(-10, 10), (-10, -10)],
            shape=[(20, 0), (-10, -9), (-10, 9)],
            size='small'
        )


class HeavyFighterHull(Hull):
    @classmethod
    def create_for_ship(cls):
        return cls(
            hullpoints=6,
            hardpoints=[(11, 0), (-10, 19), (-10, -19)],
            shape=[(10, 0), (-10, 18), (-10, -18)],
            size='small'
        )


class AutoPilot:

    @classmethod
    def create_for_ship(cls):
        return cls()

    def navigate_to_target(self, ship, target_x, target_y, tolerance=200):
        delta_x = target_x - ship.x
        delta_y = target_y - ship.y
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        if distance < tolerance:
            ship.brake()

        target_angle = math.degrees(math.atan2(-delta_y, delta_x)) + 180
        if target_angle < 0:
            target_angle += 360

        angle_diff = (target_angle - ship.angle + 180) % 360

        if angle_diff > 180:
            ship.turn('right')
        if angle_diff < 180:
            ship.turn('left')

        ship.angle = ship.angle % 360

        alignment = abs(angle_diff) / 180

        if distance > tolerance:
            if alignment <= 0.5:
                ship.accelerate('forward')
            if alignment > 0.5:
                if 45 < abs(angle_diff) < 135:
                    if angle_diff > 100:
                        ship.accelerate_lateral('right')
                    if angle_diff < 100:
                        ship.accelerate_lateral('left')

        return distance, alignment


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, x_vector, y_vector, speed):
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
    def create(cls, x, y, angle, x_vector, y_vector, speed):
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
