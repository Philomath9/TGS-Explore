import pygame
import pymunk
import math

class Ant:
    def __init__(self, gameSetup, scale):

        # Load and Scale sprite for ant
        original = pygame.image.load(r"ant.png").convert_alpha()
        ow, oh = original.get_size()
        width = int(ow * scale)
        height = int(oh * scale)
        self.original_image = pygame.transform.smoothscale(original, (width, height))
        self.image = self.original_image

        # Physics body (rotation locked)
        self.body = pymunk.Body(mass=2.0, moment=math.inf)
        self.body.position = (gameSetup["WORLD_WIDTH"] * 0.5, gameSetup["WORLD_HEIGHT"] * 0.5)

        # Collision box matches scaled image
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = 0.85
        self.shape.elasticity = 0.7
        self.shape.mass = 2.0

        self.shape.color = (255, 120, 120)  # For debug draw if needed

        self.angle = 0

        gameSetup["space"].add(self.body, self.shape)

    def move(self, direction, thrust_force):
        force = (0,0)
        if direction == 'left':
            force = (-thrust_force, 0)
        if direction == 'right':
            force = (thrust_force, 0)
        if direction == 'up':
            force = (0, thrust_force)
        if direction == 'down':
            force = (0, -thrust_force)
        
        if force != (0, 0):
            # Change 'local' to 'world' to ignore the player's rotation
            self.body.apply_force_at_world_point(force, self.body.position)


    
    def draw(self, gameSetup, cam_pos, zoom):
        
        #Rewrites world_to_screen(), could be done more properly

        dx = (self.body.position[0] - cam_pos[0]) * zoom
        dy = (cam_pos[1] - self.body.position[1]) * zoom
        sx = dx + gameSetup["WIDTH"] / 2
        sy = dy + gameSetup["HEIGHT"] / 2

        screen_pos = int(sx), int(sy)

        # Turn Ant based off its velocity
        vx, vy = self.body.velocity
        speed = math.hypot(vx, vy)
        if speed > 5:
            self.angle = math.degrees(math.atan2(vy, vx)) - 90

        rotated = pygame.transform.rotate(self.original_image, self.angle)

        rect = rotated.get_rect(center=screen_pos)
        gameSetup["screen"].blit(rotated, rect)