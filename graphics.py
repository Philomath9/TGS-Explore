import pygame
import pymunk
import pymunk.pygame_util
import math 

def doGraphicsSetup():
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    space = pymunk.Space()
    space.gravity = (0, 1200)

    
    # Floor
    floor = pymunk.Segment(space.static_body, (0, 500), (900, 500), 30)
    floor.friction = 0.50
    space.add(floor)

    # Player with LOCKED ROTATION
    player_body = pymunk.Body(mass=1, moment=math.inf)  # locks rotation by setting moment of inertia to infinity
    player_body.position = 200, 300
    player_shape = pymunk.Poly.create_box(player_body, (40, 80))
    player_shape.friction = 0.9
    player_shape.elasticity = 0.1
    space.add(player_body, player_shape)
    return screen, clock, draw_options, space, player_body

def doGraphicsStep(screen, clock, draw_options, space):
    space.step(1/60.0)

    screen.fill((18, 20, 35))
    space.debug_draw(draw_options)
    pygame.display.flip()
    clock.tick(60)