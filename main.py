
import pygame
import pymunk
import math
import random
import graphicsAndSound  
import map
import asyncio
from ant import Ant
from circle import CircleManager
from block import Block

gameSetup = {}

graphicsAndSound.doGraphicsSetup(gameSetup)
map.createMap(gameSetup)


# ── Player ────────────────────────────────────────────────────
player = Ant(gameSetup, 1.6)
blocks = []
for _ in range(20):
    blocks.append(Block(gameSetup))

# ── Enhanced Camera (follow + pan/zoom) ──────────────────────
class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_x = gameSetup["WORLD_WIDTH"] * 0.5
        self.center_y = gameSetup["WORLD_HEIGHT"] * 0.5
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.zoom = 1.0
        self.lerp_speed = 0.12  # Smooth follow (0=instant, 1=no follow)

    def update(self, target_pos):
        # Lerp to offsetted player position
        target_x = target_pos[0] + self.pan_offset_x
        target_y = target_pos[1] + self.pan_offset_y
        self.center_x += (target_x - self.center_x) * self.lerp_speed
        self.center_y += (target_y - self.center_y) * self.lerp_speed
        
        # Clamp to world bounds (zoom-aware)
        half_view_w = (self.screen_width * 0.5) / self.zoom
        half_view_h = (self.screen_height * 0.5) / self.zoom
        self.center_x = max(half_view_w, min(gameSetup["WORLD_WIDTH"] - half_view_w, self.center_x))
        self.center_y = max(half_view_h, min(gameSetup["WORLD_HEIGHT"] - half_view_h, self.center_y))

camera = Camera(gameSetup["WIDTH"], gameSetup["HEIGHT"])

# ── Mouse State ──────────────────────────────────────────────
panning = False
last_mouse_pos = (0, 0)
pan_button = 3  # Right mouse button

# ── Circle Manager ────────────────────────────────────────────
circle_manager = CircleManager(gameSetup, spawn_interval=2.0, max_circles=10)

# ── Drawing Helpers (zoom-aware, Y-flip) ─────────────────────
def world_to_screen(world_pos, cam_center, zoom):
    """Convert world pos to screen pos (zoom + Y-flip)."""
    dx = (world_pos[0] - cam_center[0]) * zoom
    dy = (cam_center[1] - world_pos[1]) * zoom
    sx = dx + gameSetup["WIDTH"] / 2
    sy = dy + gameSetup["HEIGHT"] / 2
    return int(sx), int(sy)

def draw_segment(screen, seg, cam_center, zoom, color=(220, 220, 220)):
    sa = world_to_screen(seg.a, cam_center, zoom)
    sb = world_to_screen(seg.b, cam_center, zoom)
    width = max(1, int(seg.radius * zoom * 1.8))
    pygame.draw.line(screen, color, sa, sb, width)

def draw_circle(screen, pos, radius, color, cam_center, zoom):
    screen_pos = world_to_screen(pos, cam_center, zoom)
    rad = int(radius * zoom)
    pygame.draw.circle(screen, color, screen_pos, rad)

# ── Main Loop ─────────────────────────────────────────────────
running = True
start_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds

