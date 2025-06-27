import pygame
import entities
import game_engine

class Game:
    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Starlight Frontier")
        self.clock = pygame.time.Clock()

        self.game_physics = game_engine.Physics.create_for_gameloop()
        self.game_master = game_engine.GameMaster.create_for_gameloop(entities)
        self.screen_painter = game_engine.ScreenPainter.create_for_gameloop(self.screen_width, self.screen_height)
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
        self.player, self.enemies = self.game_master.setup_game(
            self.all_ships, self.projectiles, (2000, 2000), 5, self.difficulty, ship_class
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
        self.screen.blit(self.star_surface, (-640, -360))  # Center starfield on 1280x720
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
            self.player.accelerate('forward')
        if keys[pygame.K_s]:
            self.player.accelerate('backward')
        if keys[pygame.K_q]:
            self.player.accelerate_lateral('left')
        if keys[pygame.K_e]:
            self.player.accelerate_lateral('right')
        if keys[pygame.K_a]:
            self.player.turn('left')
        if keys[pygame.K_d]:
            self.player.turn('right')
        if keys[pygame.K_x]:
            self.player.brake()
        if keys[pygame.K_SPACE]:
            projs = self.player.fire()
            for proj in projs:
                self.projectiles.add(proj)

        self.all_ships.update(dt)
        self.projectiles.update()

        self.game_physics.check_for_ship_collision(self.all_ships)
        self.game_physics.check_for_projectile_collisions(self.projectiles, self.all_ships)

        self.camera.update(4000, 4000)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.star_surface, (-self.camera.x, -self.camera.y))
        for ship in self.all_ships:
            ship.rect.center = (ship.x - self.camera.x, ship.y - self.camera.y)
        for proj in self.projectiles:
            proj.rect.center = (proj.x - self.camera.x, proj.y - self.camera.y)
        self.all_ships.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.hud.draw(self.screen, self.player, self.enemies)

        for enemy in self.enemies[:]:
            if not enemy.alive():
                self.enemies.remove(enemy)
                continue
            distance, alignment = enemy.approach_target(self.player.x, self.player.y)
            if distance < 500 and alignment <= 0.2:
                projs = enemy.fire()
                for proj in projs:
                    self.projectiles.add(proj)


if __name__ == '__main__':
    game = Game()
    game.run()