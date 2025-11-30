import pygame
import json
import os

import logging

class Map:
    def __init__(self, game, map_name):
        self.game = game
        self.name = map_name
        self.obstacles = []
        self.waves = []
        self.load_map_data()

    def load_map_data(self):
        map_path = os.path.join(os.path.dirname(__file__), 'maps', f'{self.name}.json')
        if not os.path.isfile(map_path):
            logging.error(f"Map file not found at {map_path}")
            return

        with open(map_path, 'r') as f:
            data = json.load(f)
            self.obstacles = data.get('obstacles', [])
            self.waves = data.get('waves', [])

    def draw_obstacles(self):
        for obstacle in self.obstacles:
            x, y, w, h = obstacle
            screen_x, screen_y = self.game.world_to_screen(x, y)
            rect = pygame.Rect(screen_x, screen_y, w * self.game.game_zoom, h * self.game.game_zoom)
            pygame.draw.rect(self.game.display, self.game.ocean_light, rect)
            pygame.draw.rect(self.game.display, self.game.ocean_accent, rect, 2)
