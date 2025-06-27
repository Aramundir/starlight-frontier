import math
import random
import pygame


class Camera:
    def __init__(self, screen_width, screen_height, player):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player = player
        self.x = None
        self.y = None

    @classmethod
    def create_for_gameloop(cls, screen_width, screen_height, player):
        return cls(screen_width, screen_height, player)

    def get_ship_screen_coordinates(self, ship):
        screen_x = ship.x - self.x
        screen_y = ship.y - self.y
        return [screen_x, screen_y]

    def get_multiple_ship_screen_coordinates(self, ships):
        return {ship: self.get_ship_screen_coordinates(ship) for ship in ships}

    def update(self, world_width, world_height):
        self.x = self.player.x - self.screen_width / 2
        self.y = self.player.y - self.screen_height / 2
        self.x = max(0, min(self.x, world_width - self.screen_width))
        self.y = max(0, min(self.y, world_height - self.screen_height))


class Physics:
    def __init__(self):
        self.world_width = 4000
        self.world_height = 4000

    @classmethod
    def create_for_gameloop(cls):
        return cls()

    def check_for_ship_collision(self, all_ships):
        for ship1 in all_ships:
            self.check_world_bounds(ship1)
            rect_collisions = pygame.sprite.spritecollide(ship1, all_ships, False, pygame.sprite.collide_rect)
            for ship2 in rect_collisions:
                if ship1 != ship2:
                    if pygame.sprite.collide_mask(ship1, ship2):
                        self.resolve_ship_collision(ship1, ship2)

    def resolve_ship_collision(self, ship1, ship2):
        dx = ship2.x - ship1.x
        dy = ship2.y - ship1.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            distance = 1

        nx = dx / distance
        ny = dy / distance

        min_distance = 25

        overlap = min_distance - distance
        if overlap > 0:
            push = overlap / 2
            ship1.x -= nx * push
            ship1.y -= ny * push
            ship2.x += nx * push
            ship2.y += ny * push

            ship1.rect.center = (ship1.x, ship1.y)
            ship2.rect.center = (ship2.x, ship2.y)

    def check_for_projectile_collisions(self, projectiles, all_ships):
        proj_list = list(projectiles)
        for i, proj1 in enumerate(proj_list):
            if not proj1.alive():
                continue
            if not (0 <= proj1.x <= self.world_width and 0 <= proj1.y <= self.world_height):
                proj1.kill()
                continue

            rect_collisions = pygame.sprite.spritecollide(proj1, all_ships, False, pygame.sprite.collide_rect)
            for ship in rect_collisions:
                if pygame.sprite.collide_mask(proj1, ship):
                    ship.hullpoints -= 1
                    proj1.kill()
                    if ship.hullpoints <= 0:
                        ship.kill()
                    break
            for proj2 in proj_list[i + 1:]:
                if proj2.alive() and proj1.rect.colliderect(proj2.rect):
                    if pygame.sprite.collide_mask(proj1, proj2):
                        proj1.kill()
                        proj2.kill()

    def check_world_bounds(self, ship):
        if ship.x < 0:
            ship.x = 0
            ship.x_vector = max(0, ship.x_vector)
        if ship.x > self.world_width:
            ship.x = self.world_width
            ship.x_vector = min(0, ship.x_vector)
        if ship.y < 0:
            ship.y = 0
            ship.y_vector = max(0, ship.y_vector)
        if ship.y > self.world_height:
            ship.y = self.world_height
            ship.y_vector = min(0, ship.y_vector)
        ship.rect.center = (ship.x, ship.y)


class GameMaster:
    def __init__(self, entities):
        self.entities = entities
        self.world_width = 4000
        self.world_height = 4000

    @classmethod
    def create_for_gameloop(cls, entities):
        return cls(entities)

    def spawn_enemies(self, num_enemies, player_pos, difficulty, min_distance=300):
        enemies = []
        enemy_class = {
            1: ['scout'],
            2: ['scout', 'fighter'],
            3: ['scout', 'fighter', 'heavy_fighter'],
            4: ['fighter', 'heavy_fighter'],
            5: ['heavy_fighter']
        }
        for _ in range(num_enemies):
            while True:
                x = random.randint(0, self.world_width)
                y = random.randint(0, self.world_height)
                distance = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
                if distance >= min_distance:
                    break
            ship_class = random.choice(enemy_class[difficulty])
            enemy = self.entities.Ship.create(x, y, 'enemy', ship_class)
            enemies.append(enemy)
        return enemies

    def setup_game(self, all_ships, projectiles, player_pos, num_enemies, difficulty):
        all_ships.empty()
        projectiles.empty()
        player = self.entities.Ship.create(player_pos[0], player_pos[1], 'player', 'heavy_fighter')
        all_ships.add(player)
        enemies = self.spawn_enemies(num_enemies, player_pos, difficulty)
        all_ships.add(enemies)
        return player, enemies


