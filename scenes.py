import pygame
import sys
import time
import math
import random
import logging
from entities import Bullet

class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def draw(self, display):
        raise NotImplementedError

    def draw_text(self, text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_button(self, text, x, y, w, h, inactive_color, active_color, is_selected=False):
        mouse = pygame.mouse.get_pos()
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)
        on_button = rect.collidepoint(mouse)

        if on_button or is_selected:
            pygame.draw.rect(self.game.display, active_color, rect, border_radius=5)
        else:
            pygame.draw.rect(self.game.display, inactive_color, rect, border_radius=5)

        pygame.draw.rect(self.game.display, self.game.ocean_accent, rect, 2, border_radius=5)
        self.draw_text(text, self.game.font, self.game.white, self.game.display, x, y)

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
                    button_rect = pygame.Rect(0, 0, 250, 50)
                    button_rect.center = (self.game.window_res[0] // 2, 250 + i * 60)
                    if button_rect.collidepoint(mx, my):
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
        title_surf = self.game.big_font.render("One In The Chamber", True, self.game.biolum)
        title_rect = title_surf.get_rect(center=(self.game.window_res[0]//2, 100))
        display.blit(title_surf, title_rect)
        self.game.draw_glow(title_rect.center, 120, self.game.biolum, 0.15)

        for i, item in enumerate(self.menu_items):
            self.draw_button(
                item,
                self.game.window_res[0] // 2,
                250 + i * 60,
                250, 50,
                self.game.ocean_med,
                self.game.ocean_light,
                is_selected=(i == self.menu_index)
            )

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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                back_button_rect = pygame.Rect(0, 0, 150, 50)
                back_button_rect.center = (self.game.window_res[0] // 2, 420)
                if back_button_rect.collidepoint(mx, my):
                    self.game.scene = 'menu'

    def update(self):
        pass

    def draw(self, display):
        display.fill(self.game.ocean_dark)
        self.draw_text('Settings', self.game.big_font, self.game.biolum, display, self.game.window_res[0] // 2, 60)

        for i, key in enumerate(self.settings_items):
            val = self.game.SETTINGS[key]
            label = f"{key.replace('_', ' ').title()}: < {val} >"
            self.draw_button(
                label,
                self.game.window_res[0] // 2,
                150 + i * 60,
                300, 50,
                self.game.ocean_med,
                self.game.ocean_light,
                is_selected=(i == self.settings_index)
            )

        self.draw_button("Back", self.game.window_res[0] // 2, 420, 150, 50, self.game.ocean_med, self.game.ocean_light)

class UpgradesScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tabs = ['Stats', 'Power-Ups']
        self.current_tab_index = 0
        self.upgrades_index = 0
        self._update_upgrade_lists()

    def _update_upgrade_lists(self):
        self.stat_upgrades = [up for up in self.game.upgrades if up.category == 'stat']
        self.power_up_upgrades = [up for up in self.game.upgrades if up.category == 'power_up']

    def get_current_upgrades(self):
        if self.tabs[self.current_tab_index] == 'Stats':
            return self.stat_upgrades
        else:
            return self.power_up_upgrades

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_tab_index = (self.current_tab_index - 1) % len(self.tabs)
                    self.upgrades_index = 0
                if event.key == pygame.K_RIGHT:
                    self.current_tab_index = (self.current_tab_index + 1) % len(self.tabs)
                    self.upgrades_index = 0
                if event.key == pygame.K_UP:
                    current_upgrades = self.get_current_upgrades()
                    if current_upgrades:
                        self.upgrades_index = (self.upgrades_index - 1) % len(current_upgrades)
                if event.key == pygame.K_DOWN:
                    current_upgrades = self.get_current_upgrades()
                    if current_upgrades:
                        self.upgrades_index = (self.upgrades_index + 1) % len(current_upgrades)
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.purchase_upgrade()
                if event.key == pygame.K_ESCAPE:
                    self.game.scene = 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                # Tab buttons
                for i, tab_name in enumerate(self.tabs):
                    tab_rect = pygame.Rect(0, 0, 140, 40)
                    tab_rect.center = (self.game.window_res[0] // 2 + (i * 150) - 75, 100)
                    if tab_rect.collidepoint(mx, my):
                        self.current_tab_index = i
                        self.upgrades_index = 0
                        return

                # Upgrade buttons
                current_upgrades = self.get_current_upgrades()
                for i, up in enumerate(current_upgrades):
                    button_rect = pygame.Rect(0, 0, 400, 50)
                    button_rect.center = (self.game.window_res[0] // 2, 200 + i * 60)
                    if button_rect.collidepoint(mx, my):
                        self.upgrades_index = i
                        self.purchase_upgrade()

                # Back button
                back_button_rect = pygame.Rect(0, 0, 150, 50)
                back_button_rect.center = (self.game.window_res[0] // 2, 420)
                if back_button_rect.collidepoint(mx, my):
                    self.game.scene = 'menu'

    def purchase_upgrade(self):
        current_upgrades = self.get_current_upgrades()
        if current_upgrades:
            upgrade = current_upgrades[self.upgrades_index]
            upgrade.apply_upgrade(self.game)

    def update(self):
        self._update_upgrade_lists()

    def draw(self, display):
        display.fill(self.game.ocean_dark)
        self.draw_text('Upgrades', self.game.big_font, self.game.biolum, display, self.game.window_res[0] // 2, 40)

        # Draw tabs
        for i, tab_name in enumerate(self.tabs):
            self.draw_button(
                tab_name,
                self.game.window_res[0] // 2 + (i * 150) - 75,
                100,
                140, 40,
                self.game.ocean_med,
                self.game.ocean_light,
                is_selected=(i == self.current_tab_index)
            )

        # Draw upgrades for the current tab
        current_upgrades = self.get_current_upgrades()
        for i, up in enumerate(current_upgrades):
            cost_text = f"Cost: {up.cost}" if up.cost != "Unlocked" else "Unlocked"
            level_text = f"Lvl {up.level} " if up.category == 'stat' else ""
            label = f"{level_text}{up.name}  -  {cost_text}"

            self.draw_button(
                label,
                self.game.window_res[0] // 2,
                200 + i * 60,
                400, 50,
                self.game.ocean_med,
                self.game.ocean_light,
                is_selected=(i == self.upgrades_index)
            )

        self.draw_button("Back", self.game.window_res[0] // 2, 420, 150, 50, self.game.ocean_med, self.game.ocean_light)
        self.draw_text(f"Coins: {self.game.score}", self.game.font, self.game.biolum, display, self.game.window_res[0] - 10, 10, center=False)

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
                        length = math.hypot(dir_x, dir_y)
                        if length != 0:
                            dir_x /= length
                            dir_y /= length
                        # decrement ammo properly
                        if self.game.AMMO > 0:
                            self.game.AMMO -= 1
                            self.game.bullets.append(Bullet(self.game, self.game.player.x, self.game.player.y, (dir_x, dir_y)))
                            shoot_delay = self.game.SHOOT_DELAY
                            if 'rapid_fire' in self.game.active_power_ups:
                                shoot_delay /= 2
                            self.game.shoot_cooldown = now + shoot_delay
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
                    if now >= self.game.shield_last_used + self.game.SHIELD_COOLDOWN:
                        self.game.shield_last_used = now
                        self.game.shield_end_time = now + self.game.SHIELD_DURATION
                        self.game.shield_active = True
                if event.key == pygame.K_ESCAPE:
                    self.game.scene = 'menu'

    def update(self):
        if self.game.paused:
            return

        # Power-up effects
        original_speed = self.game.SETTINGS['player_speed']
        original_shoot_delay = self.game.SHOOT_DELAY

        now = time.time()
        active_effects = self.game.active_power_ups.copy()

        for effect, end_time in active_effects.items():
            if now > end_time:
                del self.game.active_power_ups[effect]
                continue

            if effect == 'speed_boost':
                original_speed *= 1.5
            if effect == 'rapid_fire':
                original_shoot_delay /= 2
            if effect == 'invincibility':
                self.game.shield_active = True
                self.game.shield_end_time = end_time

        # handle continuous key presses for movement (only in game scene)
        self.game.player.prev_x = self.game.player.x
        self.game.player.prev_y = self.game.player.y
        keys = pygame.key.get_pressed()
        speed = original_speed
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
        if self.game.shield_end_time <= time.time():
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
                dist_ep = math.hypot(dx, dy)
                if dist_ep <= 16:
                    # if shield is active, push enemy away and prevent damage
                    if self.game.shield_active:
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
            if not (0 < b.x < self.game.WORLD_WIDTH and 0 < b.y < self.game.WORLD_HEIGHT):
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
                        # 10% chance to drop a power-up instead of a regular pickup
                        if random.random() < 0.1:
                            unlocked_power_ups = [up.key for up in self.game.upgrades if up.category == 'power_up' and up.level > 0]
                            if unlocked_power_ups:
                                power_up_type = random.choice(unlocked_power_ups)
                                self.game.spawn_power_up(e.x, e.y, power_up_type)
                        else:
                            self.game.spawn_pickup(e.x, e.y, 'health')
                    if b in self.game.bullets:
                        self.game.bullets.remove(b)
                    break

        # update power-ups
        for p in self.game.power_ups[:]:
            p.update()
            # Check for collision with player
            dx = p.x - self.game.player.x
            dy = p.y - self.game.player.y
            if math.hypot(dx, dy) < 20:  # 20 is the collision radius
                self.game.active_power_ups[p.type] = time.time() + p.duration
                self.game.power_ups.remove(p)

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
                mdist = math.hypot(dxm, dym)
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
                if math.hypot(dx, dy) <= 16:
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
        self.game.enemies = [e for e in self.game.enemies if e.alive or e.death_time < e.death_duration]

        # wave management: if all enemies are dead, schedule/advance wave
        alive = any(e.alive for e in self.game.enemies)
        now = time.time()
        if not alive and self.game.wave_active:
            # wave cleared
            self.game.wave_active = False
            self.game.wave_timer = now + self.game.WAVE_DELAY
        if not self.game.wave_active and now >= self.game.wave_timer:
            # advance to next wave
            if self.game.wave < len(self.game.current_map.waves):
                self.game.wave += 1
                self.game.spawn_enemies(self.game.current_map.waves[self.game.wave - 1]['count'])
                self.game.wave_active = True
            else:
                # All waves cleared, move to the next map
                self.game.current_map_index = (self.game.current_map_index + 1) % len(self.game.available_maps)
                self.game.start_game()

    def draw(self, display):
        display.fill(self.game.ocean_dark)

        # draw tiled world background
        self.game.draw_tiles()

        # draw map obstacles
        if self.game.current_map:
            self.game.current_map.draw_obstacles()

        for e in self.game.enemies:
            e.draw()
        for b in self.game.bullets:
            b.draw()
        for p in self.game.power_ups:
            p.draw()
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

        # HUD
        hud_surface = pygame.Surface((self.game.window_res[0], 150), pygame.SRCALPHA)
        hud_surface.fill((10, 20, 30, 180))
        display.blit(hud_surface, (0, 0))

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
            display.blit(reload_surf, (5, 50))
        else:
            ammo_surf = self.game.font.render(f"Ammo: {self.game.AMMO}", True, self.game.foam)
            display.blit(ammo_surf, (5, 25))

        score_surf = self.game.font.render(f"Score: {self.game.score}", True, self.game.biolum)
        display.blit(score_surf, (5, 5))

        wave_surf = self.game.font.render(f"Wave: {self.game.wave}", True, self.game.biolum)
        display.blit(wave_surf, (self.game.window_res[0] - wave_surf.get_width() - 5, 5))

        shield_cooldown_remaining = max(0, self.game.shield_last_used + self.game.SHIELD_COOLDOWN - now)
        if shield_cooldown_remaining > 0:
            shield_text = f"Shield CD: {shield_cooldown_remaining:.1f}"
            shield_color = self.game.coral
        else:
            shield_text = "Shield Ready"
            shield_color = self.game.green
        shield_surf = self.game.font.render(shield_text, True, shield_color)
        display.blit(shield_surf, (5, 75))

        # Display active power-ups
        power_up_y = 100
        for effect, end_time in self.game.active_power_ups.items():
            remaining_time = max(0, end_time - now)
            power_up_text = f"{effect.replace('_', ' ').title()}: {remaining_time:.1f}s"
            power_up_surf = self.game.font.render(power_up_text, True, self.game.biolum)
            display.blit(power_up_surf, (5, power_up_y))
            power_up_y += 25

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
