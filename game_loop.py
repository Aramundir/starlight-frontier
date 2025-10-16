import pygame
import entities
import game_engine

class Game:
    def __init__(self, screen_width=1600, screen_height=900, world_width=8000, world_height=8000):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Starlight Frontier")
        self.clock = pygame.time.Clock()

        self.game_physics = game_engine.Physics.create_for_gameloop(self.world_width, self.world_height)
        self.game_master = game_engine.GameMaster.create_for_gameloop(entities, self.world_width, self.world_height)
        self.screen_painter = game_engine.ScreenPainter.create_for_gameloop(self.screen_width, self.screen_height, self.world_width, self.world_height)
        self.star_surface = self.screen_painter.create_a_star_surface()

        self.game_state = 'menu'
        self.difficulty = 1
        self.all_ships = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.player = None
        self.enemies = []
        self.camera = None
        self.hud = None

    def start_game(self, ship_class):
        number_of_enemies = 1
        self.player, self.enemies = self.game_master.setup_game(
            self.all_ships, self.projectiles, (self.world_width // 2, self.world_height // 2), number_of_enemies, self.difficulty, ship_class
        )
        self.camera = game_engine.Camera.create_for_gameloop(self.screen_width, self.screen_height, self.player)
        self.hud = game_engine.HUD.create_for_gameloop(self.camera)

    def run(self):
        running = True
        while running:
            dt = self.clock.get_time()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if self.game_state == 'menu':
                self._handle_menu(events)
            if self.game_state == 'paused':
                self._handle_paused(events)
            if self.game_state == 'playing':
                self._handle_playing(dt, events)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _handle_menu(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.start_game('scout')
                    self.game_state = 'playing'
                if event.key == pygame.K_2:
                    self.start_game('fighter')
                    self.game_state = 'playing'
                if event.key == pygame.K_3:
                    self.start_game('heavy_fighter')
                    self.game_state = 'playing'

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.star_surface, (-self.screen_width // 2, -self.screen_height // 2))
        self.screen_painter.display_menu(self.screen)

    def _handle_paused(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = 'playing'
                if event.key == pygame.K_r:
                    self.difficulty = 1
                    self.game_state = 'menu'

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.star_surface, (-self.camera.x, -self.camera.y))
        for ship in self.all_ships:
            ship.rect.center = (ship.x - self.camera.x, ship.y - self.camera.y)
        for proj in self.projectiles:
            proj.rect.center = (proj.x - self.camera.x, proj.y - self.camera.y)
        self.all_ships.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.hud.draw(self.screen, self.player, self.enemies)
        self.screen_painter.display_pause(self.screen)

    def _handle_playing(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = 'paused'

        if not self.player.alive():
            self.screen_painter.display_end_screen(self.screen, 'game_over')
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.difficulty = 1
                self.game_state = 'menu'
            return

        if len(self.enemies) == 0:
            self.screen_painter.display_end_screen(self.screen, 'victory')
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                if self.difficulty < 5:
                    self.difficulty += 1
                self.game_state = 'menu'
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.start_to_accelerate('forward')
        if keys[pygame.K_s]:
            self.player.start_to_accelerate('backward')
        if keys[pygame.K_q]:
            self.player.start_to_accelerate('left')
        if keys[pygame.K_e]:
            self.player.start_to_accelerate('right')
        if keys[pygame.K_a]:
            self.player.start_to_turn('left')
        if keys[pygame.K_d]:
            self.player.start_to_turn('right')
        if keys[pygame.K_x]:
            self.player.start_to_brake()
        if keys[pygame.K_z]:
            self.player.start_to_brake_rotation()
        if keys[pygame.K_SPACE]:
            projs = self.player.fire()
            for proj in projs:
                self.projectiles.add(proj)

        self.all_ships.update(dt)
        self.projectiles.update()

        self.game_physics.check_for_ship_collision(self.all_ships)
        self.game_physics.check_for_projectile_collisions(self.projectiles, self.all_ships)

        self.camera.update(self.world_width, self.world_height)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.star_surface, (-self.camera.x, -self.camera.y))
        for ship in self.all_ships:
            ship.rect.center = (ship.x - self.camera.x, ship.y - self.camera.y)
        for proj in self.projectiles:
            proj.rect.center = (proj.x - self.camera.x, proj.y - self.camera.y)
        self.all_ships.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.hud.draw (self.screen, self.player, self.enemies)

        for enemy in self.enemies[:]:
            combat_range = 500
            optimal_alignment = 0.2
            if not enemy.alive():
                self.enemies.remove(enemy)
                continue
            distance, alignment = enemy.approach_target(self.player.x, self.player.y)
            if distance < combat_range and alignment <= optimal_alignment:
                projs = enemy.fire()
                for proj in projs:
                    self.projectiles.add(proj)


if __name__ == '__main__':
    game = Game()
    game.run()