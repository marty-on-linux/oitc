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

# fonts
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 36)

# assets (generate simple pixel sprites at runtime if missing)
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.isdir(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)

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
enemy_sprite_paths = [os.path.join(assets_dir, f'crab_{i}.png') for i in range(3)]
if not os.path.isfile(player_sprite_path):
    generate_person_sprite(player_sprite_path, size=24)
if not os.path.isfile(gun_sprite_path):
    generate_gun_sprite(gun_sprite_path, size=(30,10))
for p in enemy_sprite_paths:
    if not os.path.isfile(p):
        generate_crab_sprite(p, size=20)

# load sprites
try:
    player_sprite = pygame.image.load(player_sprite_path).convert_alpha()
    gun_sprite = pygame.image.load(gun_sprite_path).convert_alpha()
    enemy_sprites = [pygame.image.load(p).convert_alpha() for p in enemy_sprite_paths]
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
# game update loop
running = True
clock = pygame.time.Clock()
# player movement speed (pixels per frame)
PLAYER_SPEED = 3
# default settings (editable from settings menu)
SETTINGS = {
    "player_speed": PLAYER_SPEED,
    "enemy_count": 5,
    "enemy_speed": 1.2,
    "fps_limit": 60,
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
        # draw sprite if available, otherwise fallback to circle
        if 'player_sprite' in globals() and player_sprite:
            w, h = player_sprite.get_size()
            display.blit(player_sprite, (int(self.x - w/2), int(self.y - h/2)))
        else:
            pygame.draw.circle(display, white, (int(self.x), int(self.y)), 6)
        # draw a small health bar above the player
        bar_w = 36
        bar_h = 6
        hp_ratio = max(0, self.hp) / self.max_hp
        bx = int(self.x - bar_w/2)
        by = int(self.y - 18)
        pygame.draw.rect(display, (40, 40, 40), (bx, by, bar_w, bar_h))
        hp_color = (int(255*(1-hp_ratio)), int(255*hp_ratio), 40)
        pygame.draw.rect(display, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h))
    # convenience: keep inside bounds
    def clamp(self, w, h):
        self.x = max(0, min(self.x, w - 1))
        self.y = max(0, min(self.y, h - 1))

BULLET_SPEED = 5

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
    def draw(self):
        pygame.draw.circle(display, red, (int(self.x), int(self.y)), 3)
    def update(self):
        spd = SETTINGS.get('bullet_speed', BULLET_SPEED)
        self.x += self.direction[0] * spd
        self.y += self.direction[1] * spd


class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True
        # vibrant random color
        self.color = random.choice([(255,100,200),(120,255,160),(100,160,255),(255,200,80),(180,100,255)])
        # optionally assign a sprite
        self.sprite = None
    def draw(self):
        if self.alive:
            if self.sprite:
                w, h = self.sprite.get_size()
                display.blit(self.sprite, (int(self.x - w/2), int(self.y - h/2)))
            else:
                pygame.draw.circle(display, self.color, (int(self.x), int(self.y)), 10)
    def update(self, player):
        if not self.alive:
            return
        # simple chasing AI: move toward the player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        if dist != 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    def collide_with_bullet(self, bullet):
        # collision radius test
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        return (dx*dx + dy*dy) <= (8 + 3) ** 2

player = Player(400, 240)
AMMO = SETTINGS.get('max_ammo', 10)
MAX_AMMO = SETTINGS.get('max_ammo', 10)
reload_cooldown = 0.0
RELOAD_TIME = 0.5
bullets = []
enemies = []
score = 0
particles = []
pickups = []

def spawn_pickup(x, y, kind):
    # kind: 'ammo', 'health', 'coin'
    pickups.append({'x': x, 'y': y, 'kind': kind, 'ttl': 600})

def make_particles(x, y, color, n=10):
    for i in range(n):
        ang = random.uniform(0, 2*math.pi)
        speed = random.uniform(1.0, 4.0)
        particles.append({'x': x, 'y': y, 'vx': math.cos(ang)*speed, 'vy': math.sin(ang)*speed, 'life': random.randint(10, 30), 'color': color})

