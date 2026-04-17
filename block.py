import pymunk
import random

class Block:
    def __init__(self, gameSetup, position=None, size=(60, 40), mass=3):
        self.gameSetup = gameSetup
        self.size = size

        # Random position if not provided
        if position is None:
            x = random.uniform(50, gameSetup["WORLD_WIDTH"] - 50)
            y = random.uniform(50, gameSetup["WORLD_HEIGHT"] - 50)
            position = (x, y)

        # Create physics body
        self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        self.body.position = position

        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.elasticity = 0.8
        self.shape.friction = 0.7
        self.shape.color = (100, 200, 255)

        gameSetup["space"].add(self.body, self.shape)

    def spawn_block_at_mouse(mouse_pos, camera, gameSetup):
        mx, my = mouse_pos

        screen_center_x = gameSetup["WIDTH"] / 2
        screen_center_y = gameSetup["HEIGHT"] / 2

        dx = (mx - screen_center_x) / camera.zoom
        dy = (screen_center_y - my) / camera.zoom

        world_x = camera.center_x + dx
        world_y = camera.center_y + dy

        # Clamp
        world_x = max(50, min(gameSetup["WORLD_WIDTH"] - 50, world_x))
        world_y = max(50, min(gameSetup["WORLD_HEIGHT"] - 50, world_y))

        Block(gameSetup, position=(world_x, world_y))
        gameSetup['spawn_sound'].play()