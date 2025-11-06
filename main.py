import pygame
import sys

pygame.init()

window_res = (800, 480)
window_title = "One In The Chamber"
# window_icon = pygame.image.load('')
display = pygame.display.set_mode(window_res)
pygame.display.set_caption(window_title)

# font for FPS counter
font = pygame.font.SysFont(None, 24)

# basic colours
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
# game update loop
running = True
clock = pygame.time.Clock()
# player movement speed (pixels per frame)
PLAYER_SPEED = 3

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self):
        pygame.draw.circle(display, white, (int(self.x), int(self.y)), 5)
    # convenience: keep inside bounds
    def clamp(self, w, h):
        self.x = max(0, min(self.x, w - 1))
        self.y = max(0, min(self.y, h - 1))
player = Player(400, 240)

while running:
    # clear screen first, then handle events, draw, and flip
    display.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # handle continuous key presses for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.y += PLAYER_SPEED

    # keep player on-screen
    player.clamp(window_res[0], window_res[1])

    # draw and show FPS
    player.draw()
    fps_surf = font.render(f"FPS: {int(clock.get_fps())}", True, white)
    display.blit(fps_surf, (5, 5))

    # update the full display and cap the frame rate
    pygame.display.flip()
    clock.tick(60)


