import pygame
import pymunk

def createMap(gameSetup):

    # ── Static Map (walls + platforms) ────────────────────────────
    space = gameSetup['space']
    WORLD_HEIGHT = gameSetup['WORLD_HEIGHT']
    WORLD_WIDTH = gameSetup['WORLD_WIDTH']  # why am I doing this.  It is faster than looking it up every time
    static_body = space.static_body

    # Outer world boundaries (thick walls)
    wall_thickness = 50
    walls = [
        pymunk.Segment(static_body, (0, 0), (0, WORLD_HEIGHT), wall_thickness),
        pymunk.Segment(static_body, (WORLD_WIDTH, 0), (WORLD_WIDTH, WORLD_HEIGHT), wall_thickness),
        pymunk.Segment(static_body, (0, 0), (WORLD_WIDTH, 0), wall_thickness),
        pymunk.Segment(static_body, (0, WORLD_HEIGHT), (WORLD_WIDTH, WORLD_HEIGHT), wall_thickness),
    ]
    for wall in walls:
        wall.elasticity = 0.9
        wall.friction = 0.8
    space.add(*walls)

    # Procedural platforms (grid-like map tiles)
    platform_spacing = 450
    platform_width = 250
    platform_thickness = 20
    platforms = []  # Store for reference if needed
    for grid_x in range(150, WORLD_WIDTH - 150, platform_spacing):
        for grid_y in range(150, WORLD_HEIGHT - 150, platform_spacing):
            # Horizontal platform
            plat_h = pymunk.Segment(static_body,
                                (grid_x - platform_width//2, grid_y),
                                (grid_x + platform_width//2, grid_y),
                                platform_thickness)
            plat_h.elasticity = 0.7
            plat_h.friction = 1.0
            space.add(plat_h)
            platforms.append(plat_h)
