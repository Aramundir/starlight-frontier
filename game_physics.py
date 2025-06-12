import math
import random
import pygame


def check_for_ship_collision(all_ships):
    for ship1 in all_ships:
        rect_collisions = pygame.sprite.spritecollide(ship1, all_ships, False, pygame.sprite.collide_rect)
        for ship2 in rect_collisions:
            if ship1 != ship2:
                if pygame.sprite.collide_mask(ship1, ship2):
                    resolve_ship_collision(ship1, ship2)


def resolve_ship_collision(ship1, ship2):
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