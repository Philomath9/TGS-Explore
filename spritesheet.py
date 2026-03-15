import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    # Get the individual frame
    def get_frame(self, x, y, width, height, scale=1):
        rect = pygame.Rect(x, y, width, height)
        frame = self.sheet.subsurface(rect)

        if scale != 1:
            frame = pygame.transform.smoothscale(
                frame,
                (int(width * scale), int(height * scale))
            )

        return frame

    # Get the list of frames
    def get_strip(self, x, y, frame_width, frame_height, count, scale=1):
        frames = []

        for i in range(count):
            frame = self.get_frame(
                x + i * frame_width,
                y,
                frame_width,
                frame_height,
                scale
            )
            frames.append(frame)

        return frames