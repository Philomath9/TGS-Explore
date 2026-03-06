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
    player_shape.color = (255, 0, 0, 0)  # Red color for debugging
    space.add(player_body, player_shape)
    
    # Load player walking animation frames
    player_frames = []
    for i in range(1, 5):  # Load player_walk_1.png, player_walk_2.png, etc.
        try:
            frame = pygame.image.load(f'player_walk_{i}.png').convert_alpha()
            frame = pygame.transform.smoothscale(frame, (80, 80))
            player_frames.append(frame)
        except pygame.error:
            # If frames don't exist, use the main player.png
            if i == 1:
                player_image = pygame.image.load('player.png').convert_alpha()
                player_image = pygame.transform.smoothscale(player_image, (80, 80))
                player_frames.append(player_image)


    # Load background image
    background = pygame.image.load('Background.png')
    background = pygame.transform.smoothscale(background, (900, 600))
    
    # Animation state
    animation = {
        'frame': 0,
        'frame_counter': 0,
        'is_moving': False,
        'frames': player_frames,
        'parallax_offset': 0
    }
    
    return screen, clock, draw_options, space, player_body, player_frames[0], animation, background

def doGraphicsStep(screen, clock, draw_options, space, player_body, player_image, animation, background):
    space.step(1/60.0)

    # Update parallax scrolling based on player velocity
    velocity = player_body.velocity
    animation['parallax_offset'] += velocity.x * 0.1  # Scale factor for parallax effect
    
    # Clamp parallax offset to prevent excessive scrolling
    animation['parallax_offset'] = max(-100, min(100, animation['parallax_offset']))
    
    # Draw background with parallax offset
    screen.blit(background, (int(animation['parallax_offset']), 0))
    
    # Update animation based on movement
    velocity = player_body.velocity
    is_moving = abs(velocity.x) > 10
    
    if is_moving:
        animation['frame_counter'] += 1
        # Change frame every 8 ticks for walking animation
        if animation['frame_counter'] >= 8:
            animation['frame_counter'] = 0
            animation['frame'] = (animation['frame'] + 1) % len(animation['frames'])
        
        # Get current frame and flip based on direction
        display_image = animation['frames'][animation['frame']]
        if velocity.x < 0:
            display_image = pygame.transform.flip(display_image, True, False)
    else:
        # Reset animation when not moving
        animation['frame'] = 0
        animation['frame_counter'] = 0
        display_image = animation['frames'][0]
    
    # Draw player image at player position
    player_pos = player_body.position
    image_rect = display_image.get_rect(center=player_pos)
    screen.blit(display_image, image_rect)
    
    pygame.display.flip()
    clock.tick(60)