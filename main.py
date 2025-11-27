import pygame
import sys
import random
import time
import math
import os
import logging
from scenes import MenuScene, SettingsScene, UpgradesScene, GameScene
from entities import Player, Bullet, Enemy

class Game:
    def __init__(self):
        pygame.init()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.window_res = (800, 480)
        self.window_title = "One In The Chamber"
        self.display = pygame.display.set_mode(self.window_res)
        pygame.display.set_caption(self.window_title)
        pygame.display.set_icon(pygame.Surface((1, 1)))  # placeholder blank icon

        # window state
        self.is_maximized = False
        self.base_window_res = self.window_res
        self.zoom_level = 1.0

        # camera state
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_smooth = 0.1  # lower = smoother
        self.game_zoom = 1.0

        # world settings
        self.WORLD_WIDTH = 3200
        self.WORLD_HEIGHT = 1920
        self.TILE_SIZE = 64

        # fonts
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 36)

        # assets (generate simple pixel sprites at runtime if missing)
        self.assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        if not os.path.isdir(self.assets_dir):
            os.makedirs(self.assets_dir, exist_ok=True)

        # basic colours (more vibrant palette)
        self.white = (255, 255, 255)
        self.black = (10, 10, 14)
        self.red = (255, 75, 75)
        self.green = (120, 255, 160)
        self.blue = (100, 160, 255)
        self.accent = (200, 100, 255)

        # ocean theme colors
        self.ocean_dark = (8, 25, 45)
        self.ocean_med = (15, 35, 60)
        self.ocean_light = (25, 50, 80)
        self.ocean_accent = (100, 200, 255)
        self.foam = (200, 230, 255)
        self.coral = (255, 120, 150)
        self.biolum = (100, 255, 200)  # bioluminescence

        self.generate_assets()
        self.load_sprites()

        # game update loop
        self.running = True
        self.clock = pygame.time.Clock()
        # player movement speed (pixels per frame)
        self.PLAYER_SPEED = 3
        # cooldown system
        self.shoot_cooldown = 0.0  # time until next shot allowed
        self.SHOOT_DELAY = 0.25  # cooldown between shots in seconds
        # quality-of-life globals
        self.popups = []  # floating text popups (e.g., +10)
        self.paused = False
        self.MAGNET_RADIUS = 140
        self.MAGNET_STRENGTH = 0.12
        self.MINIMAP_W = 160
        self.MINIMAP_H = 100
        # shield globals
        self.SHIELD_DURATION = 2.0
        self.shield_end_time = 0.0
        self.shield_active = False
        # default settings (editable from settings menu)
        self.SETTINGS = {
            "player_speed": self.PLAYER_SPEED,
            "enemy_count": 15,
            "enemy_speed": 1.2,
            "fps_limit": 120,
            "max_ammo": 10,
            "bullet_speed": 5,
        }

        self.player = Player(self)
        self.AMMO = self.SETTINGS.get('max_ammo', 10)
        self.MAX_AMMO = self.SETTINGS.get('max_ammo', 10)
        self.reload_cooldown = 0.0
        self.RELOAD_TIME = 1.5  # increased reload time to prevent spamming
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.particles = []
        self.pickups = []

        # simple scene management: 'menu', 'settings', 'game'
        self.scenes = {
            'menu': MenuScene(self),
            'settings': SettingsScene(self),
            'upgrades': UpgradesScene(self),
            'game': GameScene(self),
        }
        self.scene = 'menu'

        # wave system
        self.wave = 1
        self.wave_active = False
        self.wave_timer = 0.0
        self.WAVE_DELAY = 2.5

        # upgrades available in shop
        self.upgrades = [
            {"name": "Increase Max Ammo", "key": "max_ammo", "inc": 5, "cost": 10},
            {"name": "Increase Player Speed", "key": "player_speed", "inc": 1, "cost": 15},
            {"name": "Increase Bullet Speed", "key": "bullet_speed", "inc": 1, "cost": 12},
        ]

    def generate_assets(self):
        # ensure player and a few enemy sprites exist
        player_sprite_path = os.path.join(self.assets_dir, 'player.png')
        gun_sprite_path = os.path.join(self.assets_dir, 'gun.png')
        enemy_sprite_path = os.path.join(self.assets_dir, 'crab.png')
        try:
            if not os.path.isfile(player_sprite_path):
                self.generate_person_sprite(player_sprite_path, size=24)
            if not os.path.isfile(gun_sprite_path):
                self.generate_gun_sprite(gun_sprite_path, size=(30,10))
            if not os.path.isfile(enemy_sprite_path):
                self.generate_crab_sprite(enemy_sprite_path, 20)
        except (pygame.error, IOError) as e:
            logging.error(f"Error generating assets: {e}")

    def load_sprites(self):
        # load sprites
        try:
            player_sprite_path = os.path.join(self.assets_dir, 'player.png')
            gun_sprite_path = os.path.join(self.assets_dir, 'gun.png')
            enemy_sprite_path = os.path.join(self.assets_dir, 'crab.png')
            self.player_sprite = pygame.image.load(player_sprite_path).convert_alpha()
            self.gun_sprite = pygame.image.load(gun_sprite_path).convert_alpha()
            self.enemy_sprites = [pygame.image.load(enemy_sprite_path).convert_alpha()]
        except pygame.error as e:
            logging.error(f"Error loading sprites: {e}")
            self.player_sprite = None
            self.gun_sprite = None
            self.enemy_sprites = []

    def toggle_maximize(self):
        if not self.is_maximized:
            # maximize window
            info = pygame.display.get_desktop_sizes()[0]
            self.display = pygame.display.set_mode(info, pygame.FULLSCREEN)
            self.window_res = info
            self.is_maximized = True
        else:
            # restore to base size
            self.display = pygame.display.set_mode(self.base_window_res)
            self.window_res = self.base_window_res
            self.is_maximized = False

    def set_zoom(self, new_zoom):
        self.zoom_level = max(0.5, min(3.0, new_zoom))
        new_res = (int(self.base_window_res[0] * self.zoom_level), int(self.base_window_res[1] * self.zoom_level))
        self.window_res = new_res
        self.display = pygame.display.set_mode(self.window_res)
        pygame.display.set_caption(f"{self.window_title} (Zoom: {self.zoom_level:.1f}x)")

    def update_camera(self, player_x, player_y):
        # smoothly follow player
        target_x = player_x - (self.window_res[0] / 2) / self.game_zoom
        target_y = player_y - (self.window_res[1] / 2) / self.game_zoom
        
        self.camera_x += (target_x - self.camera_x) * self.camera_smooth
        self.camera_y += (target_y - self.camera_y) * self.camera_smooth
        
        # clamp to world bounds
        self.camera_x = max(0, min(self.camera_x, self.WORLD_WIDTH - self.window_res[0] / self.game_zoom))
        self.camera_y = max(0, min(self.camera_y, self.WORLD_HEIGHT - self.window_res[1] / self.game_zoom))

    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x - self.camera_x) * self.game_zoom
        screen_y = (world_y - self.camera_y) * self.game_zoom
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        world_x = screen_x / self.game_zoom + self.camera_x
        world_y = screen_y / self.game_zoom + self.camera_y
        return world_x, world_y

    def draw_tiles(self):
        # draw tiled background
        tile_color_a = self.ocean_dark
        tile_color_b = self.ocean_med
        
        start_tile_x = int(self.camera_x // self.TILE_SIZE)
        start_tile_y = int(self.camera_y // self.TILE_SIZE)
        end_tile_x = int((self.camera_x + self.window_res[0] / self.game_zoom) // self.TILE_SIZE) + 1
        end_tile_y = int((self.camera_y + self.window_res[1] / self.game_zoom) // self.TILE_SIZE) + 1

        for tx in range(start_tile_x, min(end_tile_x + 1, self.WORLD_WIDTH // self.TILE_SIZE)):
            for ty in range(start_tile_y, min(end_tile_y + 1, self.WORLD_HEIGHT // self.TILE_SIZE)):
                color = tile_color_a if (tx + ty) % 2 == 0 else tile_color_b

                world_x = tx * self.TILE_SIZE
                world_y = ty * self.TILE_SIZE
                screen_x, screen_y = self.world_to_screen(world_x, world_y)

                tile_w = int(self.TILE_SIZE * self.game_zoom) + 1
                tile_h = int(self.TILE_SIZE * self.game_zoom) + 1

                pygame.draw.rect(self.display, color, (screen_x, screen_y, tile_w, tile_h))
                # grid lines with glow
                pygame.draw.rect(self.display, (40, 80, 120), (screen_x, screen_y, tile_w, tile_h), 1)

    def draw_glow(self, pos, radius, color, intensity=0.3):
        """Draw a soft glow effect around a point"""
        x, y = int(pos[0]), int(pos[1])
        for i in range(int(radius), 0, -2):
            alpha = int(255 * intensity * (1 - i / radius))
            c = tuple(min(255, int(col + (255 - col) * 0.3)) for col in color)
            pygame.draw.circle(self.display, c, (x, y), i, 1)

    def generate_pixel_sprite(self, path, size=16, palette=None, symmetric=True):
        # creates a small pixel art PNG using pygame and saves it
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        if palette is None:
            palette = [(255,100,200),(120,255,160),(100,160,255),(255,200,80),(180,100,255),(255,255,255),(60,60,60)]
        for x in range(size):
            for y in range(size):
                # decide pixel
                if random.random() < 0.45:
                    col = random.choice(palette)
                    surf.set_at((x,y), pygame.Color(*col))
                else:
                    surf.set_at((x,y), pygame.Color(0,0,0,0))
        if symmetric:
            # mirror left to right for nicer sprites
            for x in range(size//2):
                for y in range(size):
                    surf.set_at((size-1-x, y), surf.get_at((x,y)))
        # save to disk
        try:
            pygame.image.save(surf, path)
        except (pygame.error, IOError) as e:
            logging.error(f"Error saving pixel sprite: {e}")

    def generate_person_sprite(self, path, size=24):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # colors
        skin = (255, 205, 148)
        shirt = (60, 160, 220)
        pants = (40, 40, 80)
        hair = (40, 20, 10)
        cx = size//2
        # head
        for x in range(cx-3, cx+4):
            for y in range(4, 10):
                surf.set_at((x, y), pygame.Color(*skin))
        # hair
        for x in range(cx-4, cx+5):
            surf.set_at((x, 3), pygame.Color(*hair))
        # eyes
        surf.set_at((cx-2, 7), pygame.Color(0,0,0))
        surf.set_at((cx+2, 7), pygame.Color(0,0,0))
        # torso
        for x in range(cx-4, cx+5):
            for y in range(10, 16):
                surf.set_at((x, y), pygame.Color(*shirt))
        # arms
        for x in range(cx-7, cx-4):
            for y in range(11,14):
                surf.set_at((x, y), pygame.Color(*shirt))
        for x in range(cx+5, cx+8):
            for y in range(11,14):
                surf.set_at((x, y), pygame.Color(*shirt))
        # legs
        for x in range(cx-3, cx):
            for y in range(16, size-2):
                surf.set_at((x, y), pygame.Color(*pants))
        for x in range(cx+1, cx+4):
            for y in range(16, size-2):
                surf.set_at((x, y), pygame.Color(*pants))
        try:
            pygame.image.save(surf, path)
        except (pygame.error, IOError) as e:
            logging.error(f"Error saving person sprite: {e}")

    def generate_crab_sprite(self, path, size=20):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        body = (220, 80, 120)
        eye = (255,255,255)
        leg = (180,60,100)
        cx = size//2
        cy = size//2 + 2
        # body blob
        for x in range(cx-6, cx+7):
            for y in range(cy-4, cy+3):
                # simple ellipse mask
                if ((x-cx)**2)/36 + ((y-cy)**2)/9 <= 1.6:
                    surf.set_at((x,y), pygame.Color(*body))
        # claws
        for x in range(2):
            surf.set_at((2 + x, cy-2), pygame.Color(*leg))
            surf.set_at((size-3 - x, cy-2), pygame.Color(*leg))
        # legs
        for i in range(3):
            lx = cx - 7 + i*2
            surf.set_at((lx, cy+2), pygame.Color(*leg))
            lx2 = cx + 7 - i*2
            surf.set_at((lx2, cy+2), pygame.Color(*leg))
        # eyes on stalks
        surf.set_at((cx-2, cy-5), pygame.Color(*eye))
        surf.set_at((cx+2, cy-5), pygame.Color(*eye))
        surf.set_at((cx-2, cy-6), pygame.Color(0,0,0))
        surf.set_at((cx+2, cy-6), pygame.Color(0,0,0))
        try:
            pygame.image.save(surf, path)
        except (pygame.error, IOError) as e:
            logging.error(f"Error saving crab sprite: {e}")

    def generate_gun_sprite(self, path, size=(28,10)):
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        barrel = (50,50,50)
        grip = (30,30,30)
        # draw barrel (to the right)
        for x in range(0, w-8):
            for y in range(2, h-2):
                surf.set_at((x,y), pygame.Color(*barrel))
        # muzzle
        for x in range(w-8, w-5):
            for y in range(3, h-3):
                surf.set_at((x,y), pygame.Color(200,200,60))
        # grip (downwards near left)
        for x in range(6, 12):
            for y in range(h-4, h):
                surf.set_at((x,y), pygame.Color(*grip))
        try:
            pygame.image.save(surf, path)
        except (pygame.error, IOError) as e:
            logging.error(f"Error saving gun sprite: {e}")

    def spawn_pickup(self, x, y, kind):
        # kind: 'ammo', 'health', 'coin'
        # include visual state for shrink-on-pickup
        self.pickups.append({'x': x, 'y': y, 'kind': kind, 'ttl': 600, 'picked': False, 'size': 6 * self.game_zoom, 'shrink_rate': 0.35})

    def make_particles(self, x, y, color, n=10):
        for i in range(n):
            ang = random.uniform(0, 2*math.pi)
            speed = random.uniform(1.5, 5.5)
            lifetime = random.randint(20, 50)  # longer life for better fade effect
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(ang)*speed,
                'vy': math.sin(ang)*speed,
                'life': lifetime,
                'max_life': lifetime,
                'color': color,
                'size': random.uniform(1.5, 4)  # larger particlesw
            })

    def spawn_enemies(self, count, append=False):
        # spawn enemies relative to the player's current position so gameplay is more intense
        # if append==False replace current enemies, otherwise add to them
        if not append:
            self.enemies.clear()
        px = self.player.x
        py = self.player.y
        # spawn radius around player (min, max)
        min_r = 200
        max_r = 480
        for i in range(count):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(min_r, max_r)
            x = px + math.cos(ang) * dist
            y = py + math.sin(ang) * dist
            # clamp to world bounds
            x = max(0, min(self.WORLD_WIDTH, x))
            y = max(0, min(self.WORLD_HEIGHT, y))
            e = Enemy(self, x, y, self.SETTINGS["enemy_speed"])
            # assign a random enemy sprite if available
            if self.enemy_sprites:
                e.sprite = random.choice(self.enemy_sprites)
            self.enemies.append(e)

    def start_game(self):
        self.scene = 'game'
        self.PLAYER_SPEED = self.SETTINGS['player_speed']
        self.wave = 1
        self.wave_active = True
        self.spawn_enemies(self.SETTINGS['enemy_count'] * self.wave)
        self.bullets.clear()
        self.AMMO = self.SETTINGS.get('max_ammo', 10)
        self.MAX_AMMO = self.SETTINGS.get('max_ammo', 10)
        self.score = 0
        self.player.x, self.player.y = self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2
        # reset camera
        self.camera_x = self.player.x - (self.window_res[0] / 2) / self.game_zoom
        self.camera_y = self.player.y - (self.window_res[1] / 2) / self.game_zoom

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # window controls (available in all scenes)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_maximize()
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.set_zoom(self.zoom_level + 0.1)
                    if event.key == pygame.K_MINUS:
                        self.set_zoom(self.zoom_level - 0.1)
                    if event.key == pygame.K_0:
                        self.set_zoom(1.0)

                # scroll wheel zooming (game zoom only, in game scene)
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # scroll up = zoom in
                        self.game_zoom = min(3.0, self.game_zoom + 0.1)
                    elif event.y < 0:  # scroll down = zoom out
                        self.game_zoom = max(0.5, self.game_zoom - 0.1)

            current_scene = self.scenes[self.scene]
            current_scene.handle_events(events)
            current_scene.update()
            current_scene.draw(self.display)

            # common: FPS display and wave info
            fps_surf = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, self.ocean_accent)
            self.display.blit(fps_surf, (5, 5))
            if self.scene == 'game':
                wave_surf = self.font.render(f"Wave: {self.wave}", True, self.biolum)
                self.display.blit(wave_surf, (self.window_res[0]-120, 5))

            # debug overlay: scene and player coords (helpful when player seems invisible)
            try:
                debug_surf = self.font.render(f"Scene: {self.scene}  Player: {int(self.player.x)},{int(self.player.y)}  HP:{self.player.hp}", True, (200,200,200))
                self.display.blit(debug_surf, (10, self.window_res[1]-24))
            except pygame.error as e:
                logging.error(f"Error rendering debug overlay: {e}")

            # update the full display and cap the frame rate (from settings)
            pygame.display.flip()
            self.clock.tick(self.SETTINGS.get('fps_limit', 60))

if __name__ == '__main__':
    game = Game()
    game.run()
