import pygame
import sys
import random
import time
import math
import os

pygame.init()

window_res = (800, 480)
window_title = "One In The Chamber"
# window_icon = pygame.image.load('')
display = pygame.display.set_mode(window_res)
pygame.display.set_caption(window_title)
pygame.display.set_icon(pygame.Surface((1, 1)))  # placeholder blank icon

# window state
is_maximized = False
base_window_res = window_res
zoom_level = 1.0

# camera state
camera_x = 0.0
camera_y = 0.0
camera_smooth = 0.1  # lower = smoother
game_zoom = 1.0

# world settings
WORLD_WIDTH = 3200
WORLD_HEIGHT = 1920
TILE_SIZE = 64

# fonts
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 36)

# assets (generate simple pixel sprites at runtime if missing)
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.isdir(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)

def toggle_maximize():
    global display, window_res, is_maximized, base_window_res
    if not is_maximized:
        # maximize window
        info = pygame.display.get_desktop_sizes()[0]
        display = pygame.display.set_mode(info, pygame.FULLSCREEN)
        window_res = info
        is_maximized = True
    else:
        # restore to base size
        display = pygame.display.set_mode(base_window_res)
        window_res = base_window_res
        is_maximized = False

def set_zoom(new_zoom):
    global zoom_level, base_window_res, window_res, display
    zoom_level = max(0.5, min(3.0, new_zoom))
    new_res = (int(base_window_res[0] * zoom_level), int(base_window_res[1] * zoom_level))
    window_res = new_res
    display = pygame.display.set_mode(window_res)
    pygame.display.set_caption(f"{window_title} (Zoom: {zoom_level:.1f}x)")

def update_camera(player_x, player_y):
    global camera_x, camera_y
    # smoothly follow player
    target_x = player_x - (window_res[0] / 2) / game_zoom
    target_y = player_y - (window_res[1] / 2) / game_zoom
    
    camera_x += (target_x - camera_x) * camera_smooth
    camera_y += (target_y - camera_y) * camera_smooth
    
    # clamp to world bounds
    camera_x = max(0, min(camera_x, WORLD_WIDTH - window_res[0] / game_zoom))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - window_res[1] / game_zoom))

def world_to_screen(world_x, world_y):
    screen_x = (world_x - camera_x) * game_zoom
    screen_y = (world_y - camera_y) * game_zoom
    return screen_x, screen_y

def screen_to_world(screen_x, screen_y):
    world_x = screen_x / game_zoom + camera_x
    world_y = screen_y / game_zoom + camera_y
    return world_x, world_y

