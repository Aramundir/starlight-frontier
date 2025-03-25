import pygame
import math
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

ship_x, ship_y = 400, 300
ship_angle = 0
ship_speed = 0
max_speed = 5

star_surface = pygame.Surface((800, 600))
star_surface.fill((0, 0, 0))
for _ in range(100):
    pygame.draw.circle(star_surface, (255, 255, 255),
                      (random.randint(0, 800), random.randint(0, 600)), 1)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        ship_speed = min(ship_speed + 0.1, max_speed)
    if keys[pygame.K_s]:
        ship_speed = max(ship_speed - 0.1, 0)
    if keys[pygame.K_a]:
        ship_angle += 5
    if keys[pygame.K_d]:
        ship_angle -= 5

    ship_x += math.cos(math.radians(ship_angle)) * ship_speed
    ship_y -= math.sin(math.radians(ship_angle)) * ship_speed

    ship_x = ship_x % 800
    ship_y = ship_y % 600

    screen.fill((0, 0, 0))
    screen.blit(star_surface, (0, 0))

    points = [
        (ship_x + 20 * math.cos(math.radians(ship_angle)), ship_y - 20 * math.sin(math.radians(ship_angle))),
        (ship_x + 10 * math.cos(math.radians(ship_angle + 135)), ship_y - 10 * math.sin(math.radians(ship_angle + 135))),
        (ship_x + 10 * math.cos(math.radians(ship_angle - 135)), ship_y - 10 * math.sin(math.radians(ship_angle - 135)))
    ]
    pygame.draw.polygon(screen, (0, 0, 255), points)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()