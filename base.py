import pygame
import random
import entities, game_engine

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

all_ships = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
player = entities.Ship.create(640, 360, 'player', 'heavy_fighter')
all_ships.add(player)

game_physics = game_engine.Physics.create_for_gameloop()
enemy_spawner = game_engine.Spawner.create_for_gameloop()

enemies = enemy_spawner.spawn_enemies(5, (640, 360))

all_ships.add(enemies)

star_surface = pygame.Surface((1280, 720))
star_surface.fill((0, 0, 0))
for star in range(150):
    pygame.draw.circle(star_surface, (255, 255, 255),
                      (random.randint(0, 1280), random.randint(0, 720)), 1)


running = True
while running:
    dt = clock.get_time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not player.alive():
        font = pygame.font.SysFont(None, 48)
        text = font.render("Game Over - Press R to Restart", True, (255, 0, 0))
        screen.blit(text, (400, 360))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            all_ships.empty()
            projectiles.empty()
            player = entities.Ship.create(640, 360, 'player', 'heavy_fighter')
            all_ships.add(player)
            enemies = enemy_spawner.spawn_enemies(5, (640, 360))
            all_ships.add(enemies)
        pygame.display.flip()
        continue

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
    if keys[pygame.K_SPACE]:
        projs = player.fire_projectile()
        for proj in projs:
            projectiles.add(proj)

    all_ships.update(dt)
    projectiles.update()

    game_physics.check_for_ship_collision(all_ships)
    game_physics.check_for_projectile_collisions(projectiles, all_ships)

    screen.blit(star_surface, (0, 0))

    all_ships.draw(screen)
    projectiles.draw(screen)


    for enemy in enemies:
        distance, aligmnent = enemy.approach_target(player.x, player.y)
        if distance < 200 and aligmnent >= 0.9:
            projs = enemy.fire_projectile()
            for proj in projs:
                projectiles.add(proj)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()