class ScreenPainter:
    def __init__(self):
        self.world_width = 4000
        self.world_height = 4000

    @classmethod
    def create_for_gameloop(cls):
        return cls()

    def create_a_star_surface(self):
        star_surface = pygame.Surface((self.world_width, self.world_height))
        star_surface.fill((0, 0, 0))
        for star in range(1500):
            pygame.draw.circle(star_surface, (255, 255, 255),
                               (random.randint(0, self.world_width), random.randint(0, self.world_height)), 1)
        return star_surface

    def display_end_screen(self, screen, status):
        font = pygame.font.SysFont(None, 48)
        screen_text = {
            'game_over': font.render("Game Over! - Press R to Restart", True, (190, 0, 0)),
            'victory': font.render("Congratulations! - Press R to Advance", True, (190, 190, 0))
        }
        text = screen_text[status]
        text_rect = text.get_rect(center=(640, 360))  # Center on 1280x720
        screen.blit(text, text_rect)


class HUD:
    def __init__(self, camera):
        self.hull_meter = HullMeter.create_for_hud(camera)
        self.aiming_line = AimingLine.create_for_hud(camera)
        self.offscreen_arrows = OffscreenArrows.create_for_hud(camera)

    @classmethod
    def create_for_gameloop(cls, camera):
        return cls(camera)

    def draw(self, screen, player, enemies):
        self.hull_meter.draw(screen, player)
        self.aiming_line.draw(screen, player)
        self.offscreen_arrows.draw(screen, player, enemies)


class HullMeter:
    def __init__(self, camera):
        self.camera = camera
        self.hull_color = (0, 255, 0, 200)
        self.hull_width = 50
        self.hull_height = 5
        self.hull_offset_y = 25

    @classmethod
    def create_for_hud(cls, camera):
        return cls(camera)

    def draw(self, screen, player):
        player_coords = self.camera.get_ship_screen_coordinates(player)
        hull_ratio = player.hullpoints / player.ship_stats['max_hullpoints']
        hull_current_width = self.hull_width * hull_ratio
        hull_x = player_coords[0] - self.hull_width / 2
        hull_y = player_coords[1] + self.hull_offset_y
        base_surface = pygame.Surface((self.hull_width, self.hull_height), pygame.SRCALPHA)
        pygame.draw.rect(base_surface, self.hull_color,
                         (0, 0, hull_current_width, self.hull_height))
        pygame.draw.rect(base_surface, (100, 100, 100),
                         (0, 0, self.hull_width, self.hull_height), 1)
        screen.blit(base_surface, (hull_x, hull_y))


