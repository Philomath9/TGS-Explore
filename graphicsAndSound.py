import pygame
import pymunk
import pymunk.pygame_util
import math 

def doGraphicsSetup(gameSetup):
    pygame.init()
    pygame.mixer.init()
# ── Full Screen Setup ────────────────────────────────────────
    info = pygame.display.Info()
    #WIDTH = info.current_w
    #HEIGHT = info.current_h
    WIDTH = 800
    HEIGHT = 600
    #screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TGSgame")
    clock = pygame.time.Clock()

    # Large world (map size)
    WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000

    # Pymunk physics space
    space = pymunk.Space()
    space.gravity = (0, 0)      # No gravity for top-down
    space.damping = 0.92        # Air resistance for smooth stopping
    #loadsoundeffects
    gameSetup['spawn_sound'] = pygame.mixer.Sound("spawn.mp3")
    #gameSetup['jump_sound'] = pygame.mixer.Sound("jump.wav")
    #gameSetup['jump_sound'] = pygame.mixer.Sound("jump.wav")
    #gameSetup['jump_sound'] = pygame.mixer.Sound("jump.wav")




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