while running:
    dt = gameSetup["clock"].tick(60) / 1000.0
 #   mx, my = pygame.mouse.get_pos()
 #   if(mx < gameSetup["WIDTH"] * 0.1):
 #       camera.pan_offset_x -= 10 / camera.zoom
 #   if(mx > gameSetup["WIDTH"] * 0.9):
 #       camera.pan_offset_x += 10 / camera.zoom
 #   if(my < gameSetup["HEIGHT"] * 0.1):
 #       camera.pan_offset_y += 10 / camera.zoom
 #   if(my > gameSetup["HEIGHT"] * 0.9):
 #       camera.pan_offset_y -= 10 / camera.zoom

    gameSetup['screen'].blit(gameSetup['backgroundimage'], (0, 0))


    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # ── Mouse Pan (Right Drag) ──────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left Click: Spawn box
                Block.spawn_block_at_mouse(event.pos, camera, blocks, gameSetup)

    player.update_movement(keys, dt)
    # ── Circle Manager Update ──────────────────────────────────
    circle_manager.update(dt, player)

    # ── Physics Step ────────────────────────────────────────────
    gameSetup["space"].step(1 / 60.0)

    # ── Update Camera ───────────────────────────────────────────
    camera.update(player.body.position)
    cam_pos = (camera.center_x, camera.center_y)
    zoom = camera.zoom

    # ── Render ──────────────────────────────────────────────────
    #gameSetup["screen"].fill((25, 35, 60))  # Dark BG

    bcount = 0
    # Draw ALL shapes (static + dynamic)
    for shape in gameSetup["space"].shapes:
        if shape.body is gameSetup["space"].static_body:
            # Static segments (walls/platforms)
            if isinstance(shape, pymunk.Segment):
                draw_segment(gameSetup["screen"], shape, cam_pos, zoom)
        else:
            # Dynamic shapes
            if isinstance(shape, pymunk.Circle):
                # Check if circle has a custom color (yellow spawned circles)
                if hasattr(shape, 'color'):
                    color = shape.color
                else:
                    color = (255, 150, 150) if shape.body == player.body else (150, 220, 255)
                draw_circle(gameSetup["screen"], shape.body.position, shape.radius, color, cam_pos, zoom)
            elif isinstance(shape, pymunk.Poly) and shape != player.shape:
                # Rotated polygon
                verts_screen = [world_to_screen(v.rotated(shape.body.angle) + shape.body.position, cam_pos, zoom)
                for v in shape.get_vertices()]
                color = (150, 220, 255, 180)  # Semi-transparent blue boxes
                pygame.draw.polygon(gameSetup["screen"], color, verts_screen)
                # Outline
                pygame.draw.polygon(gameSetup["screen"], (255, 255, 255), verts_screen, width=max(1, int(2 * zoom)))
                if(shape.body.position.y < 160):
                    bcount = bcount +1
            elif isinstance(shape, pymunk.Poly):
                player.draw(gameSetup, cam_pos, zoom)

    if bcount == 20:
        win_font = pygame.font.SysFont(None, 64)
        win_text = win_font.render("You Win! Time: " + timer_text, True, (255, 255, 100))
        gameSetup["screen"].blit(win_text, (gameSetup["WIDTH"] // 2 - win_text.get_width() // 2, gameSetup["HEIGHT"] // 2 - win_text.get_height() // 2))
        asyncio.sleep(2)
        running = False

    # ── HUD ─────────────────────────────────────────────────────
    font = pygame.font.SysFont(None, 32)
    score_text = font.render(f"Score: {circle_manager.get_score()}", True, (255, 255, 100))
    gameSetup["screen"].blit(score_text, (20, 20))
    
    pos_text = font.render(f"World: {player.body.position.x:.0f}, {player.body.position.y:.0f}", True, (255,255,255))
    gameSetup["screen"].blit(pos_text, (20, 60))
    
    pan_text = font.render(f"Blocks Below: {bcount:.0f}", True, (200, 200, 255))
    gameSetup["screen"].blit(pan_text, (20, 100))
    
    ctrl_text = pygame.font.SysFont(None, 24).render("ESC=Quit | WASD=Move | Right Drag=Pan | Wheel=Zoom | LClick=Spawn", True, (150, 150, 150))
    gameSetup["screen"].blit(ctrl_text, (20, gameSetup["HEIGHT"] - 40))
    
    # Timer display
    elapsed_time = pygame.time.get_ticks() / 1000.0 - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timer_surface = font.render(timer_text, True, (255, 255, 100))
    gameSetup["screen"].blit(timer_surface, (gameSetup['WIDTH'] - 200, 20))

    pygame.display.flip()

pygame.quit()