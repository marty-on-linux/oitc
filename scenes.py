import pygame
import sys
import time
import math
import random
class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def draw(self, display):
        raise NotImplementedError

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.menu_items = ["Start Game", "Upgrades", "Settings", "Quit"]
        self.menu_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                if event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.handle_menu_selection()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, item in enumerate(self.menu_items):
                    w, h = self.game.font.size(item)
                    bx = self.game.window_res[0]//2 - w//2
                    by = 150 + i*30
                    rect = pygame.Rect(bx - 8, by - 4, w + 16, h + 8)
                    if rect.collidepoint(mx, my):
                        self.menu_index = i
                        self.handle_menu_selection()

    def handle_menu_selection(self):
        choice = self.menu_items[self.menu_index]
        if choice == 'Start Game':
            self.game.start_game()
        elif choice == 'Upgrades':
            self.game.scene = 'upgrades'
        elif choice == 'Settings':
            self.game.scene = 'settings'
        elif choice == 'Quit':
            pygame.quit()
            sys.exit()

    def update(self):
        pass

    def draw(self, display):
        display.fill(self.game.ocean_dark)
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.game.window_title, True, self.game.biolum)
        display.blit(title, (self.game.window_res[0]//2 - title.get_width()//2, 50))
        self.game.draw_glow((self.game.window_res[0]//2, 50 + title.get_height()//2), 80, self.game.biolum, 0.15)
        for i, item in enumerate(self.menu_items):
            color = self.game.biolum if i == self.menu_index else self.game.foam
            it_surf = self.game.font.render(item, True, color)
            display.blit(it_surf, (self.game.window_res[0]//2 - it_surf.get_width()//2, 150 + i*30))

class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.settings_items = ["player_speed", "enemy_count", "enemy_speed", "fps_limit"]
        self.settings_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    key = self.settings_items[self.settings_index]
                    if key == 'player_speed':
                        self.game.SETTINGS['player_speed'] = max(1, self.game.SETTINGS['player_speed'] - 1)
                    elif key == 'enemy_count':
                        self.game.SETTINGS['enemy_count'] = max(1, self.game.SETTINGS['enemy_count'] - 1)
                    elif key == 'enemy_speed':
                        self.game.SETTINGS['enemy_speed'] = max(0.1, round(self.game.SETTINGS['enemy_speed'] - 0.1, 2))
                    elif key == 'fps_limit':
                        self.game.SETTINGS['fps_limit'] = max(15, self.game.SETTINGS['fps_limit'] - 5)
                if event.key == pygame.K_RIGHT:
                    key = self.settings_items[self.settings_index]
                    if key == 'player_speed':
                        self.game.SETTINGS['player_speed'] = min(20, self.game.SETTINGS['player_speed'] + 1)
                    elif key == 'enemy_count':
                        self.game.SETTINGS['enemy_count'] = min(50, self.game.SETTINGS['enemy_count'] + 1)
                    elif key == 'enemy_speed':
                        self.game.SETTINGS['enemy_speed'] = min(10.0, round(self.game.SETTINGS['enemy_speed'] + 0.1, 2))
                    elif key == 'fps_limit':
                        self.game.SETTINGS['fps_limit'] = min(240, self.game.SETTINGS['fps_limit'] + 5)
                if event.key == pygame.K_UP:
                    self.settings_index = (self.settings_index - 1) % len(self.settings_items)
                if event.key == pygame.K_DOWN:
                    self.settings_index = (self.settings_index + 1) % len(self.settings_items)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.game.scene = 'menu'

    def update(self):
        pass

    def draw(self, display):
        display.fill(self.game.ocean_dark)
        title_font = pygame.font.SysFont(None, 42)
        title = title_font.render('Settings', True, self.game.biolum)
        display.blit(title, (self.game.window_res[0]//2 - title.get_width()//2, 40))
        for i, key in enumerate(self.settings_items):
            val = self.game.SETTINGS[key]
            label = f"{key}: {val}"
            color = self.game.biolum if i == self.settings_index else self.game.foam
            surf = self.game.font.render(label, True, color)
            display.blit(surf, (100, 120 + i*30))

class UpgradesScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.upgrades_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.upgrades_index = (self.upgrades_index - 1) % len(self.game.upgrades)
                if event.key == pygame.K_DOWN:
                    self.upgrades_index = (self.upgrades_index + 1) % len(self.game.upgrades)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.purchase_upgrade()
                if event.key == pygame.K_ESCAPE:
                    self.game.scene = 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, up in enumerate(self.game.upgrades):
                    w, h = self.game.font.size(up['name'])
                    bx = 120
                    by = 120 + i*40
                    rect = pygame.Rect(bx - 8, by - 4, 400, h + 8)
                    if rect.collidepoint(mx, my):
                        self.upgrades_index = i
                        self.purchase_upgrade()

    def purchase_upgrade(self):
        up = self.game.upgrades[self.upgrades_index]
        if self.game.score >= up['cost']:
            self.game.score -= up['cost']
            self.game.SETTINGS[up['key']] = self.game.SETTINGS.get(up['key'], 0) + up['inc']
            if up['key'] == 'max_ammo':
                self.game.MAX_AMMO = self.game.SETTINGS['max_ammo']
            if up['key'] == 'player_speed':
                self.game.PLAYER_SPEED = self.game.SETTINGS['player_speed']

    def update(self):
        pass

    def draw(self, display):
        display.fill(self.game.ocean_dark)
        title = self.game.big_font.render('Upgrades', True, self.game.biolum)
        display.blit(title, (self.game.window_res[0]//2 - title.get_width()//2, 40))
        for i, up in enumerate(self.game.upgrades):
            name = up['name']
            cost = up['cost']
            label = f"{name}  -  Cost: {cost}"
            color = self.game.biolum if i == self.upgrades_index else self.game.foam
            surf = self.game.font.render(label, True, color)
            display.blit(surf, (120, 120 + i*40))
        # show player score as currency
        cur = self.game.font.render(f"Coins: {self.game.score}", True, self.game.biolum)
        display.blit(cur, (self.game.window_res[0]-120, 20))

class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    now = time.time()
                    # check shooting cooldown and ensure not reloading
                    if not self.game.paused and now >= self.game.shoot_cooldown and now >= self.game.reload_cooldown:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        # convert screen coords to world coords
                        world_mx, world_my = self.game.screen_to_world(mouse_x, mouse_y)
                        dir_x = world_mx - self.game.player.x
                        dir_y = world_my - self.game.player.y
                        length = (dir_x**2 + dir_y**2) ** 0.5
                        if length != 0:
                            dir_x /= length
                            dir_y /= length
                        # decrement ammo properly
                        if self.game.AMMO > 0:
                            self.game.AMMO -= 1
                            self.game.bullets.append(self.game.Bullet(self.game.player.x, self.game.player.y, (dir_x, dir_y)))
                            self.game.shoot_cooldown = now + self.game.SHOOT_DELAY  # set cooldown
                        else:
                            # out of ammo sound or feedback could go here
                            pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # reload when R pressed (with a tiny cooldown)
                    now = time.time()
                    if now >= self.game.reload_cooldown and self.game.AMMO < self.game.MAX_AMMO:
                        self.game.AMMO = self.game.MAX_AMMO
                        self.game.reload_cooldown = now + self.game.RELOAD_TIME
                # pause toggle
                if event.key == pygame.K_p:
                    self.game.paused = not self.game.paused
                # debug: spawn 20 additional enemies (append)
                if event.key == pygame.K_2:
                    self.game.spawn_enemies(20, append=True)
                # shield activation
                if event.key == pygame.K_f:
                    now = time.time()
                    # start shield for SHIELD_DURATION
                    self.game.shield_end_time = now + self.game.SHIELD_DURATION
                    self.game.shield_active = True
                if event.key == pygame.K_ESCAPE:
                    self.game.scene = 'menu'

    def update(self):
        if self.game.paused:
            return

        # handle continuous key presses for movement (only in game scene)
        keys = pygame.key.get_pressed()
        speed = self.game.SETTINGS['player_speed']
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.game.player.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.game.player.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.game.player.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.game.player.y += speed

        # keep player in world bounds
        self.game.player.clamp(self.game.WORLD_WIDTH, self.game.WORLD_HEIGHT)

        # update camera to follow player FIRST, before rendering anything
        self.game.update_camera(self.game.player.x, self.game.player.y)
        # update shield state
        try:
            if self.game.shield_end_time <= time.time():
                self.game.shield_active = False
        except Exception:
            self.game.shield_active = False

        # update/draw enemies and check collisions with player
        for e in self.game.enemies:
            e.speed = self.game.SETTINGS['enemy_speed']
            if e.alive:
                e.update(self.game.player, self.game.enemies)
            else:
                # death animation update
                e.death_time += 1
            # enemy-player collision
            if e.alive:
                dx = e.x - self.game.player.x
                dy = e.y - self.game.player.y
                dist_ep = (dx*dx + dy*dy) ** 0.5
                if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                    # if shield is active, push enemy away and prevent damage
                    rem = max(0.0, self.game.shield_end_time - time.time()) if 'shield_end_time' in globals() else 0.0
                    if rem > 0:
                        # push enemy away from player a bit
                        if dist_ep == 0:
                            nx, ny = random.uniform(-1,1), random.uniform(-1,1)
                        else:
                            nx, ny = dx / dist_ep, dy / dist_ep
                        e.x += nx * 16
                        e.y += ny * 16
                        # small visual feedback
                        self.game.make_particles(e.x, e.y, e.color, n=6)
                    else:
                        # enemy hits player
                        e.alive = False
                        e.death_time = 0  # start death animation
                        self.game.player.hp -= 1
                        self.game.make_particles(e.x, e.y, e.color, n=12)
                        self.game.spawn_pickup(e.x, e.y, 'coin')

        # update bullets and collisions (bullets can destroy enemies)
        for b in self.game.bullets[:]:
            b.update()
            # remove out-of-world bullets
            if b.x < 0 or b.x > self.game.WORLD_WIDTH or b.y < 0 or b.y > self.game.WORLD_HEIGHT:
                self.game.bullets.remove(b)
                continue
            # check collision with enemies
            for e in self.game.enemies:
                if e.alive and e.collide_with_bullet(b):
                    e.alive = False
                    e.death_time = 0  # start death animation
                    # reward player
                    self.game.score += 5
                    # cooler particle effect with more particles
                    self.game.make_particles(e.x, e.y, e.color, n=20)
                    # random pickup drop
                    r = random.random()
                    if r < 0.35:
                        self.game.spawn_pickup(e.x, e.y, 'coin')
                    elif r < 0.7:
                        self.game.spawn_pickup(e.x, e.y, 'ammo')
                    else:
                        self.game.spawn_pickup(e.x, e.y, 'health')
                    if b in self.game.bullets:
                        self.game.bullets.remove(b)
                    break

        # update pickups
        for p in self.game.pickups[:]:
            p['ttl'] -= 1
            if p['ttl'] <= 0:
                try:
                    self.game.pickups.remove(p)
                except ValueError:
                    pass
                continue
            # magnet effect: pull pickups gently toward player when nearby
            if not p.get('picked'):
                dxm = self.game.player.x - p['x']
                dym = self.game.player.y - p['y']
                mdist = (dxm*dxm + dym*dym) ** 0.5
                if mdist < self.game.MAGNET_RADIUS and mdist > 0:
                    p['x'] += (dxm / mdist) * (self.game.MAGNET_STRENGTH * mdist)
                    p['y'] += (dym / mdist) * (self.game.MAGNET_STRENGTH * mdist)
            # if already picked, shrink until consumed
            if p.get('picked'):
                p['size'] = max(0, p.get('size', 6 * self.game.game_zoom) - p.get('shrink_rate', 0.35))
                if p['size'] <= 0:
                    # apply pickup effect when shrink completes
                    if p['kind'] == 'coin':
                        self.game.score += 10
                        self.game.popups.append({'text': '+10', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.game.foam})
                    elif p['kind'] == 'ammo':
                        self.game.AMMO = min(self.game.MAX_AMMO, self.game.AMMO + max(3, self.game.MAX_AMMO // 2))
                        self.game.popups.append({'text': '+Ammo', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.game.green})
                    elif p['kind'] == 'health':
                        self.game.player.hp = min(self.game.player.max_hp, self.game.player.hp + 2)
                        self.game.popups.append({'text': '+HP', 'x': p['x'], 'y': p['y'] - 8, 'life': 60, 'vy': -0.6, 'color': self.game.red})
                    try:
                        self.game.pickups.remove(p)
                    except ValueError:
                        pass
            else:
                # pickup by player (initiate shrink instead of immediate remove)
                dx = p['x'] - self.game.player.x
                dy = p['y'] - self.game.player.y
                if (dx*dx + dy*dy) <= (10 + 6) ** 2:
                    p['picked'] = True

        # update particles
        for q in self.game.particles[:]:
            q['x'] += q['vx']
            q['y'] += q['vy']
            q['vy'] += 0.1
            q['life'] -= 1
            if q['life'] <= 0:
                self.game.particles.remove(q)
                continue

        # floating popups
        for popup in self.game.popups[:]:
            popup['y'] += popup.get('vy', -0.4)
            popup['life'] -= 1
            if popup['life'] <= 0:
                self.game.popups.remove(popup)
                continue

        # check player death
        if self.game.player.hp <= 0:
            # reset to menu and heal player
            self.game.scene = 'menu'
            self.game.player.hp = self.game.player.max_hp
        # remove dead enemies after death animation completes
        for e in self.game.enemies[:]:
            if not e.alive and e.death_time >= e.death_duration:
                self.game.enemies.remove(e)

        # wave management: if all enemies are dead, schedule/advance wave
        alive = any(e.alive for e in self.game.enemies)
        now = time.time()
        if not alive and self.game.wave_active:
            # wave cleared
            self.game.wave_active = False
            self.game.wave_timer = now + self.game.WAVE_DELAY
        if not self.game.wave_active and now >= self.game.wave_timer:
            # advance to next wave
            self.game.wave += 1
            self.game.spawn_enemies(self.game.SETTINGS['enemy_count'] * self.game.wave)
            self.game.wave_active = True

    def draw(self, display):
        display.fill(self.game.ocean_dark)

        # draw tiled world background
        self.game.draw_tiles()

        for e in self.game.enemies:
            e.draw()
        for b in self.game.bullets:
            b.draw()
        for p in self.game.pickups:
            kind = p['kind']
            color = (255, 220, 80) if kind == 'coin' else (120, 255, 160) if kind == 'ammo' else (255, 100, 120)
            screen_px, screen_py = self.game.world_to_screen(p['x'], p['y'])
            sz = int(p.get('size', 6 * self.game.game_zoom))
            pygame.draw.circle(display, color, (int(screen_px), int(screen_py)), sz)
        for q in self.game.particles:
            screen_px, screen_py = self.game.world_to_screen(q['x'], q['y'])
            alpha_ratio = q['life'] / q['max_life'] if q.get('max_life') else 1
            fade_size = int(q.get('size', 2) * self.game.game_zoom * alpha_ratio)
            if fade_size > 0:
                pygame.draw.circle(display, q['color'], (int(screen_px), int(screen_py)), fade_size)

        # draw player, gun and HUD (static)
        self.game.player.draw()
        if self.game.gun_sprite:
            mx, my = pygame.mouse.get_pos()
            world_mx, world_my = self.game.screen_to_world(mx, my)
            ang = math.degrees(math.atan2(world_my - self.game.player.y, world_mx - self.game.player.x))
            w, h = self.game.gun_sprite.get_size()
            w_scaled = int(w * self.game.game_zoom)
            h_scaled = int(h * self.game.game_zoom)
            gun_scaled = pygame.transform.scale(self.game.gun_sprite, (w_scaled, h_scaled))
            rot = pygame.transform.rotate(gun_scaled, -ang)
            player_screen_x, player_screen_y = self.game.world_to_screen(self.game.player.x, self.game.player.y)
            rrect = rot.get_rect(center=(int(player_screen_x), int(player_screen_y)))
            display.blit(rot, rrect.topleft)

        # HUD (ammo / reload progress)
        now = time.time()
        if now < self.game.reload_cooldown:
            remaining = max(0, self.game.reload_cooldown - now)
            progress = 1 - (remaining / self.game.RELOAD_TIME)
            bar_w = 120
            bar_h = 10
            bx = 5
            by = 25
            pygame.draw.rect(display, self.game.ocean_med, (bx, by, bar_w, bar_h))
            pygame.draw.rect(display, self.game.foam, (bx, by, int(bar_w * progress), bar_h))
            reload_surf = self.game.font.render("Reloading...", True, self.game.coral)
            display.blit(reload_surf, (5, 25 + bar_h + 2))
        else:
            ammo_surf = self.game.font.render(f"Ammo: {self.game.AMMO} (R to reload)", True, self.game.foam)
            display.blit(ammo_surf, (5, 25))

        # draw popups
        for popup in self.game.popups[:]:
            sx, sy = self.game.world_to_screen(popup['x'], popup['y'])
            alpha = max(0, int(255 * (popup['life'] / 60)))
            txt = self.game.font.render(popup['text'], True, popup.get('color', self.game.foam))
            display.blit(txt, (int(sx - txt.get_width() / 2), int(sy)))

        # minimap (static)
        map_x = self.game.window_res[0] - self.game.MINIMAP_W - 8
        map_y = 8
        pygame.draw.rect(display, self.game.ocean_med, (map_x, map_y, self.game.MINIMAP_W, self.game.MINIMAP_H))
        pygame.draw.rect(display, self.game.foam, (map_x, map_y, self.game.MINIMAP_W, self.game.MINIMAP_H), 1)
        scale_x = self.game.MINIMAP_W / self.game.WORLD_WIDTH
        scale_y = self.game.MINIMAP_H / self.game.WORLD_HEIGHT
        # enemies
        for e in self.game.enemies:
            ex = map_x + int(e.x * scale_x)
            ey = map_y + int(e.y * scale_y)
            pygame.draw.circle(display, self.game.coral if e.alive else (60,60,60), (ex, ey), 2)
        # player
        px = map_x + int(self.game.player.x * scale_x)
        py = map_y + int(self.game.player.y * scale_y)
        pygame.draw.circle(display, self.game.biolum, (px, py), 3)

        if self.game.paused:
            # paused overlay
            overlay = pygame.Surface((self.game.window_res[0], self.game.window_res[1]), pygame.SRCALPHA)
            overlay.fill((5, 5, 10, 120))
            display.blit(overlay, (0, 0))
            pause_surf = self.game.big_font.render('PAUSED', True, self.game.foam)
            display.blit(pause_surf, (self.game.window_res[0]//2 - pause_surf.get_width()//2, self.game.window_res[1]//2 - pause_surf.get_height()//2))
