import pygame
import pymunk
import pymunk.pygame_util
import math   
import graphics

screen, clock, draw_options, space, player_body, player_image, animation, background = graphics.doGraphicsSetup()

keys = {}
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys[event.key] = True
        if event.type == pygame.KEYUP:
            keys[event.key] = False

    # Controls - Arrow keys or WASD
    if keys.get(pygame.K_LEFT, False) or keys.get(pygame.K_a, False):
        player_body.apply_force_at_local_point((-800, 0), (0, 0))
    if keys.get(pygame.K_RIGHT, False) or keys.get(pygame.K_d, False):
        player_body.apply_force_at_local_point((800, 0), (0, 0))
    if (keys.get(pygame.K_SPACE, False) or keys.get(pygame.K_w, False)) and abs(player_body.velocity.y) < 20:
        player_body.apply_impulse_at_local_point((0, -450), (0, -40))  # jump

    graphics.doGraphicsStep(screen, clock, draw_options, space, player_body, player_image, animation, background)

pygame.quit()