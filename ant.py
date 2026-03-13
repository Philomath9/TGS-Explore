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
        self.turn_speed = 0.15
        self.move_speed = 500.0
        self.move_accel = 24.0
        self.move_decel = 4.5
        self.input_smoothing = 6.0
        self.smoothed_input = pymunk.Vec2d(0.0, 0.0)

        gameSetup["space"].add(self.body, self.shape)

    def update_movement(self, keys, dt):
        input_x = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(keys[pygame.K_a] or keys[pygame.K_LEFT])
        input_y = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(keys[pygame.K_s] or keys[pygame.K_DOWN])

        input_vec = pymunk.Vec2d(input_x, input_y)
        if input_vec.length > 1:
            input_vec = input_vec.normalized()

        input_blend = min(1.0, self.input_smoothing * dt)
        self.smoothed_input += (input_vec - self.smoothed_input) * input_blend

        desired_velocity = self.smoothed_input * self.move_speed
        response = self.move_accel if input_vec.length > 0 else self.move_decel
        blend = min(1.0, response * dt)
        self.body.velocity += (desired_velocity - self.body.velocity) * blend


    
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

            # Target angle
            target_angle = math.degrees(math.atan2(vy, vx)) - 90

            # Shortest rotation direction
            diff = (target_angle - self.angle + 180) % 360 - 180

            # Smooth turn
            self.angle += diff * self.turn_speed

        # Rotate sprite
        rotated = pygame.transform.rotate(self.original_image, self.angle)

        rect = rotated.get_rect(center=screen_pos)
        gameSetup["screen"].blit(rotated, rect)