def spawn_enemies(count):
    enemies.clear()
    for i in range(count):
        # spawn around edges
        side = i % 4
        if side == 0:
            x = 0
            y = random.uniform(0, window_res[1])
        elif side == 1:
            x = window_res[0]
            y = random.uniform(0, window_res[1])
        elif side == 2:
            x = random.uniform(0, window_res[0])
            y = 0
        else:
            x = random.uniform(0, window_res[0])
            y = window_res[1]
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
    display.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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
                        player.x, player.y = window_res[0] / 2, window_res[1] / 2
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
                            player.x, player.y = window_res[0] / 2, window_res[1] / 2
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
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dir_x = mouse_x - player.x
                    dir_y = mouse_y - player.y
                    length = (dir_x**2 + dir_y**2) ** 0.5
                    if length != 0:
                        dir_x /= length
                        dir_y /= length
                    # decrement ammo properly
                    if AMMO > 0:
                        AMMO -= 1
                        bullets.append(Bullet(player.x, player.y, (dir_x, dir_y)))
                    else:
                        # out of ammo sound or feedback could go here
                        pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # reload when R pressed (with a tiny cooldown)
                    now = time.time()
                    if now >= reload_cooldown:
                        AMMO = MAX_AMMO
                        reload_cooldown = now + RELOAD_TIME

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

    # keep player on-screen
    player.clamp(window_res[0], window_res[1])

    # Scene drawing
    if scene == 'menu':
        # draw menu
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(window_title, True, white)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 50))
        for i, item in enumerate(menu_items):
            color = green if i == menu_index else white
            it_surf = font.render(item, True, color)
            display.blit(it_surf, (window_res[0]//2 - it_surf.get_width()//2, 150 + i*30))

    elif scene == 'settings':
        title_font = pygame.font.SysFont(None, 42)
        title = title_font.render('Settings', True, white)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 40))
        for i, key in enumerate(settings_items):
            val = SETTINGS[key]
            label = f"{key}: {val}"
            color = green if i == settings_index else white
            surf = font.render(label, True, color)
            display.blit(surf, (100, 120 + i*30))

    elif scene == 'upgrades':
        title = big_font.render('Upgrades', True, accent)
        display.blit(title, (window_res[0]//2 - title.get_width()//2, 40))
        for i, up in enumerate(upgrades):
            name = up['name']
            cost = up['cost']
            label = f"{name}  -  Cost: {cost}"
            color = green if i == upgrades_index else white
            surf = font.render(label, True, color)
            display.blit(surf, (120, 120 + i*40))
        # show player score as currency
        cur = font.render(f"Coins: {score}", True, white)
        display.blit(cur, (window_res[0]-120, 20))

    elif scene == 'game':
        # update/draw enemies and check collisions with player
        for e in enemies:
            e.speed = SETTINGS['enemy_speed']
            e.update(player)
            e.draw()
            # enemy-player collision
            if e.alive:
                dx = e.x - player.x
                dy = e.y - player.y
                if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                    # enemy hits player
                    e.alive = False
                    player.hp -= 1
                    make_particles(e.x, e.y, e.color, n=12)
                    spawn_pickup(e.x, e.y, 'coin')

        # update bullets and collisions (bullets can destroy enemies)
        for b in bullets[:]:
            b.update()
            # remove off-screen bullets
            if b.x < 0 or b.x > window_res[0] or b.y < 0 or b.y > window_res[1]:
                bullets.remove(b)
                continue
            # check collision with enemies
            hit = False
            for e in enemies:
                if e.alive and e.collide_with_bullet(b):
                    e.alive = False
                    # reward player
                    score += 5
                    # particle effect
                    make_particles(e.x, e.y, e.color, n=14)
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
                pickups.remove(p)
                continue
            # draw pickup
            kind = p['kind']
            color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
            pygame.draw.circle(display, color, (int(p['x']), int(p['y'])), 6)
            # pickup by player
            dx = p['x'] - player.x
            dy = p['y'] - player.y
            if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                if kind == 'coin':
                    score += 3
                elif kind == 'ammo':
                    AMMO = min(MAX_AMMO, AMMO + max(1, MAX_AMMO // 2))
                elif kind == 'health':
                    player.hp = min(player.max_hp, player.hp + 1)
                pickups.remove(p)

        # update particles
        for q in particles[:]:
            q['x'] += q['vx']
            q['y'] += q['vy']
            q['vy'] += 0.1
            q['life'] -= 1
            if q['life'] <= 0:
                particles.remove(q)
                continue
            pygame.draw.circle(display, q['color'], (int(q['x']), int(q['y'])), 2)

        # draw player and HUD
            player.draw()
            # draw gun that follows cursor (rotated to point at mouse)
            if 'gun_sprite' in globals() and gun_sprite:
                mx, my = pygame.mouse.get_pos()
                ang = math.degrees(math.atan2(my - player.y, mx - player.x))
                # rotate gun so that 0deg points to the right
                rot = pygame.transform.rotate(gun_sprite, -ang)
                rrect = rot.get_rect(center=(int(player.x), int(player.y)))
                display.blit(rot, rrect.topleft)
        # show ammo, reload status and score
        now = time.time()
        if now < reload_cooldown:
            reload_surf = font.render("Reloading...", True, accent)
            display.blit(reload_surf, (5, 25))
        else:
            ammo_surf = font.render(f"Ammo: {AMMO} (R to reload)", True, white)
            display.blit(ammo_surf, (5, 25))
        score_surf = font.render(f"Score: {score}", True, white)
        display.blit(score_surf, (5, 45))

        # check player death
        if player.hp <= 0:
            # reset to menu and heal player
            scene = 'menu'
            player.hp = player.max_hp
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
    fps_surf = font.render(f"FPS: {int(clock.get_fps())}", True, white)
    display.blit(fps_surf, (5, 5))
    if scene == 'game':
        wave_surf = font.render(f"Wave: {wave}", True, accent)
        display.blit(wave_surf, (window_res[0]-120, 5))

    # update the full display and cap the frame rate (from settings)
    pygame.display.flip()
    clock.tick(SETTINGS.get('fps_limit', 60))


