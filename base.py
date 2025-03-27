import pygame
import random
import entities

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player = entities.Ship.create(400, 300, 5, 'player')
all_sprites.add(player)

enemies = []

for number in range(5):
    x = random.randint(0, 750)
    y = random.randint(0, 550)
    enemy = entities.Ship.create(x, y, 3, 'enemy')
    all_sprites.add(enemy)
    enemies.append(enemy)

star_surface = pygame.Surface((800, 600))
star_surface.fill((0, 0, 0))
for star in range(100):
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
    if keys[pygame.K_q]:
        player.accelerate_lateral('left')
    if keys[pygame.K_e]:
        player.accelerate_lateral('right')
    if keys[pygame.K_a]:
        player.turn('left')
    if keys[pygame.K_d]:
        player.turn('right')
    if keys[pygame.K_x]:
        player.brake()

    all_sprites.update()

    screen.blit(star_surface, (0, 0))

    all_sprites.draw(screen)


    for enemy in enemies:
        enemy.approach_target(player.x, player.y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()