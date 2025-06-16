import math
import random
import pygame


class Physics(object):
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
            for proj2 in proj_list[i+1:]:
                if proj2.alive() and proj1.rect.colliderect(proj2.rect):
                    if pygame.sprite.collide_mask(proj1, proj2):
                        proj1.kill()
                        proj2.kill()

    def check_world_bounds(self, ship):
        bounds_actions = {
            'left': lambda: setattr(ship, 'x', 0) or setattr(ship, 'x_vector', max(0, ship.x_vector)),
            'right': lambda: setattr(ship, 'x', self.world_width) or setattr(ship, 'x_vector', min(0, ship.x_vector)),
            'top': lambda: setattr(ship, 'y', 0) or setattr(ship, 'y_vector', max(0, ship.y_vector)),
            'bottom': lambda: setattr(ship, 'y', self.world_height) or setattr(ship, 'y_vector', min(0, ship.y_vector))
        }
        if ship.x < 0:
            bounds_actions['left']()
        if ship.x > self.world_width:
            bounds_actions['right']()
        if ship.y < 0:
            bounds_actions['top']()
        if ship.y > self.world_height:
            bounds_actions['bottom']()
        ship.rect.center = (ship.x, ship.y)


class Spawner(object):
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
        player = self.entities.Ship.create(player_pos[0], player_pos[1], 'player', 'fighter')
        all_ships.add(player)
        enemies = self.spawn_enemies(num_enemies, player_pos, difficulty)
        all_ships.add(enemies)
        return player, enemies


class ScreenPainter(object):
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
