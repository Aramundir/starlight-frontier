import pygame
from pygame import SRCALPHA

import entities, game_engine

pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

all_ships = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

game_physics = game_engine.Physics.create_for_gameloop()
game_master = game_engine.GameMaster.create_for_gameloop(entities)
screen_painter = game_engine.ScreenPainter.create_for_gameloop()
star_surface = screen_painter.create_a_star_surface()

difficulty = 1
player, enemies = game_master.setup_game(all_ships, projectiles, (2000, 2000), 5, difficulty)

camera = game_engine.Camera.create_for_gameloop(screen_width, screen_height, player)
hud = game_engine.HUD.create_for_gameloop(camera)



running = True
while running:
    dt = clock.get_time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not player.alive():
        screen_painter.display_end_screen(screen, 'game_over')
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            difficulty = 1
            player, enemies = game_master.setup_game(all_ships, projectiles, (2000, 2000), 5, difficulty)
            camera = game_engine.Camera.create_for_gameloop(screen_width, screen_height, player)
            hud = game_engine.HUD.create_for_gameloop(camera)
        pygame.display.flip()
        continue

    if len(enemies) == 0:
        screen_painter.display_end_screen(screen, 'victory')
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            if difficulty < 5:
                difficulty += 1
            player, enemies = game_master.setup_game(all_ships, projectiles, (2000, 2000), 5, difficulty)
            camera = game_engine.Camera.create_for_gameloop(screen_width, screen_height, player)
            hud = game_engine.HUD.create_for_gameloop(camera)
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

    camera.update(4000, 4000)

    screen.fill((0, 0, 0))
    screen.blit(star_surface, (-camera.x, -camera.y))
    for ship in all_ships:
        ship.rect.center = (ship.x - camera.x, ship.y - camera.y)
    for proj in projectiles:
        proj.rect.center = (proj.x - camera.x, proj.y - camera.y)

    all_ships.draw(screen)
    projectiles.draw(screen)
    hud.draw(screen, player, enemies)


    for enemy in enemies[:]:
        if not enemy.alive():
            enemies.remove(enemy)
            continue
        distance, alignment = enemy.approach_target(player.x, player.y)
        if distance < 500 and alignment <= 0.2:
            projs = enemy.fire_projectile()
            for proj in projs:
                projectiles.add(proj)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
