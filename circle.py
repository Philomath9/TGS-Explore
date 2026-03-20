import pygame
import pymunk
import math
import random


class CircleManager:
    def __init__(self, gameSetup, spawn_interval=2.0, max_circles=10):
        self.gameSetup = gameSetup
        self.spawn_timer = 0.0
        self.spawn_interval = spawn_interval
        self.spawned_circles = []
        self.max_circles = max_circles
        self.score = 0

    def update(self, dt, player):
        """Update circles: spawn new ones and handle collisions."""
        # ── Spawn Yellow Circles ────────────────────────────────────
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.spawned_circles) < self.max_circles:
            self.spawn_timer = 0.0
            self._spawn_circle()

        # ── Collision Detection (Yellow Circles) ────────────────────
        circles_to_remove = []
        for circle in self.spawned_circles:
            # Check if circle is still in space (not removed)
            if circle.body in self.gameSetup["space"].bodies:
                # Calculate distance between player and circle
                dx = player.body.position.x - circle.body.position.x
                dy = player.body.position.y - circle.body.position.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Get player's collision radius from bounding box
                vertices = player.shape.get_vertices()
                if vertices:
                    # Calculate approximate radius as distance from center to first vertex
                    max_dist = 0
                    for v in vertices:
                        dist = math.sqrt(v.x**2 + v.y**2)
                        max_dist = max(max_dist, dist)
                    player_radius = max_dist
                else:
                    player_radius = 50  # Fallback
                
                circle_radius = circle.radius
                # Collision if distance < sum of radii
                if distance < player_radius + circle_radius:
                    # Remove circle from physics space
                    self.gameSetup["space"].remove(circle.body, circle)
                    circles_to_remove.append(circle)
                    self.score += 1
        
        # Remove collected circles from tracking list
        for circle in circles_to_remove:
            self.spawned_circles.remove(circle)

    def _spawn_circle(self):
        """Spawn a new yellow circle at random position."""
        spawn_x = random.randint(100, self.gameSetup["WORLD_WIDTH"] - 100)
        spawn_y = random.randint(100, self.gameSetup["WORLD_HEIGHT"] - 100)
        
        # Create yellow circle
        circle_body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, 15))
        circle_body.position = (spawn_x, spawn_y)
        circle_shape = pymunk.Circle(circle_body, 15)
        circle_shape.elasticity = 0.8
        circle_shape.friction = 0.5
        circle_shape.color = (255, 255, 0)  # Yellow
        
        self.gameSetup["space"].add(circle_body, circle_shape)
        self.spawned_circles.append(circle_shape)

    def get_score(self):
        """Get current score."""
        return self.score

    def get_circles(self):
        """Get list of spawned circles."""
        return self.spawned_circles