class AimingLine:
    def __init__(self, camera):
        self.camera = camera
        self.screen_width = camera.screen_width
        self.screen_height = camera.screen_height
        self.aiming_line_color = (0, 255, 0, 200)
        self.aiming_line_start_offset = 50
        self.aiming_line_length = 150
        self.aiming_line_thickness = 1

    @classmethod
    def create_for_hud(cls, camera):
        return cls(camera)

    def draw(self, screen, player):
        line_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        player_coords = self.camera.get_ship_screen_coordinates(player)
        rad = math.radians(player.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        for hp_x, hp_y in player.ship_stats['hardpoints']:
            hp_rot_x = hp_x * cos_a - hp_y * sin_a
            hp_rot_y = hp_x * sin_a + hp_y * cos_a
            hp_screen_x = player_coords[0] + hp_rot_x
            hp_screen_y = player_coords[1] - hp_rot_y

            line_start_x = hp_screen_x + self.aiming_line_start_offset * cos_a
            line_start_y = hp_screen_y - self.aiming_line_start_offset * sin_a
            line_end_x = hp_screen_x + self.aiming_line_length * cos_a
            line_end_y = hp_screen_y - self.aiming_line_length * sin_a

            pygame.draw.line(line_surface, self.aiming_line_color,
                             (line_start_x, line_start_y),
                             (line_end_x, line_end_y),
                             self.aiming_line_thickness)

        screen.blit(line_surface, (0, 0))


class OffscreenArrows:
    def __init__(self, camera):
        self.camera = camera
        self.screen_width = camera.screen_width
        self.screen_height = camera.screen_height
        self.arrow_color = (255, 0, 0, 200)
        self.arrow_size = 8
        self.arrow_margin = 10

    @classmethod
    def create_for_hud(cls, camera):
        return cls(camera)

    def _is_enemy_offscreen(self, enemy_screen_coords):
        x, y = enemy_screen_coords
        return not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height)

    def _calculate_direction_vector(self, player_coords, enemy_coords):
        dx = enemy_coords[0] - player_coords[0]
        dy = enemy_coords[1] - player_coords[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < 1:
            return None, None, None
        nx = dx / distance
        ny = dy / distance
        return nx, ny, distance

    def _calculate_t_values(self, player_coords, nx, ny):
        t_left = (self.arrow_margin - player_coords[0]) / nx if nx != 0 else float('inf')
        t_right = (self.screen_width - self.arrow_margin - player_coords[0]) / nx if nx != 0 else float('inf')
        t_top = (self.arrow_margin - player_coords[1]) / ny if ny != 0 else float('inf')
        t_bottom = (self.screen_height - self.arrow_margin - player_coords[1]) / ny if ny != 0 else float('inf')
        return t_left, t_right, t_top, t_bottom

    def _select_intersection_t(self, nx, ny, t_left, t_right, t_top, t_bottom):
        t_values = []
        if nx > 0 and t_right > 0:
            t_values.append(t_right)
        if nx < 0 < t_left:
            t_values.append(t_left)
        if ny > 0 and t_bottom > 0:
            t_values.append(t_bottom)
        if ny < 0 < t_top:
            t_values.append(t_top)
        return min(t_values) if t_values else None

    def _calculate_intersection_point(self, player_coords, nx, ny, t):
        intersect_x = player_coords[0] + nx * t
        intersect_y = player_coords[1] + ny * t
        intersect_x = max(self.arrow_margin, min(intersect_x, self.screen_width - self.arrow_margin))
        intersect_y = max(self.arrow_margin, min(intersect_y, self.screen_height - self.arrow_margin))
        return intersect_x, intersect_y

    def _draw_arrow(self, screen, intersect_x, intersect_y, nx, ny):
        arrow_surface = pygame.Surface((self.arrow_size * 2, self.arrow_size * 2), pygame.SRCALPHA)
        angle = math.degrees(math.atan2(-ny, nx)) + 180
        points = [
            (self.arrow_size, self.arrow_size),
            (self.arrow_size - self.arrow_size * math.cos(math.radians(angle + 150)),
             self.arrow_size + self.arrow_size * math.sin(math.radians(angle + 150))),
            (self.arrow_size - self.arrow_size * math.cos(math.radians(angle - 150)),
             self.arrow_size + self.arrow_size * math.sin(math.radians(angle - 150)))
        ]
        pygame.draw.polygon(arrow_surface, self.arrow_color, points)
        screen.blit(arrow_surface, (intersect_x - self.arrow_size, intersect_y - self.arrow_size))

    def draw(self, screen, player, enemies):
        ship_coords = self.camera.get_multiple_ship_screen_coordinates([player] + list(enemies))
        player_coords = ship_coords[player]

        for enemy in enemies:
            if not enemy.alive():
                continue
            enemy_coords = ship_coords[enemy]
            if not self._is_enemy_offscreen(enemy_coords):
                continue

            nx, ny, distance = self._calculate_direction_vector(player_coords, enemy_coords)
            if distance is None:
                continue

            t_left, t_right, t_top, t_bottom = self._calculate_t_values(player_coords, nx, ny)
            t = self._select_intersection_t(nx, ny, t_left, t_right, t_top, t_bottom)
            if t is None:
                continue

            intersect_x, intersect_y = self._calculate_intersection_point(player_coords, nx, ny, t)
            self._draw_arrow(screen, intersect_x, intersect_y, nx, ny)
