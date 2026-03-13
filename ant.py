import pygame
import pymunk
import math

class Ant:
    def __init__(self, gameSetup, scale):

        # Load and Scale sprite for ant
        original = pygame.image.load(r"TGS-Explore\Sprites\ant.png").convert_alpha()
        ow, oh = original.get_size()
        width = int(ow * scale)
        height = int(oh * scale)
        self.image = pygame.transform.smoothscale(original, (width, height))

        # Physics body (rotation locked)
        self.body = pymunk.Body(mass=2.0, moment=math.inf)
        self.body.position = (gameSetup["WORLD_WIDTH"] * 0.5, gameSetup["WORLD_HEIGHT"] * 0.5)

        # Collision box matches scaled image
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = 0.85
        self.shape.elasticity = 0.7
        self.shape.mass = 2.0

        self.shape.color = (255, 120, 120)  # For debug draw if needed

        gameSetup["space"].add(self.body, self.shape)
    
    def draw(self, gameSetup, cam_pos, zoom):
        
        #Rewrites world_to_screen(), could be done more properly

        dx = (self.body.position[0] - cam_pos[0]) * zoom
        dy = (cam_pos[1] - self.body.position[1]) * zoom
        sx = dx + gameSetup["WIDTH"] / 2
        sy = dy + gameSetup["HEIGHT"] / 2

        screen_pos = int(sx), int(sy)
        rect = self.image.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
        gameSetup["screen"].blit(self.image, rect)