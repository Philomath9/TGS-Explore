class Animation:
    def __init__(self, frames, frame_time=0.1, loop=True):
        self.frames = frames
        self.frame_time = frame_time
        self.loop = loop

        self.timer = 0
        self.index = 0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        self.timer += dt

        if self.timer >= self.frame_time:
            self.timer = 0
            self.index += 1

            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        return self.frames[self.index]

    def reset(self):
        self.index = 0
        self.timer = 0
        self.finished = False