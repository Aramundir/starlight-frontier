import pygame
import entities, game_engine

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Starlight Frontier")
clock = pygame.time.Clock()

all_ships = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

game_physics = game_engine.Physics.create_for_gameloop()
spawner = game_engine.Spawner.create_for_gameloop(entities)
screen_painter = game_engine.ScreenPainter.create_for_gameloop()

difficulty = 1

player, enemies = spawner.setup_game(all_ships, projectiles, (640, 360), 5, difficulty)

star_surface = screen_painter.create_a_star_surface()

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
            player, enemies = spawner.setup_game(all_ships, projectiles, (640, 360), 5, difficulty)
        pygame.display.flip()
        continue

    if len(enemies) == 0:
        screen_painter.display_end_screen(screen, 'victory')
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            if difficulty < 5:
                difficulty += 1
            player, enemies = spawner.setup_game(all_ships, projectiles, (640, 360), 5, difficulty)
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


    for enemy in enemies[:]:
        if not enemy.alive():
            enemies.remove(enemy)
            continue
        distance, alignment = enemy.approach_target(player.x, player.y)
        if distance < 200 and alignment <= 0.1:
            projs = enemy.fire_projectile()
            for proj in projs:
                projectiles.add(proj)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