def draw_tiles():
    # draw tiled background
    tile_color_a = ocean_dark
    tile_color_b = ocean_med
    
    start_tile_x = int(camera_x // TILE_SIZE)
    start_tile_y = int(camera_y // TILE_SIZE)
    end_tile_x = int((camera_x + window_res[0] / game_zoom) // TILE_SIZE) + 1
    end_tile_y = int((camera_y + window_res[1] / game_zoom) // TILE_SIZE) + 1
    
    for tx in range(start_tile_x, min(end_tile_x + 1, WORLD_WIDTH // TILE_SIZE)):
        for ty in range(start_tile_y, min(end_tile_y + 1, WORLD_HEIGHT // TILE_SIZE)):
            color = tile_color_a if (tx + ty) % 2 == 0 else tile_color_b
            
            world_x = tx * TILE_SIZE
            world_y = ty * TILE_SIZE
            screen_x, screen_y = world_to_screen(world_x, world_y)
            
            tile_w = int(TILE_SIZE * game_zoom) + 1
            tile_h = int(TILE_SIZE * game_zoom) + 1
            
            pygame.draw.rect(display, color, (screen_x, screen_y, tile_w, tile_h))
            # grid lines with glow
            pygame.draw.rect(display, (40, 80, 120), (screen_x, screen_y, tile_w, tile_h), 1)

def draw_glow(pos, radius, color, intensity=0.3):
    """Draw a soft glow effect around a point"""
    x, y = int(pos[0]), int(pos[1])
    for i in range(int(radius), 0, -2):
        alpha = int(255 * intensity * (1 - i / radius))
        c = tuple(min(255, int(col + (255 - col) * 0.3)) for col in color)
        pygame.draw.circle(display, c, (x, y), i, 1)

def generate_pixel_sprite(path, size=16, palette=None, symmetric=True):
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

def generate_person_sprite(path, size=24):
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

def generate_crab_sprite(path, size=20):
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

def generate_gun_sprite(path, size=(28,10)):
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

# ensure player and a few enemy sprites exist
player_sprite_path = os.path.join(assets_dir, 'player.png')
gun_sprite_path = os.path.join(assets_dir, 'gun.png')
enemy_sprite_path = os.path.join(assets_dir, 'crab.png')
if not os.path.isfile(player_sprite_path):
    generate_person_sprite(player_sprite_path, size=24)
if not os.path.isfile(gun_sprite_path):
    generate_gun_sprite(gun_sprite_path, size=(30,10))
if not os.path.isfile(enemy_sprite_path):
    generate_crab_sprite(enemy_sprite_path, 20)

# load sprites
try:
    player_sprite = pygame.image.load(player_sprite_path).convert_alpha()
    gun_sprite = pygame.image.load(gun_sprite_path).convert_alpha()
    enemy_sprites = [pygame.image.load(enemy_sprite_path).convert_alpha()]
except Exception:
    player_sprite = None
    gun_sprite = None
    enemy_sprites = []

# basic colours (more vibrant palette)
white = (255, 255, 255)
black = (10, 10, 14)
red = (255, 75, 75)
green = (120, 255, 160)
blue = (100, 160, 255)
accent = (200, 100, 255)

# ocean theme colors
ocean_dark = (8, 25, 45)
ocean_med = (15, 35, 60)
ocean_light = (25, 50, 80)
ocean_accent = (100, 200, 255)
foam = (200, 230, 255)
coral = (255, 120, 150)
biolum = (100, 255, 200)  # bioluminescence
# game update loop
running = True
clock = pygame.time.Clock()
# player movement speed (pixels per frame)
PLAYER_SPEED = 3
# cooldown system
shoot_cooldown = 0.0  # time until next shot allowed
SHOOT_DELAY = 0.25  # cooldown between shots in seconds
# quality-of-life globals
popups = []  # floating text popups (e.g., +10)
paused = False
MAGNET_RADIUS = 140
MAGNET_STRENGTH = 0.12
MINIMAP_W = 160
MINIMAP_H = 100
# shield globals
SHIELD_DURATION = 2.0
shield_end_time = 0.0
shield_active = False
# default settings (editable from settings menu)
SETTINGS = {
    "player_speed": PLAYER_SPEED,
    "enemy_count": 15,
    "enemy_speed": 1.2,
    "fps_limit": 120,
    "max_ammo": 10,
    "bullet_speed": 5,
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # health
        self.max_hp = 5
        self.hp = self.max_hp
    def draw(self):
        screen_x, screen_y = world_to_screen(self.x, self.y)
        # draw sprite if available, otherwise a small fallback marker
        if 'player_sprite' in globals() and player_sprite:
            w, h = player_sprite.get_size()
            w = int(w * game_zoom)
            h = int(h * game_zoom)
            scaled = pygame.transform.scale(player_sprite, (w, h))
            display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
        else:
            # small, unobtrusive fallback marker (no large glow)
            pygame.draw.circle(display, white, (int(screen_x), int(screen_y)), int(6 * game_zoom))
        # draw a clearer health bar and ammo counter above the player's head
        bar_w = 64 * game_zoom
        bar_h = 8 * game_zoom
        hp_ratio = max(0, self.hp) / self.max_hp
        bx = screen_x - bar_w/2
        by = screen_y - 26 * game_zoom
        # background
        pygame.draw.rect(display, ocean_dark, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        # empty bar
        pygame.draw.rect(display, (60, 60, 60), (bx, by, bar_w, bar_h))
        # filled hp
        hp_color = (int(255*(1-hp_ratio)), int(255*hp_ratio), 40) if hp_ratio < 0.5 else biolum
        pygame.draw.rect(display, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h))
        # numeric hp label
        hp_label = font.render(f"HP: {self.hp}/{self.max_hp}", True, white)
        display.blit(hp_label, (int(screen_x - hp_label.get_width()/2), int(by - hp_label.get_height())))
        # ammo counter to the right of the HP bar
        try:
            ammo_text = f"Ammo: {AMMO}/{MAX_AMMO}"
        except Exception:
            ammo_text = "Ammo: ?"
        ammo_surf = font.render(ammo_text, True, foam)
        display.blit(ammo_surf, (int(bx + bar_w + 6 * game_zoom), int(by)))
        # draw shield bubble if active
        try:
            rem = max(0.0, shield_end_time - time.time())
        except Exception:
            rem = 0.0
        if rem > 0:
            # radius shrinks as remaining time approaches zero
            max_r = 42 * game_zoom
            radius = max(2, int(max_r * (rem / SHIELD_DURATION)))
            width = max(1, int(3 * game_zoom))
            pygame.draw.circle(display, ocean_accent, (int(screen_x), int(screen_y)), radius, width)
    # convenience: keep inside bounds
    def clamp(self, w, h):
        self.x = max(0, min(self.x, w))
        self.y = max(0, min(self.y, h))

BULLET_SPEED = 5

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.trail_counter = 0
    def draw(self):
        screen_x, screen_y = world_to_screen(self.x, self.y)
        # draw a visible solid core for the bullet first (bright), then a smaller accent and subtle glow
        core_r = int(4 * game_zoom)
        accent_r = int(2 * game_zoom)
        # core (bright) to make bullet easily visible (gold)
        pygame.draw.circle(display, (255, 220, 80), (int(screen_x), int(screen_y)), core_r)
        # inner accent for color
        pygame.draw.circle(display, ocean_accent, (int(screen_x), int(screen_y)), accent_r)
        # small subtle glow (reduced intensity)
        draw_glow((screen_x, screen_y), 6 * game_zoom, ocean_accent, 0.08)
    def update(self):
        spd = SETTINGS.get('bullet_speed', BULLET_SPEED)
        self.x += self.direction[0] * spd
        self.y += self.direction[1] * spd
        # add trail particles
        self.trail_counter += 1
        if self.trail_counter % 4 == 0:
            # fewer trail particles and in a different color so they don't mask the bullet core
            make_particles(self.x, self.y, ocean_accent, n=1)


class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True
        # ocean themed colors
        self.color = random.choice([coral, biolum, ocean_accent, (150, 200, 255), (100, 180, 200)])
        # optionally assign a sprite
        self.sprite = None
        self.avoid_radius = 60  # separation radius to avoid clustering
        # death animation
        self.death_time = 0  # frames since death started (0 = alive)
        self.death_duration = 12  # frames to animate death
        
    def draw(self):
        screen_x, screen_y = world_to_screen(self.x, self.y)
        
        if self.alive:
            if self.sprite:
                w, h = self.sprite.get_size()
                w = int(w * game_zoom)
                h = int(h * game_zoom)
                scaled = pygame.transform.scale(self.sprite, (w, h))
                display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
            else:
                pygame.draw.circle(display, self.color, (int(screen_x), int(screen_y)), int(10 * game_zoom))
                # glow effect
                draw_glow((screen_x, screen_y), 15 * game_zoom, self.color, 0.15)
        else:
            # death animation: rely on particles only (no large glow circle)
            # spawn a short burst of particles on death start
            if self.death_time == 0:
                make_particles(self.x, self.y, self.color, n=8)
            # optionally draw a subtle fading dot (very small)
            if self.death_time < self.death_duration:
                alpha_progress = 1 - (self.death_time / self.death_duration)
                small_r = max(1, int(6 * game_zoom * alpha_progress))
                pygame.draw.circle(display, self.color, (int(screen_x), int(screen_y)), small_r)
                
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

player = Player(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
AMMO = SETTINGS.get('max_ammo', 10)
MAX_AMMO = SETTINGS.get('max_ammo', 10)
reload_cooldown = 0.0
RELOAD_TIME = 1.5  # increased reload time to prevent spamming
bullets = []
enemies = []
score = 0
particles = []
pickups = []

def spawn_pickup(x, y, kind):
    # kind: 'ammo', 'health', 'coin'
    # include visual state for shrink-on-pickup
    pickups.append({'x': x, 'y': y, 'kind': kind, 'ttl': 600, 'picked': False, 'size': 6 * game_zoom, 'shrink_rate': 0.35})

def make_particles(x, y, color, n=10):
    for i in range(n):
        ang = random.uniform(0, 2*math.pi)
        speed = random.uniform(1.5, 5.5)
        lifetime = random.randint(20, 50)  # longer life for better fade effect
        particles.append({
            'x': x, 'y': y, 
            'vx': math.cos(ang)*speed, 
            'vy': math.sin(ang)*speed, 
            'life': lifetime, 
            'max_life': lifetime,
            'color': color,
            'size': random.uniform(1.5, 4)  # larger particlesw
        })

def spawn_enemies(count, append=False):
    # spawn enemies relative to the player's current position so gameplay is more intense
    # if append==False replace current enemies, otherwise add to them
    if not append:
        enemies.clear()
    px = player.x
    py = player.y
    # spawn radius around player (min, max)
    min_r = 200
    max_r = 480
    for i in range(count):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(min_r, max_r)
        x = px + math.cos(ang) * dist
        y = py + math.sin(ang) * dist
        # clamp to world bounds
        x = max(0, min(WORLD_WIDTH, x))
        y = max(0, min(WORLD_HEIGHT, y))
        e = Enemy(x, y, SETTINGS["enemy_speed"])
        # assign a random enemy sprite if available
        if enemy_sprites:
            e.sprite = random.choice(enemy_sprites)
        enemies.append(e)

# simple scene management: 'menu', 'settings', 'game'
scene = 'menu'

# wave system
wave = 1
wave_active = False
wave_timer = 0.0
WAVE_DELAY = 2.5

# menu state
menu_items = ["Start Game", "Upgrades", "Settings", "Quit"]
menu_index = 0

# settings menu state
settings_items = ["player_speed", "enemy_count", "enemy_speed", "fps_limit"]
settings_index = 0
# upgrades available in shop
upgrades = [
    {"name": "Increase Max Ammo", "key": "max_ammo", "inc": 5, "cost": 10},
    {"name": "Increase Player Speed", "key": "player_speed", "inc": 1, "cost": 15},
    {"name": "Increase Bullet Speed", "key": "bullet_speed", "inc": 1, "cost": 12},
]
upgrades_index = 0
while running:
    # clear screen first, then handle events, draw, and flip
    display.fill(ocean_dark)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # window controls (available in all scenes)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_maximize()
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                set_zoom(zoom_level + 0.1)
            if event.key == pygame.K_MINUS:
                set_zoom(zoom_level - 0.1)
            if event.key == pygame.K_0:
                set_zoom(1.0)
        
        # scroll wheel zooming (game zoom only, in game scene)
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # scroll up = zoom in
                game_zoom = min(3.0, game_zoom + 0.1)
            elif event.y < 0:  # scroll down = zoom out
                game_zoom = max(0.5, game_zoom - 0.1)

        # scene-specific input
        if scene == 'menu':
            # keyboard navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_items)
                if event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_items)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    choice = menu_items[menu_index]
                    if choice == 'Start Game':
                        # apply settings
                        PLAYER_SPEED = SETTINGS['player_speed']
                        wave = 1
                        wave_active = True
                        spawn_enemies(SETTINGS['enemy_count'] * wave)
                        bullets.clear()
                        AMMO = SETTINGS.get('max_ammo', 10)
                        MAX_AMMO = SETTINGS.get('max_ammo', 10)
                        score = 0
                        player.x, player.y = WORLD_WIDTH / 2, WORLD_HEIGHT / 2
                        scene = 'game'
                    elif choice == 'Upgrades':
                        scene = 'upgrades'
                    elif choice == 'Settings':
                        scene = 'settings'
                    elif choice == 'Quit':
                        pygame.quit()
                        sys.exit()
            # mouse click support for menu buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, item in enumerate(menu_items):
                    w, h = font.size(item)
                    bx = window_res[0]//2 - w//2
                    by = 150 + i*30
                    rect = pygame.Rect(bx - 8, by - 4, w + 16, h + 8)
                    if rect.collidepoint(mx, my):
                        choice = item
                        if choice == 'Start Game':
                            PLAYER_SPEED = SETTINGS['player_speed']
                            wave = 1
                            wave_active = True
                            spawn_enemies(SETTINGS['enemy_count'] * wave)
                            bullets.clear()
                            AMMO = SETTINGS.get('max_ammo', 10)
                            MAX_AMMO = SETTINGS.get('max_ammo', 10)
                            score = 0
                            player.x, player.y = WORLD_WIDTH / 2, WORLD_HEIGHT / 2
                            # reset camera
                            camera_x = player.x - (window_res[0] / 2) / game_zoom
                            camera_y = player.y - (window_res[1] / 2) / game_zoom
                            scene = 'game'
                            camera_x = player.x - (window_res[0] / 2) / game_zoom
                            camera_y = player.y - (window_res[1] / 2) / game_zoom
                            scene = 'game'
                        elif choice == 'Upgrades':
                            scene = 'upgrades'
                        elif choice == 'Settings':
                            scene = 'settings'
                        elif choice == 'Quit':
                            pygame.quit()
                            sys.exit()

        elif scene == 'settings':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    key = settings_items[settings_index]
                    if key == 'player_speed':
                        SETTINGS['player_speed'] = max(1, SETTINGS['player_speed'] - 1)
                    elif key == 'enemy_count':
                        SETTINGS['enemy_count'] = max(1, SETTINGS['enemy_count'] - 1)
                    elif key == 'enemy_speed':
                        SETTINGS['enemy_speed'] = max(0.1, round(SETTINGS['enemy_speed'] - 0.1, 2))
                    elif key == 'fps_limit':
                        SETTINGS['fps_limit'] = max(15, SETTINGS['fps_limit'] - 5)
                if event.key == pygame.K_RIGHT:
                    key = settings_items[settings_index]
                    if key == 'player_speed':
                        SETTINGS['player_speed'] = min(20, SETTINGS['player_speed'] + 1)
                    elif key == 'enemy_count':
                        SETTINGS['enemy_count'] = min(50, SETTINGS['enemy_count'] + 1)
                    elif key == 'enemy_speed':
                        SETTINGS['enemy_speed'] = min(10.0, round(SETTINGS['enemy_speed'] + 0.1, 2))
                    elif key == 'fps_limit':
                        SETTINGS['fps_limit'] = min(240, SETTINGS['fps_limit'] + 5)
                if event.key == pygame.K_UP:
                    settings_index = (settings_index - 1) % len(settings_items)
                if event.key == pygame.K_DOWN:
                    settings_index = (settings_index + 1) % len(settings_items)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    scene = 'menu'

        elif scene == 'upgrades':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    upgrades_index = (upgrades_index - 1) % len(upgrades)
                if event.key == pygame.K_DOWN:
                    upgrades_index = (upgrades_index + 1) % len(upgrades)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    up = upgrades[upgrades_index]
                    if score >= up['cost']:
                        score -= up['cost']
                        SETTINGS[up['key']] = SETTINGS.get(up['key'], 0) + up['inc']
                        # apply some immediate effects
                        if up['key'] == 'max_ammo':
                            MAX_AMMO = SETTINGS['max_ammo']
                        if up['key'] == 'player_speed':
                            PLAYER_SPEED = SETTINGS['player_speed']
                if event.key == pygame.K_ESCAPE:
                    scene = 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, up in enumerate(upgrades):
                    w, h = font.size(up['name'])
                    bx = 120
                    by = 120 + i*40
                    rect = pygame.Rect(bx - 8, by - 4, 400, h + 8)
                    if rect.collidepoint(mx, my):
                        if score >= up['cost']:
                            score -= up['cost']
                            SETTINGS[up['key']] = SETTINGS.get(up['key'], 0) + up['inc']
                            if up['key'] == 'max_ammo':
                                MAX_AMMO = SETTINGS['max_ammo']
                            if up['key'] == 'player_speed':
                                PLAYER_SPEED = SETTINGS['player_speed']

        elif scene == 'game':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    now = time.time()
                    # check shooting cooldown and ensure not reloading
                    if not paused and now >= shoot_cooldown and now >= reload_cooldown:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        # convert screen coords to world coords
                        world_mx, world_my = screen_to_world(mouse_x, mouse_y)
                        dir_x = world_mx - player.x
                        dir_y = world_my - player.y
                        length = (dir_x**2 + dir_y**2) ** 0.5
                        if length != 0:
                            dir_x /= length
                            dir_y /= length
                        # decrement ammo properly
                        if AMMO > 0:
                            AMMO -= 1
                            bullets.append(Bullet(player.x, player.y, (dir_x, dir_y)))
                            shoot_cooldown = now + SHOOT_DELAY  # set cooldown
                        else:
                            # out of ammo sound or feedback could go here
                            pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # reload when R pressed (with a tiny cooldown)
                    now = time.time()
                    if now >= reload_cooldown and AMMO < MAX_AMMO:
                        AMMO = MAX_AMMO
                        reload_cooldown = now + RELOAD_TIME
                # pause toggle
                if event.key == pygame.K_p:
                    paused = not paused
                # debug: spawn 20 additional enemies (append)
                if event.key == pygame.K_2:
                    spawn_enemies(20, append=True)
                # shield activation
                if event.key == pygame.K_f:
                    now = time.time()
                    # start shield for SHIELD_DURATION
                    shield_end_time = now + SHIELD_DURATION
                    shield_active = True

    # handle continuous key presses for movement (only in game scene)
    keys = pygame.key.get_pressed()
    if scene == 'game':
        speed = SETTINGS['player_speed']
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += speed
        if keys[pygame.K_ESCAPE]:
            # return to menu
            scene = 'menu'

    # keep player in world bounds
    player.clamp(WORLD_WIDTH, WORLD_HEIGHT)

    # Scene drawing
    if scene == 'menu':
        # draw menu
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(window_title, True, biolum)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 50))
        draw_glow((window_res[0]//2, 50 + title.get_height()//2), 80, biolum, 0.15)
        for i, item in enumerate(menu_items):
            color = biolum if i == menu_index else foam
            it_surf = font.render(item, True, color)
            display.blit(it_surf, (window_res[0]//2 - it_surf.get_width()//2, 150 + i*30))

    elif scene == 'settings':
        title_font = pygame.font.SysFont(None, 42)
        title = title_font.render('Settings', True, biolum)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 40))
        for i, key in enumerate(settings_items):
            val = SETTINGS[key]
            label = f"{key}: {val}"
            color = biolum if i == settings_index else foam
            surf = font.render(label, True, color)
            display.blit(surf, (100, 120 + i*30))

    elif scene == 'upgrades':
        title = big_font.render('Upgrades', True, biolum)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 40))
        for i, up in enumerate(upgrades):
            name = up['name']
            cost = up['cost']
            label = f"{name}  -  Cost: {cost}"
            color = biolum if i == upgrades_index else foam
            surf = font.render(label, True, color)
            display.blit(surf, (120, 120 + i*40))
        # show player score as currency
        cur = font.render(f"Coins: {score}", True, biolum)
        display.blit(cur, (window_res[0]-120, 20))

    elif scene == 'game':
        # update camera to follow player FIRST, before rendering anything
        update_camera(player.x, player.y)
        # update shield state
        try:
            if shield_end_time <= time.time():
                shield_active = False
        except Exception:
            shield_active = False
        
        # draw tiled world background
        draw_tiles()
        
        # paused drawing: when paused, render current scene but skip updates
        if paused:
            for e in enemies:
                e.draw()
            for b in bullets:
                b.draw()
            for p in pickups:
                kind = p['kind']
                color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
                screen_px, screen_py = world_to_screen(p['x'], p['y'])
                sz = int(p.get('size', 6 * game_zoom))
                pygame.draw.circle(display, color, (int(screen_px), int(screen_py)), sz)
            for q in particles:
                screen_px, screen_py = world_to_screen(q['x'], q['y'])
                alpha_ratio = q['life'] / q['max_life'] if q.get('max_life') else 1
                fade_size = int(q.get('size', 2) * game_zoom * alpha_ratio)
                if fade_size > 0:
                    pygame.draw.circle(display, q['color'], (int(screen_px), int(screen_py)), fade_size)
            # draw player, gun and HUD (static)
            player.draw()
            if 'gun_sprite' in globals() and gun_sprite:
                mx, my = pygame.mouse.get_pos()
                world_mx, world_my = screen_to_world(mx, my)
                ang = math.degrees(math.atan2(world_my - player.y, world_mx - player.x))
                w, h = gun_sprite.get_size()
                w_scaled = int(w * game_zoom)
                h_scaled = int(h * game_zoom)
                gun_scaled = pygame.transform.scale(gun_sprite, (w_scaled, h_scaled))
                rot = pygame.transform.rotate(gun_scaled, -ang)
                player_screen_x, player_screen_y = world_to_screen(player.x, player.y)
                rrect = rot.get_rect(center=(int(player_screen_x), int(player_screen_y)))
                display.blit(rot, rrect.topleft)
            # HUD (ammo / reload progress)
            now = time.time()
            if now < reload_cooldown:
                remaining = max(0, reload_cooldown - now)
                progress = 1 - (remaining / RELOAD_TIME)
                bar_w = 120
                bar_h = 10
                bx = 5
                by = 25
                pygame.draw.rect(display, ocean_med, (bx, by, bar_w, bar_h))
                pygame.draw.rect(display, foam, (bx, by, int(bar_w * progress), bar_h))
                reload_surf = font.render("Reloading...", True, coral)
                display.blit(reload_surf, (5, 25 + bar_h + 2))
            else:
                ammo_surf = font.render(f"Ammo: {AMMO} (R to reload)", True, foam)
                display.blit(ammo_surf, (5, 25))
            # draw popups
            for popup in popups[:]:
                popup['y'] += popup.get('vy', -0.4)
                popup['life'] -= 1
                if popup['life'] <= 0:
                    popups.remove(popup)
                    continue
                sx, sy = world_to_screen(popup['x'], popup['y'])
                alpha = max(0, int(255 * (popup['life'] / 60)))
                txt = font.render(popup['text'], True, popup.get('color', foam))
                display.blit(txt, (int(sx - txt.get_width() / 2), int(sy)))
            # minimap (static)
            map_x = window_res[0] - MINIMAP_W - 8
            map_y = 8
            pygame.draw.rect(display, ocean_med, (map_x, map_y, MINIMAP_W, MINIMAP_H))
            pygame.draw.rect(display, foam, (map_x, map_y, MINIMAP_W, MINIMAP_H), 1)
            scale_x = MINIMAP_W / WORLD_WIDTH
            scale_y = MINIMAP_H / WORLD_HEIGHT
            # enemies
            for e in enemies:
                ex = map_x + int(e.x * scale_x)
                ey = map_y + int(e.y * scale_y)
                pygame.draw.circle(display, coral if e.alive else (60,60,60), (ex, ey), 2)
            # player
            px = map_x + int(player.x * scale_x)
            py = map_y + int(player.y * scale_y)
            pygame.draw.circle(display, biolum, (px, py), 3)
            # paused overlay
            overlay = pygame.Surface((window_res[0], window_res[1]), pygame.SRCALPHA)
            overlay.fill((5, 5, 10, 120))
            display.blit(overlay, (0, 0))
            pause_surf = big_font.render('PAUSED', True, foam)
            display.blit(pause_surf, (window_res[0]//2 - pause_surf.get_width()//2, window_res[1]//2 - pause_surf.get_height()//2))
        else:
            # update/draw enemies and check collisions with player
            for e in enemies:
                e.speed = SETTINGS['enemy_speed']
                if e.alive:
                    e.update(player, enemies)
                else:
                    # death animation update
                    e.death_time += 1
                e.draw()
                # enemy-player collision
                if e.alive:
                    dx = e.x - player.x
                    dy = e.y - player.y
                    dist_ep = (dx*dx + dy*dy) ** 0.5
                    if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                        # if shield is active, push enemy away and prevent damage
                        rem = max(0.0, shield_end_time - time.time()) if 'shield_end_time' in globals() else 0.0
                        if rem > 0:
                            # push enemy away from player a bit
                            if dist_ep == 0:
                                nx, ny = random.uniform(-1,1), random.uniform(-1,1)
                            else:
                                nx, ny = dx / dist_ep, dy / dist_ep
                            e.x += nx * 16
                            e.y += ny * 16
                            # small visual feedback
                            make_particles(e.x, e.y, e.color, n=6)
                        else:
                            # enemy hits player
                            e.alive = False
                            e.death_time = 0  # start death animation
                            player.hp -= 1
                            make_particles(e.x, e.y, e.color, n=12)
                            spawn_pickup(e.x, e.y, 'coin')

            # update bullets and collisions (bullets can destroy enemies)
            for b in bullets[:]:
                b.update()
                # remove out-of-world bullets
                if b.x < 0 or b.x > WORLD_WIDTH or b.y < 0 or b.y > WORLD_HEIGHT:
                    bullets.remove(b)
                    continue
                # check collision with enemies
                hit = False
                for e in enemies:
                    if e.alive and e.collide_with_bullet(b):
                        e.alive = False
                        e.death_time = 0  # start death animation
                        # reward player
                        score += 5
                        # cooler particle effect with more particles
                        make_particles(e.x, e.y, e.color, n=20)
                        # random pickup drop
                        r = random.random()
                        if r < 0.35:
                            spawn_pickup(e.x, e.y, 'coin')
                        elif r < 0.7:
                            spawn_pickup(e.x, e.y, 'ammo')
                        else:
                            spawn_pickup(e.x, e.y, 'health')
                        if b in bullets:
                            bullets.remove(b)
                        hit = True
                        break
                if not hit and b in bullets:
                    b.draw()

            # update pickups
            for p in pickups[:]:
                p['ttl'] -= 1
                if p['ttl'] <= 0:
                    try:
                        pickups.remove(p)
                    except ValueError:
                        pass
                    continue
                # magnet effect: pull pickups gently toward player when nearby
                if not p.get('picked'):
                    dxm = player.x - p['x']
                    dym = player.y - p['y']
                    mdist = (dxm*dxm + dym*dym) ** 0.5
                    if mdist < MAGNET_RADIUS and mdist > 0:
                        p['x'] += (dxm / mdist) * (MAGNET_STRENGTH * mdist)
                        p['y'] += (dym / mdist) * (MAGNET_STRENGTH * mdist)
                # draw pickup with shrink-on-pickup behavior
                kind = p['kind']
                color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
                screen_px, screen_py = world_to_screen(p['x'], p['y'])
                # if already picked, shrink until consumed
                if p.get('picked'):
                    p['size'] = max(0, p.get('size', 6 * game_zoom) - p.get('shrink_rate', 0.35))
                    sz = int(max(1, p['size']))
                    pygame.draw.circle(display, color, (int(screen_px), int(screen_py)), sz)
                    # small particles while shrinking
                    if random.random() < 0.25:
                        make_particles(p['x'] + random.uniform(-4,4), p['y'] + random.uniform(-4,4), color, n=1)
                    if p['size'] <= 0:
                        # apply pickup effect when shrink completes
                        if kind == 'coin':
                            score += 10
                            popups.append({'text': '+10', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': foam})
                        elif kind == 'ammo':
                            AMMO = min(MAX_AMMO, AMMO + max(3, MAX_AMMO // 2))
                            popups.append({'text': '+Ammo', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': green})
                        elif kind == 'health':
                            player.hp = min(player.max_hp, player.hp + 2)
                            popups.append({'text': '+HP', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': red})
                        try:
                            pickups.remove(p)
                        except ValueError:
                            pass
                else:
                    # normal (unpicked) draw
                    sz = int(p.get('size', 6 * game_zoom))
                    pygame.draw.circle(display, color, (int(screen_px), int(screen_py)), sz)
                    # pickup by player (initiate shrink instead of immediate remove)
                    dx = p['x'] - player.x
                    dy = p['y'] - player.y
                    if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                        p['picked'] = True

            # update particles
            for q in particles[:]:
                q['x'] += q['vx']
                q['y'] += q['vy']
                q['vy'] += 0.1
                q['life'] -= 1
                if q['life'] <= 0:
                    particles.remove(q)
                    continue
                screen_px, screen_py = world_to_screen(q['x'], q['y'])
                # fade out effect
                alpha_ratio = q['life'] / q['max_life']
                fade_size = int(q['size'] * game_zoom * alpha_ratio)
                if fade_size > 0:
                    pygame.draw.circle(display, q['color'], (int(screen_px), int(screen_py)), fade_size)
                    # enhanced glow: brighter and larger (reduced intensity so bullets remain prominent)
                    glow_radius = int(fade_size * 3.5)
                    draw_glow((screen_px, screen_py), glow_radius, q['color'], 0.12 * alpha_ratio)

        # draw player and HUD
        player.draw()
        # draw gun that follows cursor (rotated to point at mouse)
        if 'gun_sprite' in globals() and gun_sprite:
            mx, my = pygame.mouse.get_pos()
            # convert screen to world for angle calculation
            world_mx, world_my = screen_to_world(mx, my)
            ang = math.degrees(math.atan2(world_my - player.y, world_mx - player.x))
            # rotate gun so that 0deg points to the right
            w, h = gun_sprite.get_size()
            w_scaled = int(w * game_zoom)
            h_scaled = int(h * game_zoom)
            gun_scaled = pygame.transform.scale(gun_sprite, (w_scaled, h_scaled))
            rot = pygame.transform.rotate(gun_scaled, -ang)
            player_screen_x, player_screen_y = world_to_screen(player.x, player.y)
            rrect = rot.get_rect(center=(int(player_screen_x), int(player_screen_y)))
            display.blit(rot, rrect.topleft)
        # show ammo, reload status and score (with progress bar)
        now = time.time()
        if now < reload_cooldown:
            remaining = max(0, reload_cooldown - now)
            progress = 1 - (remaining / RELOAD_TIME)
            bar_w = 120
            bar_h = 10
            bx = 5
            by = 25
            pygame.draw.rect(display, ocean_med, (bx, by, bar_w, bar_h))
            pygame.draw.rect(display, foam, (bx, by, int(bar_w * progress), bar_h))
            reload_surf = font.render("Reloading...", True, coral)
            display.blit(reload_surf, (5, 25 + bar_h + 2))
        else:
            ammo_surf = font.render(f"Ammo: {AMMO} (R to reload)", True, foam)
            display.blit(ammo_surf, (5, 25))
        score_surf = font.render(f"Score: {score}", True, biolum)
        display.blit(score_surf, (5, 45))
        # floating popups
        for popup in popups[:]:
            popup['y'] += popup.get('vy', -0.4)
            popup['life'] -= 1
            if popup['life'] <= 0:
                popups.remove(popup)
                continue
            sx, sy = world_to_screen(popup['x'], popup['y'])
            txt = font.render(popup['text'], True, popup.get('color', foam))
            display.blit(txt, (int(sx - txt.get_width() / 2), int(sy)))
        # minimap
        map_x = window_res[0] - MINIMAP_W - 8
        map_y = 8
        pygame.draw.rect(display, ocean_med, (map_x, map_y, MINIMAP_W, MINIMAP_H))
        pygame.draw.rect(display, foam, (map_x, map_y, MINIMAP_W, MINIMAP_H), 1)
        scale_x = MINIMAP_W / WORLD_WIDTH
        scale_y = MINIMAP_H / WORLD_HEIGHT
        for e in enemies:
            ex = map_x + int(e.x * scale_x)
            ey = map_y + int(e.y * scale_y)
            pygame.draw.circle(display, coral if e.alive else (60,60,60), (ex, ey), 2)
        px = map_x + int(player.x * scale_x)
        py = map_y + int(player.y * scale_y)
        pygame.draw.circle(display, biolum, (px, py), 3)

        # check player death
        if player.hp <= 0:
            # reset to menu and heal player
            scene = 'menu'
            player.hp = player.max_hp
        # remove dead enemies after death animation completes
        for e in enemies[:]:
            if not e.alive and e.death_time >= e.death_duration:
                enemies.remove(e)
        
        # wave management: if all enemies are dead, schedule/advance wave
        alive = any(e.alive for e in enemies)
        now = time.time()
        if not alive and wave_active:
            # wave cleared
            wave_active = False
            wave_timer = now + WAVE_DELAY
        if not wave_active and now >= wave_timer:
            # advance to next wave
            wave += 1
            spawn_enemies(SETTINGS['enemy_count'] * wave)
            wave_active = True

    # common: FPS display and wave info
    fps_surf = font.render(f"FPS: {int(clock.get_fps())}", True, ocean_accent)
    display.blit(fps_surf, (5, 5))
    if scene == 'game':
        wave_surf = font.render(f"Wave: {wave}", True, biolum)
        display.blit(wave_surf, (window_res[0]-120, 5))

    # debug overlay: scene and player coords (helpful when player seems invisible)
    try:
        debug_surf = font.render(f"Scene: {scene}  Player: {int(player.x)},{int(player.y)}  HP:{player.hp}", True, (200,200,200))
        display.blit(debug_surf, (10, window_res[1]-24))
    except Exception:
        pass

    # update the full display and cap the frame rate (from settings)
    pygame.display.flip()
    clock.tick(SETTINGS.get('fps_limit', 60))


