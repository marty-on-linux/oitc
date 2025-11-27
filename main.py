import pygame
import sys
import random
import time
import math
import os

class Game:
    def __init__(self):
        pygame.init()

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

        self.player = Player(self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2)
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
        self.scene = 'menu'

        # wave system
        self.wave = 1
        self.wave_active = False
        self.wave_timer = 0.0
        self.WAVE_DELAY = 2.5

        # menu state
        self.menu_items = ["Start Game", "Upgrades", "Settings", "Quit"]
        self.menu_index = 0

        # settings menu state
        self.settings_items = ["player_speed", "enemy_count", "enemy_speed", "fps_limit"]
        self.settings_index = 0
        # upgrades available in shop
        self.upgrades = [
            {"name": "Increase Max Ammo", "key": "max_ammo", "inc": 5, "cost": 10},
            {"name": "Increase Player Speed", "key": "player_speed", "inc": 1, "cost": 15},
            {"name": "Increase Bullet Speed", "key": "bullet_speed", "inc": 1, "cost": 12},
        ]
        self.upgrades_index = 0

    def generate_assets(self):
        # ensure player and a few enemy sprites exist
        player_sprite_path = os.path.join(self.assets_dir, 'player.png')
        gun_sprite_path = os.path.join(self.assets_dir, 'gun.png')
        enemy_sprite_path = os.path.join(self.assets_dir, 'crab.png')
        if not os.path.isfile(player_sprite_path):
            self.generate_person_sprite(player_sprite_path, size=24)
        if not os.path.isfile(gun_sprite_path):
            self.generate_gun_sprite(gun_sprite_path, size=(30,10))
        if not os.path.isfile(enemy_sprite_path):
            self.generate_crab_sprite(enemy_sprite_path, 20)
    
    def load_sprites(self):
        # load sprites
        try:
            player_sprite_path = os.path.join(self.assets_dir, 'player.png')
            gun_sprite_path = os.path.join(self.assets_dir, 'gun.png')
            enemy_sprite_path = os.path.join(self.assets_dir, 'crab.png')
            self.player_sprite = pygame.image.load(player_sprite_path).convert_alpha()
            self.gun_sprite = pygame.image.load(gun_sprite_path).convert_alpha()
            self.enemy_sprites = [pygame.image.load(enemy_sprite_path).convert_alpha()]
        except Exception:
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
        except Exception:
            pass

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
        except Exception:
            pass

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
        except Exception:
            pass

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
        except Exception:
            pass

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
            e = Enemy(x, y, self.SETTINGS["enemy_speed"])
            # assign a random enemy sprite if available
            if self.enemy_sprites:
                e.sprite = random.choice(self.enemy_sprites)
            self.enemies.append(e)

    def run(self):
        while self.running:
            # clear screen first, then handle events, draw, and flip
            self.display.fill(self.ocean_dark)
            for event in pygame.event.get():
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

                # scene-specific input
                if self.scene == 'menu':
                    # keyboard navigation
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                        if event.key == pygame.K_DOWN:
                            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            choice = self.menu_items[self.menu_index]
                            if choice == 'Start Game':
                                # apply settings
                                self.PLAYER_SPEED = self.SETTINGS['player_speed']
                                self.wave = 1
                                self.wave_active = True
                                self.spawn_enemies(self.SETTINGS['enemy_count'] * self.wave)
                                self.bullets.clear()
                                self.AMMO = self.SETTINGS.get('max_ammo', 10)
                                self.MAX_AMMO = self.SETTINGS.get('max_ammo', 10)
                                self.score = 0
                                self.player.x, self.player.y = self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2
                                self.scene = 'game'
                            elif choice == 'Upgrades':
                                self.scene = 'upgrades'
                            elif choice == 'Settings':
                                self.scene = 'settings'
                            elif choice == 'Quit':
                                pygame.quit()
                                sys.exit()
                    # mouse click support for menu buttons
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        for i, item in enumerate(self.menu_items):
                            w, h = self.font.size(item)
                            bx = self.window_res[0]//2 - w//2
                            by = 150 + i*30
                            rect = pygame.Rect(bx - 8, by - 4, w + 16, h + 8)
                            if rect.collidepoint(mx, my):
                                choice = item
                                if choice == 'Start Game':
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
                                    self.scene = 'game'
                                    self.camera_x = self.player.x - (self.window_res[0] / 2) / self.game_zoom
                                    self.camera_y = self.player.y - (self.window_res[1] / 2) / self.game_zoom
                                    self.scene = 'game'
                                elif choice == 'Upgrades':
                                    self.scene = 'upgrades'
                                elif choice == 'Settings':
                                    self.scene = 'settings'
                                elif choice == 'Quit':
                                    pygame.quit()
                                    sys.exit()

                elif self.scene == 'settings':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            key = self.settings_items[self.settings_index]
                            if key == 'player_speed':
                                self.SETTINGS['player_speed'] = max(1, self.SETTINGS['player_speed'] - 1)
                            elif key == 'enemy_count':
                                self.SETTINGS['enemy_count'] = max(1, self.SETTINGS['enemy_count'] - 1)
                            elif key == 'enemy_speed':
                                self.SETTINGS['enemy_speed'] = max(0.1, round(self.SETTINGS['enemy_speed'] - 0.1, 2))
                            elif key == 'fps_limit':
                                self.SETTINGS['fps_limit'] = max(15, self.SETTINGS['fps_limit'] - 5)
                        if event.key == pygame.K_RIGHT:
                            key = self.settings_items[self.settings_index]
                            if key == 'player_speed':
                                self.SETTINGS['player_speed'] = min(20, self.SETTINGS['player_speed'] + 1)
                            elif key == 'enemy_count':
                                self.SETTINGS['enemy_count'] = min(50, self.SETTINGS['enemy_count'] + 1)
                            elif key == 'enemy_speed':
                                self.SETTINGS['enemy_speed'] = min(10.0, round(self.SETTINGS['enemy_speed'] + 0.1, 2))
                            elif key == 'fps_limit':
                                self.SETTINGS['fps_limit'] = min(240, self.SETTINGS['fps_limit'] + 5)
                        if event.key == pygame.K_UP:
                            self.settings_index = (self.settings_index - 1) % len(self.settings_items)
                        if event.key == pygame.K_DOWN:
                            self.settings_index = (self.settings_index + 1) % len(self.settings_items)
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                            self.scene = 'menu'

                elif self.scene == 'upgrades':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.upgrades_index = (self.upgrades_index - 1) % len(self.upgrades)
                        if event.key == pygame.K_DOWN:
                            self.upgrades_index = (self.upgrades_index + 1) % len(self.upgrades)
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            up = self.upgrades[self.upgrades_index]
                            if self.score >= up['cost']:
                                self.score -= up['cost']
                                self.SETTINGS[up['key']] = self.SETTINGS.get(up['key'], 0) + up['inc']
                                # apply some immediate effects
                                if up['key'] == 'max_ammo':
                                    self.MAX_AMMO = self.SETTINGS['max_ammo']
                                if up['key'] == 'player_speed':
                                    self.PLAYER_SPEED = self.SETTINGS['player_speed']
                        if event.key == pygame.K_ESCAPE:
                            self.scene = 'menu'
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        for i, up in enumerate(self.upgrades):
                            w, h = self.font.size(up['name'])
                            bx = 120
                            by = 120 + i*40
                            rect = pygame.Rect(bx - 8, by - 4, 400, h + 8)
                            if rect.collidepoint(mx, my):
                                if self.score >= up['cost']:
                                    self.score -= up['cost']
                                    self.SETTINGS[up['key']] = self.SETTINGS.get(up['key'], 0) + up['inc']
                                    if up['key'] == 'max_ammo':
                                        self.MAX_AMMO = self.SETTINGS['max_ammo']
                                    if up['key'] == 'player_speed':
                                        self.PLAYER_SPEED = self.SETTINGS['player_speed']

                elif self.scene == 'game':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # left click
                            now = time.time()
                            # check shooting cooldown and ensure not reloading
                            if not self.paused and now >= self.shoot_cooldown and now >= self.reload_cooldown:
                                mouse_x, mouse_y = pygame.mouse.get_pos()
                                # convert screen coords to world coords
                                world_mx, world_my = self.screen_to_world(mouse_x, mouse_y)
                                dir_x = world_mx - self.player.x
                                dir_y = world_my - self.player.y
                                length = (dir_x**2 + dir_y**2) ** 0.5
                                if length != 0:
                                    dir_x /= length
                                    dir_y /= length
                                # decrement ammo properly
                                if self.AMMO > 0:
                                    self.AMMO -= 1
                                    self.bullets.append(Bullet(self.player.x, self.player.y, (dir_x, dir_y)))
                                    self.shoot_cooldown = now + self.SHOOT_DELAY  # set cooldown
                                else:
                                    # out of ammo sound or feedback could go here
                                    pass
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # reload when R pressed (with a tiny cooldown)
                            now = time.time()
                            if now >= self.reload_cooldown and self.AMMO < self.MAX_AMMO:
                                self.AMMO = self.MAX_AMMO
                                self.reload_cooldown = now + self.RELOAD_TIME
                        # pause toggle
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                        # debug: spawn 20 additional enemies (append)
                        if event.key == pygame.K_2:
                            self.spawn_enemies(20, append=True)
                        # shield activation
                        if event.key == pygame.K_f:
                            now = time.time()
                            # start shield for SHIELD_DURATION
                            self.shield_end_time = now + self.SHIELD_DURATION
                            self.shield_active = True

            # handle continuous key presses for movement (only in game scene)
            keys = pygame.key.get_pressed()
            if self.scene == 'game':
                speed = self.SETTINGS['player_speed']
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.player.x -= speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.player.x += speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.player.y -= speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.player.y += speed
                if keys[pygame.K_ESCAPE]:
                    # return to menu
                    self.scene = 'menu'

            # keep player in world bounds
            self.player.clamp(self.WORLD_WIDTH, self.WORLD_HEIGHT)

            # Scene drawing
            if self.scene == 'menu':
                # draw menu
                title_font = pygame.font.SysFont(None, 48)
                title = title_font.render(self.window_title, True, self.biolum)
                self.display.blit(title, (self.window_res[0]//2 - title.get_width()//2, 50))
                self.draw_glow((self.window_res[0]//2, 50 + title.get_height()//2), 80, self.biolum, 0.15)
                for i, item in enumerate(self.menu_items):
                    color = self.biolum if i == self.menu_index else self.foam
                    it_surf = self.font.render(item, True, color)
                    self.display.blit(it_surf, (self.window_res[0]//2 - it_surf.get_width()//2, 150 + i*30))

            elif self.scene == 'settings':
                title_font = pygame.font.SysFont(None, 42)
                title = title_font.render('Settings', True, self.biolum)
                self.display.blit(title, (self.window_res[0]//2 - title.get_width()//2, 40))
                for i, key in enumerate(self.settings_items):
                    val = self.SETTINGS[key]
                    label = f"{key}: {val}"
                    color = self.biolum if i == self.settings_index else self.foam
                    surf = self.font.render(label, True, color)
                    self.display.blit(surf, (100, 120 + i*30))

            elif self.scene == 'upgrades':
                title = self.big_font.render('Upgrades', True, self.biolum)
                self.display.blit(title, (self.window_res[0]//2 - title.get_width()//2, 40))
                for i, up in enumerate(self.upgrades):
                    name = up['name']
                    cost = up['cost']
                    label = f"{name}  -  Cost: {cost}"
                    color = self.biolum if i == self.upgrades_index else self.foam
                    surf = self.font.render(label, True, color)
                    self.display.blit(surf, (120, 120 + i*40))
                # show player score as currency
                cur = self.font.render(f"Coins: {self.score}", True, self.biolum)
                self.display.blit(cur, (self.window_res[0]-120, 20))

            elif self.scene == 'game':
                # update camera to follow player FIRST, before rendering anything
                self.update_camera(self.player.x, self.player.y)
                # update shield state
                try:
                    if self.shield_end_time <= time.time():
                        self.shield_active = False
                except Exception:
                    self.shield_active = False

                # draw tiled world background
                self.draw_tiles()

                # paused drawing: when paused, render current scene but skip updates
                if self.paused:
                    for e in self.enemies:
                        e.draw()
                    for b in self.bullets:
                        b.draw()
                    for p in self.pickups:
                        kind = p['kind']
                        color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
                        screen_px, screen_py = self.world_to_screen(p['x'], p['y'])
                        sz = int(p.get('size', 6 * self.game_zoom))
                        pygame.draw.circle(self.display, color, (int(screen_px), int(screen_py)), sz)
                    for q in self.particles:
                        screen_px, screen_py = self.world_to_screen(q['x'], q['y'])
                        alpha_ratio = q['life'] / q['max_life'] if q.get('max_life') else 1
                        fade_size = int(q.get('size', 2) * self.game_zoom * alpha_ratio)
                        if fade_size > 0:
                            pygame.draw.circle(self.display, q['color'], (int(screen_px), int(screen_py)), fade_size)
                    # draw player, gun and HUD (static)
                    self.player.draw()
                    if 'gun_sprite' in globals() and self.gun_sprite:
                        mx, my = pygame.mouse.get_pos()
                        world_mx, world_my = self.screen_to_world(mx, my)
                        ang = math.degrees(math.atan2(world_my - self.player.y, world_mx - self.player.x))
                        w, h = self.gun_sprite.get_size()
                        w_scaled = int(w * self.game_zoom)
                        h_scaled = int(h * self.game_zoom)
                        gun_scaled = pygame.transform.scale(self.gun_sprite, (w_scaled, h_scaled))
                        rot = pygame.transform.rotate(gun_scaled, -ang)
                        player_screen_x, player_screen_y = self.world_to_screen(self.player.x, self.player.y)
                        rrect = rot.get_rect(center=(int(player_screen_x), int(player_screen_y)))
                        self.display.blit(rot, rrect.topleft)
                    # HUD (ammo / reload progress)
                    now = time.time()
                    if now < self.reload_cooldown:
                        remaining = max(0, self.reload_cooldown - now)
                        progress = 1 - (remaining / self.RELOAD_TIME)
                        bar_w = 120
                        bar_h = 10
                        bx = 5
                        by = 25
                        pygame.draw.rect(self.display, self.ocean_med, (bx, by, bar_w, bar_h))
                        pygame.draw.rect(self.display, self.foam, (bx, by, int(bar_w * progress), bar_h))
                        reload_surf = self.font.render("Reloading...", True, self.coral)
                        self.display.blit(reload_surf, (5, 25 + bar_h + 2))
                    else:
                        ammo_surf = self.font.render(f"Ammo: {self.AMMO} (R to reload)", True, self.foam)
                        self.display.blit(ammo_surf, (5, 25))
                    # draw popups
                    for popup in self.popups[:]:
                        popup['y'] += popup.get('vy', -0.4)
                        popup['life'] -= 1
                        if popup['life'] <= 0:
                            self.popups.remove(popup)
                            continue
                        sx, sy = self.world_to_screen(popup['x'], popup['y'])
                        alpha = max(0, int(255 * (popup['life'] / 60)))
                        txt = self.font.render(popup['text'], True, popup.get('color', self.foam))
                        self.display.blit(txt, (int(sx - txt.get_width() / 2), int(sy)))
                    # minimap (static)
                    map_x = self.window_res[0] - self.MINIMAP_W - 8
                    map_y = 8
                    pygame.draw.rect(self.display, self.ocean_med, (map_x, map_y, self.MINIMAP_W, self.MINIMAP_H))
                    pygame.draw.rect(self.display, self.foam, (map_x, map_y, self.MINIMAP_W, self.MINIMAP_H), 1)
                    scale_x = self.MINIMAP_W / self.WORLD_WIDTH
                    scale_y = self.MINIMAP_H / self.WORLD_HEIGHT
                    # enemies
                    for e in self.enemies:
                        ex = map_x + int(e.x * scale_x)
                        ey = map_y + int(e.y * scale_y)
                        pygame.draw.circle(self.display, self.coral if e.alive else (60,60,60), (ex, ey), 2)
                    # player
                    px = map_x + int(self.player.x * scale_x)
                    py = map_y + int(self.player.y * scale_y)
                    pygame.draw.circle(self.display, self.biolum, (px, py), 3)
                    # paused overlay
                    overlay = pygame.Surface((self.window_res[0], self.window_res[1]), pygame.SRCALPHA)
                    overlay.fill((5, 5, 10, 120))
                    self.display.blit(overlay, (0, 0))
                    pause_surf = self.big_font.render('PAUSED', True, self.foam)
                    self.display.blit(pause_surf, (self.window_res[0]//2 - pause_surf.get_width()//2, self.window_res[1]//2 - pause_surf.get_height()//2))
                else:
                    # update/draw enemies and check collisions with player
                    for e in self.enemies:
                        e.speed = self.SETTINGS['enemy_speed']
                        if e.alive:
                            e.update(self.player, self.enemies)
                        else:
                            # death animation update
                            e.death_time += 1
                        e.draw()
                        # enemy-player collision
                        if e.alive:
                            dx = e.x - self.player.x
                            dy = e.y - self.player.y
                            dist_ep = (dx*dx + dy*dy) ** 0.5
                            if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                                # if shield is active, push enemy away and prevent damage
                                rem = max(0.0, self.shield_end_time - time.time()) if 'shield_end_time' in globals() else 0.0
                                if rem > 0:
                                    # push enemy away from player a bit
                                    if dist_ep == 0:
                                        nx, ny = random.uniform(-1,1), random.uniform(-1,1)
                                    else:
                                        nx, ny = dx / dist_ep, dy / dist_ep
                                    e.x += nx * 16
                                    e.y += ny * 16
                                    # small visual feedback
                                    self.make_particles(e.x, e.y, e.color, n=6)
                                else:
                                    # enemy hits player
                                    e.alive = False
                                    e.death_time = 0  # start death animation
                                    self.player.hp -= 1
                                    self.make_particles(e.x, e.y, e.color, n=12)
                                    self.spawn_pickup(e.x, e.y, 'coin')

                    # update bullets and collisions (bullets can destroy enemies)
                    for b in self.bullets[:]:
                        b.update()
                        # remove out-of-world bullets
                        if b.x < 0 or b.x > self.WORLD_WIDTH or b.y < 0 or b.y > self.WORLD_HEIGHT:
                            self.bullets.remove(b)
                            continue
                        # check collision with enemies
                        hit = False
                        for e in self.enemies:
                            if e.alive and e.collide_with_bullet(b):
                                e.alive = False
                                e.death_time = 0  # start death animation
                                # reward player
                                self.score += 5
                                # cooler particle effect with more particles
                                self.make_particles(e.x, e.y, e.color, n=20)
                                # random pickup drop
                                r = random.random()
                                if r < 0.35:
                                    self.spawn_pickup(e.x, e.y, 'coin')
                                elif r < 0.7:
                                    self.spawn_pickup(e.x, e.y, 'ammo')
                                else:
                                    self.spawn_pickup(e.x, e.y, 'health')
                                if b in self.bullets:
                                    self.bullets.remove(b)
                                hit = True
                                break
                        if not hit and b in self.bullets:
                            b.draw()

                    # update pickups
                    for p in self.pickups[:]:
                        p['ttl'] -= 1
                        if p['ttl'] <= 0:
                            try:
                                self.pickups.remove(p)
                            except ValueError:
                                pass
                            continue
                        # magnet effect: pull pickups gently toward player when nearby
                        if not p.get('picked'):
                            dxm = self.player.x - p['x']
                            dym = self.player.y - p['y']
                            mdist = (dxm*dxm + dym*dym) ** 0.5
                            if mdist < self.MAGNET_RADIUS and mdist > 0:
                                p['x'] += (dxm / mdist) * (self.MAGNET_STRENGTH * mdist)
                                p['y'] += (dym / mdist) * (self.MAGNET_STRENGTH * mdist)
                        # draw pickup with shrink-on-pickup behavior
                        kind = p['kind']
                        color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
                        screen_px, screen_py = self.world_to_screen(p['x'], p['y'])
                        # if already picked, shrink until consumed
                        if p.get('picked'):
                            p['size'] = max(0, p.get('size', 6 * self.game_zoom) - p.get('shrink_rate', 0.35))
                            sz = int(max(1, p['size']))
                            pygame.draw.circle(self.display, color, (int(screen_px), int(screen_py)), sz)
                            # small particles while shrinking
                            if random.random() < 0.25:
                                self.make_particles(p['x'] + random.uniform(-4,4), p['y'] + random.uniform(-4,4), color, n=1)
                            if p['size'] <= 0:
                                # apply pickup effect when shrink completes
                                if kind == 'coin':
                                    self.score += 10
                                    self.popups.append({'text': '+10', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.foam})
                                elif kind == 'ammo':
                                    self.AMMO = min(self.MAX_AMMO, self.AMMO + max(3, self.MAX_AMMO // 2))
                                    self.popups.append({'text': '+Ammo', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.green})
                                elif kind == 'health':
                                    self.player.hp = min(self.player.max_hp, self.player.hp + 2)
                                    self.popups.append({'text': '+HP', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.red})
                                try:
                                    self.pickups.remove(p)
                                except ValueError:
                                    pass
                        else:
                            # normal (unpicked) draw
                            sz = int(p.get('size', 6 * self.game_zoom))
                            pygame.draw.circle(self.display, color, (int(screen_px), int(screen_py)), sz)
                            # pickup by player (initiate shrink instead of immediate remove)
                            dx = p['x'] - self.player.x
                            dy = p['y'] - self.player.y
                            if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                                p['picked'] = True

                    # update particles
                    for q in self.particles[:]:
                        q['x'] += q['vx']
                        q['y'] += q['vy']
                        q['vy'] += 0.1
                        q['life'] -= 1
                        if q['life'] <= 0:
                            self.particles.remove(q)
                            continue
                        screen_px, screen_py = self.world_to_screen(q['x'], q['y'])
                        # fade out effect
                        alpha_ratio = q['life'] / q['max_life']
                        fade_size = int(q['size'] * self.game_zoom * alpha_ratio)
                        if fade_size > 0:
                            pygame.draw.circle(self.display, q['color'], (int(screen_px), int(screen_py)), fade_size)
                            # enhanced glow: brighter and larger (reduced intensity so bullets remain prominent)
                            glow_radius = int(fade_size * 3.5)
                            self.draw_glow((screen_px, screen_py), glow_radius, q['color'], 0.12 * alpha_ratio)

                # draw player and HUD
                self.player.draw()
                # draw gun that follows cursor (rotated to point at mouse)
                if 'gun_sprite' in globals() and self.gun_sprite:
                    mx, my = pygame.mouse.get_pos()
                    # convert screen to world for angle calculation
                    world_mx, world_my = self.screen_to_world(mx, my)
                    ang = math.degrees(math.atan2(world_my - self.player.y, world_mx - self.player.x))
                    # rotate gun so that 0deg points to the right
                    w, h = self.gun_sprite.get_size()
                    w_scaled = int(w * self.game_zoom)
                    h_scaled = int(h * self.game_zoom)
                    gun_scaled = pygame.transform.scale(self.gun_sprite, (w_scaled, h_scaled))
                    rot = pygame.transform.rotate(gun_scaled, -ang)
                    player_screen_x, player_screen_y = self.world_to_screen(self.player.x, self.player.y)
                    rrect = rot.get_rect(center=(int(player_screen_x), int(player_screen_y)))
                    self.display.blit(rot, rrect.topleft)
                # show ammo, reload status and score (with progress bar)
                now = time.time()
                if now < self.reload_cooldown:
                    remaining = max(0, self.reload_cooldown - now)
                    progress = 1 - (remaining / self.RELOAD_TIME)
                    bar_w = 120
                    bar_h = 10
                    bx = 5
                    by = 25
                    pygame.draw.rect(self.display, self.ocean_med, (bx, by, bar_w, bar_h))
                    pygame.draw.rect(self.display, self.foam, (bx, by, int(bar_w * progress), bar_h))
                    reload_surf = self.font.render("Reloading...", True, self.coral)
                    self.display.blit(reload_surf, (5, 25 + bar_h + 2))
                else:
                    ammo_surf = self.font.render(f"Ammo: {self.AMMO} (R to reload)", True, self.foam)
                    self.display.blit(ammo_surf, (5, 25))
                score_surf = self.font.render(f"Score: {self.score}", True, self.biolum)
                self.display.blit(score_surf, (5, 45))
                # floating popups
                for popup in self.popups[:]:
                    popup['y'] += popup.get('vy', -0.4)
                    popup['life'] -= 1
                    if popup['life'] <= 0:
                        self.popups.remove(popup)
                        continue
                    sx, sy = self.world_to_screen(popup['x'], popup['y'])
                    txt = self.font.render(popup['text'], True, popup.get('color', self.foam))
                    self.display.blit(txt, (int(sx - txt.get_width() / 2), int(sy)))
                # minimap
                map_x = self.window_res[0] - self.MINIMAP_W - 8
                map_y = 8
                pygame.draw.rect(self.display, self.ocean_med, (map_x, map_y, self.MINIMAP_W, self.MINIMAP_H))
                pygame.draw.rect(self.display, self.foam, (map_x, map_y, self.MINIMAP_W, self.MINIMAP_H), 1)
                scale_x = self.MINIMAP_W / self.WORLD_WIDTH
                scale_y = self.MINIMAP_H / self.WORLD_HEIGHT
                for e in self.enemies:
                    ex = map_x + int(e.x * scale_x)
                    ey = map_y + int(e.y * scale_y)
                    pygame.draw.circle(self.display, self.coral if e.alive else (60,60,60), (ex, ey), 2)
                px = map_x + int(self.player.x * scale_x)
                py = map_y + int(self.player.y * scale_y)
                pygame.draw.circle(self.display, self.biolum, (px, py), 3)

                # check player death
                if self.player.hp <= 0:
                    # reset to menu and heal player
                    self.scene = 'menu'
                    self.player.hp = self.player.max_hp
                # remove dead enemies after death animation completes
                for e in self.enemies[:]:
                    if not e.alive and e.death_time >= e.death_duration:
                        self.enemies.remove(e)

                # wave management: if all enemies are dead, schedule/advance wave
                alive = any(e.alive for e in self.enemies)
                now = time.time()
                if not alive and self.wave_active:
                    # wave cleared
                    self.wave_active = False
                    self.wave_timer = now + self.WAVE_DELAY
                if not self.wave_active and now >= self.wave_timer:
                    # advance to next wave
                    self.wave += 1
                    self.spawn_enemies(self.SETTINGS['enemy_count'] * self.wave)
                    self.wave_active = True

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
            except Exception:
                pass

            # update the full display and cap the frame rate (from settings)
            pygame.display.flip()
            self.clock.tick(self.SETTINGS.get('fps_limit', 60))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # health
        self.max_hp = 5
        self.hp = self.max_hp
    def draw(self):
        screen_x, screen_y = game.world_to_screen(self.x, self.y)
        # draw sprite if available, otherwise a small fallback marker
        if 'player_sprite' in globals() and game.player_sprite:
            w, h = game.player_sprite.get_size()
            w = int(w * game.game_zoom)
            h = int(h * game.game_zoom)
            scaled = pygame.transform.scale(game.player_sprite, (w, h))
            game.display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
        else:
            # small, unobtrusive fallback marker (no large glow)
            pygame.draw.circle(game.display, game.white, (int(screen_x), int(screen_y)), int(6 * game.game_zoom))
        # draw a clearer health bar and ammo counter above the player's head
        bar_w = 64 * game.game_zoom
        bar_h = 8 * game.game_zoom
        hp_ratio = max(0, self.hp) / self.max_hp
        bx = screen_x - bar_w/2
        by = screen_y - 26 * game.game_zoom
        # background
        pygame.draw.rect(game.display, game.ocean_dark, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        # empty bar
        pygame.draw.rect(game.display, (60, 60, 60), (bx, by, bar_w, bar_h))
        # filled hp
        hp_color = (int(255*(1-hp_ratio)), int(255*hp_ratio), 40) if hp_ratio < 0.5 else game.biolum
        pygame.draw.rect(game.display, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h))
        # numeric hp label
        hp_label = game.font.render(f"HP: {self.hp}/{self.max_hp}", True, game.white)
        game.display.blit(hp_label, (int(screen_x - hp_label.get_width()/2), int(by - hp_label.get_height())))
        # ammo counter to the right of the HP bar
        try:
            ammo_text = f"Ammo: {game.AMMO}/{game.MAX_AMMO}"
        except Exception:
            ammo_text = "Ammo: ?"
        ammo_surf = game.font.render(ammo_text, True, game.foam)
        game.display.blit(ammo_surf, (int(bx + bar_w + 6 * game.game_zoom), int(by)))
        # draw shield bubble if active
        try:
            rem = max(0.0, game.shield_end_time - time.time())
        except Exception:
            rem = 0.0
        if rem > 0:
            # radius shrinks as remaining time approaches zero
            max_r = 42 * game.game_zoom
            radius = max(2, int(max_r * (rem / game.SHIELD_DURATION)))
            width = max(1, int(3 * game.game_zoom))
            pygame.draw.circle(game.display, game.ocean_accent, (int(screen_x), int(screen_y)), radius, width)
    # convenience: keep inside bounds
    def clamp(self, w, h):
        self.x = max(0, min(self.x, w))
        self.y = max(0, min(self.y, h))

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.trail_counter = 0
    def draw(self):
        screen_x, screen_y = game.world_to_screen(self.x, self.y)
        # draw a visible solid core for the bullet first (bright), then a smaller accent and subtle glow
        core_r = int(4 * game.game_zoom)
        accent_r = int(2 * game.game_zoom)
        # core (bright) to make bullet easily visible (gold)
        pygame.draw.circle(game.display, (255, 220, 80), (int(screen_x), int(screen_y)), core_r)
        # inner accent for color
        pygame.draw.circle(game.display, game.ocean_accent, (int(screen_x), int(screen_y)), accent_r)
        # small subtle glow (reduced intensity)
        game.draw_glow((screen_x, screen_y), 6 * game.game_zoom, game.ocean_accent, 0.08)
    def update(self):
        spd = game.SETTINGS.get('bullet_speed', 5)
        self.x += self.direction[0] * spd
        self.y += self.direction[1] * spd
        # add trail particles
        self.trail_counter += 1
        if self.trail_counter % 4 == 0:
            # fewer trail particles and in a different color so they don't mask the bullet core
            game.make_particles(self.x, self.y, game.ocean_accent, n=1)

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True
        # ocean themed colors
        self.color = random.choice([game.coral, game.biolum, game.ocean_accent, (150, 200, 255), (100, 180, 200)])
        # optionally assign a sprite
        self.sprite = None
        self.avoid_radius = 60  # separation radius to avoid clustering
        # death animation
        self.death_time = 0  # frames since death started (0 = alive)
        self.death_duration = 12  # frames to animate death
        
    def draw(self):
        screen_x, screen_y = game.world_to_screen(self.x, self.y)
        
        if self.alive:
            if self.sprite:
                w, h = self.sprite.get_size()
                w = int(w * game.game_zoom)
                h = int(h * game.game_zoom)
                scaled = pygame.transform.scale(self.sprite, (w, h))
                game.display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
            else:
                pygame.draw.circle(game.display, self.color, (int(screen_x), int(screen_y)), int(10 * game.game_zoom))
                # glow effect
                game.draw_glow((screen_x, screen_y), 15 * game.game_zoom, self.color, 0.15)
        else:
            # death animation: rely on particles only (no large glow circle)
            # spawn a short burst of particles on death start
            if self.death_time == 0:
                game.make_particles(self.x, self.y, self.color, n=8)
            # optionally draw a subtle fading dot (very small)
            if self.death_time < self.death_duration:
                alpha_progress = 1 - (self.death_time / self.death_duration)
                small_r = max(1, int(6 * game.game_zoom * alpha_progress))
                pygame.draw.circle(game.display, self.color, (int(screen_x), int(screen_y)), small_r)
                
    def update(self, player, all_enemies):
        if not self.alive:
            return
        # AI: move toward player but avoid other enemies
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        
        # separation: move away from nearby enemies
        sep_x, sep_y = 0, 0
        for other in all_enemies:
            if other is not self and other.alive:
                odx = self.x - other.x
                ody = self.y - other.y
                odist = (odx*odx + ody*ody) ** 0.5
                if 0 < odist < self.avoid_radius:
                    # push away from other
                    sep_x += (odx / odist) * 0.5
                    sep_y += (ody / odist) * 0.5
        
        # combine: 70% chase, 30% separation
        if dist != 0:
            chase_x = (dx / dist) * 0.7
            chase_y = (dy / dist) * 0.7
        else:
            chase_x = chase_y = 0
            
        total_x = chase_x + sep_x * 0.3
        total_y = chase_y + sep_y * 0.3
        total_dist = (total_x*total_x + total_y*total_y) ** 0.5
        
        if total_dist > 0:
            self.x += (total_x / total_dist) * self.speed
            self.y += (total_y / total_dist) * self.speed
            
    def collide_with_bullet(self, bullet):
        # collision radius test (only if alive)
        if not self.alive:
            return False
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        return (dx*dx + dy*dy) <= (8 + 3) ** 2

if __name__ == '__main__':
    game = Game()
    game.run()
