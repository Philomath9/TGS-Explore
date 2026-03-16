import pygame
import pymunk
import math
from spritesheet import SpriteSheet
from animation import Animation

class Ant:
    def __init__(self, gameSetup, scale):

        # Load walking animation sprite sheet
        walk_sheet = SpriteSheet("walking.png")
        idle_sheet = SpriteSheet("idle.png")

        walk_frames = walk_sheet.get_strip(
            x=0,
            y=0,
            frame_width=64,
            frame_height=64,
            count=6,
            scale=scale
        )

        idle_frames = idle_sheet.get_strip(x=0, y=0, frame_width=64, frame_height=64, count=6, scale=scale)

        # Animation dictionary
        self.animations = {
            "idle": Animation(idle_frames, frame_time=0.12),
            "walk": Animation(walk_frames, frame_time=0.08)
        }

        self.state = "idle"
        self.current_animation = self.animations[self.state]
        self.current_frame = self.current_animation.get_frame()

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
            self.set_state("walk")
        else:
            self.set_state("idle")

        # animation playback
        if self.state == "walk":
            self.current_animation.update(dt * (speed / self.move_speed) * 6)
        else:
            self.current_animation.update(dt)

        self.current_frame = self.current_animation.get_frame()


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
    

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.current_animation = self.animations[self.state]
            self.current_animation.reset()