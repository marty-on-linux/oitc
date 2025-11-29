import pygame
import random
import time
import math

class Upgrade:
    def __init__(self, name, key, inc, base_cost, cost_scaling, category='stat'):
        self.name = name
        self.key = key
        self.inc = inc
        self.base_cost = base_cost
        self.cost_scaling = cost_scaling
        self.level = 0
        self.category = category

    @property
    def cost(self):
        if self.category == 'power_up' and self.level > 0:
            return "Unlocked"
        return int(self.base_cost * (self.cost_scaling ** self.level))

    def apply_upgrade(self, game):
        cost = self.cost
        if isinstance(cost, str) or game.score < cost:
            return

        if self.category == 'power_up' and self.level > 0:
            return

        game.score -= cost
        self.level += 1

        if self.category == 'stat':
            if self.key == 'shield_duration':
                game.SHIELD_DURATION += self.inc
            elif self.key == 'shield_cooldown':
                game.SHIELD_COOLDOWN = max(0, game.SHIELD_COOLDOWN - self.inc)
            else:
                game.SETTINGS[self.key] = game.SETTINGS.get(self.key, 0) + self.inc
                if self.key == 'max_ammo':
                    game.MAX_AMMO = game.SETTINGS['max_ammo']
                if self.key == 'player_speed':
                    game.PLAYER_SPEED = game.SETTINGS['player_speed']

class Player:
    def __init__(self, game):
        self.game = game
        self.x = self.game.WORLD_WIDTH / 2
        self.y = self.game.WORLD_HEIGHT / 2
        self.prev_x = self.x
        self.prev_y = self.y
        self.width = 32
        self.height = 32
        # health
        self.max_hp = 5
        self.hp = self.max_hp
    def draw(self):
        screen_x, screen_y = self.game.world_to_screen(self.x, self.y)
        # draw sprite if available, otherwise a small fallback marker
        if self.game.player_sprite:
            w, h = self.game.player_sprite.get_size()
            w = int(w * self.game.game_zoom)
            h = int(h * self.game.game_zoom)
            scaled = pygame.transform.scale(self.game.player_sprite, (w, h))
            self.game.display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
        else:
            # small, unobtrusive fallback marker (no large glow)
            pygame.draw.circle(self.game.display, self.game.white, (int(screen_x), int(screen_y)), int(6 * self.game.game_zoom))
        # draw a clearer health bar and ammo counter above the player's head
        bar_w = 64 * self.game.game_zoom
        bar_h = 8 * self.game.game_zoom
        hp_ratio = max(0, self.hp) / self.max_hp
        bx = screen_x - bar_w/2
        by = screen_y - 26 * self.game.game_zoom
        # background
        pygame.draw.rect(self.game.display, self.game.ocean_dark, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        # empty bar
        pygame.draw.rect(self.game.display, (60, 60, 60), (bx, by, bar_w, bar_h))
        # filled hp
        hp_color = (int(255*(1-hp_ratio)), int(255*hp_ratio), 40) if hp_ratio < 0.5 else self.game.biolum
        pygame.draw.rect(self.game.display, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h))
        # numeric hp label
        hp_label = self.game.font.render(f"HP: {self.hp}/{self.max_hp}", True, self.game.white)
        self.game.display.blit(hp_label, (int(screen_x - hp_label.get_width()/2), int(by - hp_label.get_height() - 5)))
        # ammo counter to the right of the HP bar
        ammo_text = f"Ammo: {self.game.AMMO}/{self.game.MAX_AMMO}"
        ammo_surf = self.game.font.render(ammo_text, True, self.game.foam)
        self.game.display.blit(ammo_surf, (int(bx + bar_w + 10 * self.game.game_zoom), int(by - 5)))
        # draw shield bubble if active
        if self.game.shield_end_time > time.time():
            # radius shrinks as remaining time approaches zero
            rem = self.game.shield_end_time - time.time()
            max_r = 42 * self.game.game_zoom
            radius = max(2, int(max_r * (rem / self.game.SHIELD_DURATION)))
            width = max(1, int(3 * self.game.game_zoom))
            pygame.draw.circle(self.game.display, self.game.ocean_accent, (int(screen_x), int(screen_y)), radius, width)
    # convenience: keep inside bounds
    def clamp(self, w, h):
        # World boundaries
        self.x = max(self.width / 2, min(self.x, w - self.width / 2))
        self.y = max(self.height / 2, min(self.y, h - self.height / 2))

        # Obstacle collisions
        if self.game.current_map:
            for obstacle in self.game.current_map.obstacles:
                ox, oy, ow, oh = obstacle
                # Check for collision
                if (self.x < ox + ow and self.x + self.width > ox and
                        self.y < oy + oh and self.y + self.height > oy):
                    # Collision detected, move player back to previous position
                    self.x = self.prev_x
                    self.y = self.prev_y

