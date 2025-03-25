import pygame
import random
import entities

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

ship_stats = {
    'x': 400,
    'y': 300,
    'angle': 0,
    'speed': 0,
    'max_speed': 10,
}

player = entities.Ship.create(**ship_stats)

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
        player.accelerate('forward')
    if keys[pygame.K_s]:
        player.accelerate('backward')
    if keys[pygame.K_a]:
        player.turn('left')
    if keys[pygame.K_d]:
        player.turn('right')

    player.move()

    screen.fill((0, 0, 0))
    screen.blit(star_surface, (0, 0))

    player.render(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()