import pygame
import sys
import math

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TILE_SIZE = 40

COLOR_SKY = (92, 148, 252)
COLOR_GROUND_BASE = (200, 76, 12)
COLOR_GROUND_DARK = (100, 30, 0)
COLOR_GROUND_HIGHLIGHT = (235, 130, 60)
COLOR_COIN = (252, 216, 0)
COLOR_COIN_BORDER = (180, 130, 0)
COLOR_COIN_SHINE = (255, 255, 180)
COLOR_HILL = (0, 168, 0)
COLOR_HILL_OUTLINE = (0, 100, 0)
COLOR_CLOUD = (255, 255, 255)
COLOR_FLAG_POLE = (200, 200, 200)
COLOR_FLAG = (0, 168, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_LEVEL_CLEAR = "LEVEL_CLEAR"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"


class SoundManager:
    """Handles audio playback with fallback if files or audio devices are missing."""
    def __init__(self):
        self.sounds = {}
        self.muted = False
        try:
            pygame.mixer.init()
            self.sounds['jump'] = pygame.mixer.Sound('assets/jump.wav')
            self.sounds['coin'] = pygame.mixer.Sound('assets/coin.wav')
            self.sounds['clear'] = pygame.mixer.Sound('assets/clear.wav')
            self.sounds['death'] = pygame.mixer.Sound('assets/death.wav')
        except Exception:
            self.muted = True

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 26, 38)
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -12
        self.gravity = 0.6
        self.is_grounded = False
        self.facing_right = True

    def handle_input(self, keys, sound_mgr):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.is_grounded:
            self.vy = self.jump_power
            self.is_grounded = False
            sound_mgr.play('jump')

    def update(self, platforms):
        self.vy += self.gravity
        if self.vy > 14:
            self.vy = 14

        self.rect.x += int(self.vx)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vx > 0:
                    self.rect.right = platform.rect.left
                elif self.vx < 0:
                    self.rect.left = platform.rect.right

        self.rect.y += int(self.vy)
        self.is_grounded = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy > 0:
                    self.rect.bottom = platform.rect.top
                    self.vy = 0
                    self.is_grounded = True
                elif self.vy < 0:
                    self.rect.top = platform.rect.bottom
                    self.vy = 0

    def draw(self, surface, camera_x):
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        w = self.rect.width
        h = self.rect.height

        red = (220, 30, 20)
        blue = (0, 70, 200)
        skin = (255, 204, 160)
        brown = (100, 40, 0)
        yellow = (250, 210, 0)

        pygame.draw.rect(surface, red, (draw_x, draw_y, w, 8))
        visor_x = draw_x + 16 if self.facing_right else draw_x - 3
        pygame.draw.rect(surface, red, (visor_x, draw_y + 3, 13, 5))

        pygame.draw.rect(surface, skin, (draw_x + 4, draw_y + 8, w - 8, 10))
        hair_x = draw_x + 2 if not self.facing_right else draw_x + 18
        pygame.draw.rect(surface, brown, (hair_x, draw_y + 8, 6, 6))

        eye_x = draw_x + 16 if self.facing_right else draw_x + 7
        stache_x = draw_x + 14 if self.facing_right else draw_x + 4
        pygame.draw.rect(surface, brown, (eye_x, draw_y + 9, 3, 4))
        pygame.draw.rect(surface, brown, (stache_x, draw_y + 13, 8, 4))

        pygame.draw.rect(surface, red, (draw_x + 3, draw_y + 18, w - 6, 8))

        pygame.draw.rect(surface, blue, (draw_x + 4, draw_y + 24, w - 8, 8))
        pygame.draw.rect(surface, yellow, (draw_x + 6, draw_y + 25, 2, 2))
        pygame.draw.rect(surface, yellow, (draw_x + w - 8, draw_y + 25, 2, 2))

        pygame.draw.rect(surface, blue, (draw_x + 4, draw_y + 30, 7, 4))
        pygame.draw.rect(surface, blue, (draw_x + w - 11, draw_y + 30, 7, 4))
        pygame.draw.rect(surface, brown, (draw_x + 2, draw_y + 34, 10, 4))
        pygame.draw.rect(surface, brown, (draw_x + w - 12, draw_y + 34, 10, 4))


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.draw_brick_texture(self.image, width, height)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw_brick_texture(self, surface, width, height):
        surface.fill(COLOR_GROUND_BASE)

        pygame.draw.rect(surface, COLOR_GROUND_DARK, (0, 0, width, height), 2)
        half_h = height // 2
        pygame.draw.line(surface, COLOR_GROUND_DARK, (0, half_h), (width, half_h), 2)

        half_w = width // 2
        pygame.draw.line(surface, COLOR_GROUND_DARK, (half_w, 0), (half_w, half_h), 2)
        quarter_w = width // 4
        pygame.draw.line(surface, COLOR_GROUND_DARK, (quarter_w, half_h), (quarter_w, height), 2)
        pygame.draw.line(surface, COLOR_GROUND_DARK, (width - quarter_w, half_h), (width - quarter_w, height), 2)

        pygame.draw.line(surface, COLOR_GROUND_HIGHLIGHT, (2, 2), (width - 3, 2), 1)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((18, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, COLOR_COIN_BORDER, (0, 0, 18, 22))
        pygame.draw.ellipse(self.image, COLOR_COIN, (2, 2, 14, 18))
        pygame.draw.line(self.image, COLOR_COIN_SHINE, (9, 4), (9, 17), 2)
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        spike_color = (130, 130, 130)
        border_color = (40, 40, 40)
        half = TILE_SIZE // 2

        pygame.draw.polygon(self.image, border_color, [(0, TILE_SIZE), (half // 2, 8), (half, TILE_SIZE)])
        pygame.draw.polygon(self.image, spike_color, [(2, TILE_SIZE), (half // 2, 11), (half - 2, TILE_SIZE)])

        pygame.draw.polygon(self.image, border_color, [(half, TILE_SIZE), (half + half // 2, 8), (TILE_SIZE, TILE_SIZE)])
        pygame.draw.polygon(self.image, spike_color, [(half + 2, TILE_SIZE), (half + half // 2, 11), (TILE_SIZE - 2, TILE_SIZE)])

        self.rect = self.image.get_rect(topleft=(x, y))


class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        pole_height = TILE_SIZE * 2
        self.image = pygame.Surface((TILE_SIZE, pole_height), pygame.SRCALPHA)

        pygame.draw.rect(self.image, COLOR_FLAG_POLE, (8, 10, 4, pole_height - 10))
        pygame.draw.circle(self.image, COLOR_COIN, (10, 10), 6)
        pygame.draw.polygon(self.image, COLOR_FLAG, [(12, 12), (36, 24), (12, 36)])

        self.rect = self.image.get_rect(topleft=(x, y - TILE_SIZE))


LEVELS = [
    # Level 1
    [
        "                                                                     ",
        "                                                                     ",
        "                                                                     ",
        "                                                                     ",
        "                                                                     ",
        "                                                    C   C            ",
        "                 C   C                   C   C     XXXXXXX           ",
        "                XXXXXXX                 XXXXXXX                 G    ",
        "  P                                                            XXXXX ",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ],
    # Level 2
    [
        "                                                                       ",
        "                                                                       ",
        "                                                                       ",
        "                                         C    C                        ",
        "                                        XXXXXXXX                       ",
        "              C                 XXXXXX                                 ",
        "                      XXXXXXX                    XXXXXXXXX      G      ",
        "  P       XXXXXXXXX                                           XXXXX    ",
        "XXXXXXX               XXXXXXX             XXXXXXX                      ",
        "XXXXXXX  S         S  XXXXXXX  S       S  XXXXXXX                      ",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXXX                      "
    ],
    # Level 3
    [
        "                                                                       ",
        "                                                                       ",
        "                                C   C   C                              ",
        "                                                                       ",
        "                    C   C     XXXXXXXXXXXX                             ",
        "                  XXXXXXXXX                        C   C   C           ",
        "          C                                      XXXXXXXXXXXXX         ",
        "  P     XXXXX    XXXXXXXXXXXX                XXX                 G     ",
        "XXXXX                                                          XXXXX   ",
        "XXXXXSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ],
    # Level 4
    [
        "                                                                       ",
        "                                                                       ",
        "                                                                       ",
        "                                                              C        ",
        "                                                             XXX       ",
        "                                                           X           ",
        "                  C   C          C    C             C  C  X       G    ",
        "  P             XXXXXXX         XXXXXXXX           XXXXXX       XXXXX  ",
        "XXXXX                         X                                        ",
        "XXXXXSS  SSS  XXXXXXXXX  SS  SSSSSSSSSSSS    SS  XXXXXXXXXX            ",
        "XXXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXX            "
    ],
    # Level 5
    [
        "                                                                    C  ",
        "                                                                  XXXX ",
        "                                                        C   C  X       ",
        "                                                  X   XXXXXXX          ",
        "                                      C   C     X                      ",
        "                                    XXXXXXX       X                    ",
        "                    C   C                           X                  ",
        "                  XXXXXXX                             X                ",
        "          C   C                                  C      X         G    ",
        "  P     XXXXXXX                                    X  X         XXXXX  ",
        "XXXXX                           XXXX   XXXX   XXXX                     ",
        "XXXXXSSSSSSSSSSSSSSSSSSSSSSS   SSSSSS SSSSSS SSSSSSSSSSSSSSSSSSSXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ]
]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario")
        self.clock = pygame.time.Clock()
        self.sound_mgr = SoundManager()

        self.font_large = pygame.font.SysFont("Undefined", 46, bold=True)
        self.font_medium = pygame.font.SysFont("Undefined", 22, bold=True)
        self.font_small = pygame.font.SysFont("Undefined", 18)

        self.state = STATE_MENU
        self.current_level_idx = 0
        self.score = 0
        self.lives = 3
        self.camera_x = 0

        self.load_level(self.current_level_idx)

    def load_level(self, level_idx):
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()

        level_data = LEVELS[level_idx]
        player_start_x = 100
        player_start_y = 300

        for row_idx, row in enumerate(level_data):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if char == 'X':
                    self.platforms.add(Tile(x, y, TILE_SIZE, TILE_SIZE))
                elif char == 'C':
                    self.coins.add(Coin(x, y))
                elif char == 'S':
                    self.spikes.add(Spike(x, y))
                elif char == 'G':
                    self.goals.add(Goal(x, y))
                elif char == 'P':
                    player_start_x, player_start_y = x, y

        self.player = Player(player_start_x, player_start_y)
        self.camera_x = 0

    def draw_background(self):
        self.screen.fill(COLOR_SKY)

        hill_offset = int(self.camera_x * 0.3) % SCREEN_WIDTH
        for base_x in range(-200, SCREEN_WIDTH + 400, 360):
            x = base_x - hill_offset
            y = SCREEN_HEIGHT - 60
            pygame.draw.ellipse(self.screen, COLOR_HILL_OUTLINE, (x, y - 90, 220, 160))
            pygame.draw.ellipse(self.screen, COLOR_HILL, (x + 3, y - 87, 214, 154))
            pygame.draw.ellipse(self.screen, COLOR_HILL_OUTLINE, (x + 100, y - 60, 14, 22))

        cloud_offset = int(self.camera_x * 0.15) % SCREEN_WIDTH
        for base_x in range(-150, SCREEN_WIDTH + 300, 300):
            cx = base_x - cloud_offset
            cy = 100 + (base_x % 60)
            pygame.draw.circle(self.screen, COLOR_CLOUD, (cx, cy), 20)
            pygame.draw.circle(self.screen, COLOR_CLOUD, (cx + 20, cy - 8), 24)
            pygame.draw.circle(self.screen, COLOR_CLOUD, (cx + 40, cy), 20)
            pygame.draw.rect(self.screen, COLOR_CLOUD, (cx - 5, cy, 50, 15))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = STATE_PLAYING

                elif self.state == STATE_LEVEL_CLEAR:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.current_level_idx += 1
                        if self.current_level_idx < len(LEVELS):
                            self.load_level(self.current_level_idx)
                            self.state = STATE_PLAYING
                        else:
                            self.state = STATE_VICTORY

                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.current_level_idx = 0
                        self.score = 0
                        self.lives = 3
                        self.load_level(self.current_level_idx)
                        self.state = STATE_PLAYING

    def update(self):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.sound_mgr)
        self.player.update(self.platforms)

        target_cam_x = self.player.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x += (target_cam_x - self.camera_x) * 0.1
        self.camera_x = max(0, self.camera_x)

        collected_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        for _ in collected_coins:
            self.score += 100
            self.sound_mgr.play('coin')

        hit_hazard = pygame.sprite.spritecollide(self.player, self.spikes, False)
        fell_in_pit = self.player.rect.top > SCREEN_HEIGHT + 50

        if hit_hazard or fell_in_pit:
            self.sound_mgr.play('death')
            self.lives -= 1
            if self.lives > 0:
                self.load_level(self.current_level_idx)
            else:
                self.state = STATE_GAME_OVER

        if pygame.sprite.spritecollide(self.player, self.goals, False):
            self.sound_mgr.play('clear')
            self.state = STATE_LEVEL_CLEAR

    def draw_hud(self):
        world_str = f"WORLD 1-{self.current_level_idx + 1}"
        score_str = f"SCORE  {self.score:06d}"
        lives_str = f"LIVES  x{self.lives}"

        bar_text = f"MARIO     {score_str}     {world_str}     {lives_str}"
        shadow = self.font_medium.render(bar_text, True, COLOR_BLACK)
        text = self.font_medium.render(bar_text, True, COLOR_WHITE)
        self.screen.blit(shadow, (22, 18))
        self.screen.blit(text, (20, 16))

    def draw_overlay(self, title, subtitle, prompt):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_large.render(title, True, COLOR_WHITE)
        sub_surf = self.font_medium.render(subtitle, True, COLOR_COIN)
        prompt_surf = self.font_small.render(prompt, True, COLOR_WHITE)

        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)))
        self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

    def draw(self):
        self.draw_background()

        if self.state == STATE_PLAYING:
            for sprite in self.platforms:
                self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
            for sprite in self.coins:
                self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
            for sprite in self.spikes:
                self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
            for sprite in self.goals:
                self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))

            self.player.draw(self.screen, self.camera_x)

            self.draw_hud()

        elif self.state == STATE_MENU:
            self.draw_overlay("SUPER MARIO", "Arrow Keys / A, D to Move  |  SPACE to Jump", "Press ENTER or SPACE to Start")

        elif self.state == STATE_LEVEL_CLEAR:
            self.draw_overlay(f"LEVEL {self.current_level_idx + 1} CLEARED!", f"Score: {self.score}", "Press SPACE for Next Level")

        elif self.state == STATE_GAME_OVER:
            self.draw_overlay("GAME OVER", f"Final Score: {self.score}", "Press SPACE to Restart")

        elif self.state == STATE_VICTORY:
            self.draw_overlay("COURSE COMPLETE!", f"Final Score: {self.score}", "Press SPACE to Play Again")

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
