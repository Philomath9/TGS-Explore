import pygame
import pymunk
import pymunk.pygame_util
import math 

def doGraphicsSetup(gameSetup):
    pygame.init()
# ── Full Screen Setup ────────────────────────────────────────
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("TGSgame")
    clock = pygame.time.Clock()

    # Large world (map size)
    WORLD_WIDTH, WORLD_HEIGHT = 4000, 4000

    # Pymunk physics space
    space = pymunk.Space()
    space.gravity = (0, 0)      # No gravity for top-down
    space.damping = 0.92        # Air resistance for smooth stopping

    gameSetup['screen'] = screen
    gameSetup['space'] = space
    gameSetup['info'] = info
    gameSetup['WORLD_WIDTH'] = WORLD_WIDTH
    gameSetup['WORLD_HEIGHT'] = WORLD_HEIGHT
    gameSetup['clock'] = clock
    gameSetup['WIDTH'] = WIDTH
    gameSetup['HEIGHT'] = HEIGHT

def doGraphicsStep(gameSetup):
    gameSetup['space'].step(1/60.0)

    gameSetup['screen'].fill((18, 20, 35))
    gameSetup['space'].debug_draw(gameSetup['draw_options'])
    pygame.display.flip()
    gameSetup['clock'].tick(60)