class Bullet:
    def __init__(self, game, x, y, direction):
        self.game = game
        self.x = x
        self.y = y
        self.direction = direction
        self.trail_counter = 0
    def draw(self):
        screen_x, screen_y = self.game.world_to_screen(self.x, self.y)
        # draw a visible solid core for the bullet first (bright), then a smaller accent and subtle glow
        core_r = int(4 * self.game.game_zoom)
        accent_r = int(2 * self.game.game_zoom)
        # core (bright) to make bullet easily visible (gold)
        pygame.draw.circle(self.game.display, (255, 220, 80), (int(screen_x), int(screen_y)), core_r)
        # inner accent for color
        pygame.draw.circle(self.game.display, self.game.ocean_accent, (int(screen_x), int(screen_y)), accent_r)
        # small subtle glow (reduced intensity)
        self.game.draw_glow((screen_x, screen_y), 6 * self.game.game_zoom, self.game.ocean_accent, 0.08)
    def update(self):
        spd = self.game.SETTINGS.get('bullet_speed', 5)
        self.x += self.direction[0] * spd
        self.y += self.direction[1] * spd
        # add trail particles
        self.trail_counter += 1
        if self.trail_counter % 4 == 0:
            # fewer trail particles and in a different color so they don't mask the bullet core
            self.game.make_particles(self.x, self.y, self.game.ocean_accent, n=1)

class Enemy:
    def __init__(self, game, x, y, speed):
        self.game = game
        self.x = x
        self.y = y
        self.speed = speed
        self.alive = True
        # ocean themed colors
        self.color = random.choice([self.game.coral, self.game.biolum, self.game.ocean_accent, (150, 200, 255), (100, 180, 200)])
        # optionally assign a sprite
        self.sprite = None
        self.avoid_radius = 60  # separation radius to avoid clustering
        # death animation
        self.death_time = 0  # frames since death started (0 = alive)
        self.death_duration = 12  # frames to animate death

    def draw(self):
        screen_x, screen_y = self.game.world_to_screen(self.x, self.y)

        if self.alive:
            if self.sprite:
                w, h = self.sprite.get_size()
                w = int(w * self.game.game_zoom)
                h = int(h * self.game.game_zoom)
                scaled = pygame.transform.scale(self.sprite, (w, h))
                self.game.display.blit(scaled, (int(screen_x - w/2), int(screen_y - h/2)))
            else:
                pygame.draw.circle(self.game.display, self.color, (int(screen_x), int(screen_y)), int(10 * self.game.game_zoom))
                # glow effect
                self.game.draw_glow((screen_x, screen_y), 15 * self.game.game_zoom, self.color, 0.15)
        else:
            # death animation: rely on particles only (no large glow circle)
            # spawn a short burst of particles on death start
            if self.death_time == 0:
                self.game.make_particles(self.x, self.y, self.color, n=8)
            # optionally draw a subtle fading dot (very small)
            if self.death_time < self.death_duration:
                alpha_progress = 1 - (self.death_time / self.death_duration)
                small_r = max(1, int(6 * self.game.game_zoom * alpha_progress))
                pygame.draw.circle(self.game.display, self.color, (int(screen_x), int(screen_y)), small_r)

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

class PowerUp:
    def __init__(self, game, x, y, power_up_type):
        self.game = game
        self.x = x
        self.y = y
        self.type = power_up_type
        self.creation_time = time.time()
        self.lifespan = 10  # Power-up disappears after 10 seconds
        self.size = 12 * self.game.game_zoom

        # Define properties for each power-up type
        if self.type == 'rapid_fire':
            self.color = (255, 255, 0)  # Yellow
            self.duration = 5
        elif self.type == 'speed_boost':
            self.color = (0, 255, 255)  # Cyan
            self.duration = 8
        elif self.type == 'invincibility':
            self.color = (255, 128, 0)  # Orange
            self.duration = 5
        else:
            self.color = (255, 255, 255) # Default to white
            self.duration = 5

    def draw(self):
        # Draw the power-up as a rotating star
        screen_x, screen_y = self.game.world_to_screen(self.x, self.y)
        angle = (time.time() * 180) % 360  # Rotate over time
        points = []
        for i in range(5):
            # Outer point
            outer_angle = (angle + i * 72) * (3.14159 / 180)
            points.append((screen_x + self.size * 1.2 * math.cos(outer_angle),
                           screen_y + self.size * 1.2 * math.sin(outer_angle)))
            # Inner point
            inner_angle = (angle + (i * 72 + 36)) * (3.14159 / 180)
            points.append((screen_x + self.size * 0.6 * math.cos(inner_angle),
                           screen_y + self.size * 0.6 * math.sin(inner_angle)))

        pygame.draw.polygon(self.game.display, self.color, points)
        self.game.draw_glow((screen_x, screen_y), 20 * self.game.game_zoom, self.color, 0.15)

    def update(self):
        # Check if the power-up's lifespan has expired
        if time.time() - self.creation_time > self.lifespan:
            self.game.power_ups.remove(self)
