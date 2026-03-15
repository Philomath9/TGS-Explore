import pygame
import pymunk
import math
from spritesheet import SpriteSheet
from animation import Animation

class Ant:
    def __init__(self, gameSetup, scale):

        # Load walking animation sprite sheet
        sheet = SpriteSheet("walking.png")

        walk_frames = sheet.get_strip(
            x=0,
            y=0,
            frame_width=64,
            frame_height=64,
            count=6,
            scale=scale
        )

        self.walk_animation = Animation(walk_frames, frame_time=0.08)

        self.current_frame = walk_frames[0]

        # Physics body (rotation locked)
        self.body = pymunk.Body(mass=2.0, moment=math.inf)
        self.body.position = (gameSetup["WORLD_WIDTH"] * 0.5, gameSetup["WORLD_HEIGHT"] * 0.5)

        # Collision box matches sprite size
        width, height = self.current_frame.get_size()

        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = 0.85
        self.shape.elasticity = 0.7
        self.shape.mass = 2.0
        self.shape.color = (255, 120, 120)

        self.angle = 0
        self.turn_speed = 0.15

        self.move_speed = 500.0
        self.move_accel = 24.0
        self.move_decel = 4.5

        self.input_smoothing = 6.0
        self.smoothed_input = pymunk.Vec2d(0.0, 0.0)

        gameSetup["space"].add(self.body, self.shape)

    def update_movement(self, keys, dt):

        #Key inputs
        input_x = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(keys[pygame.K_a] or keys[pygame.K_LEFT])
        input_y = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(keys[pygame.K_s] or keys[pygame.K_DOWN])

        #velocity updates
        input_vec = pymunk.Vec2d(input_x, input_y)
        if input_vec.length > 1:
            input_vec = input_vec.normalized()

        input_blend = min(1.0, self.input_smoothing * dt)
        self.smoothed_input += (input_vec - self.smoothed_input) * input_blend

        desired_velocity = self.smoothed_input * self.move_speed
        response = self.move_accel if input_vec.length > 0 else self.move_decel
        blend = min(1.0, response * dt)

        self.body.velocity += (desired_velocity - self.body.velocity) * blend

        #animation updates
        speed = self.body.velocity.length

        if speed > 5:
            self.walk_animation.update(dt * (speed / self.move_speed) * 6) #Faster animation as speed increases
            self.current_frame = self.walk_animation.get_frame()
        else:
            self.walk_animation.reset()
            self.current_frame = self.walk_animation.get_frame()

    def draw(self, gameSetup, cam_pos, zoom):

        dx = (self.body.position[0] - cam_pos[0]) * zoom
        dy = (cam_pos[1] - self.body.position[1]) * zoom
        sx = dx + gameSetup["WIDTH"] / 2
        sy = dy + gameSetup["HEIGHT"] / 2

        screen_pos = int(sx), int(sy)

        # Rotate ant based on velocity
        vx, vy = self.body.velocity
        speed = math.hypot(vx, vy)

        if speed > 5:
            target_angle = math.degrees(math.atan2(vy, vx)) - 90
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * self.turn_speed

        rotated = pygame.transform.rotate(self.current_frame, self.angle)

        rect = rotated.get_rect(center=screen_pos)
        gameSetup["screen"].blit(rotated, rect)