import time

class FpsCounter:
    def __init__(self):
        self.start_time = time.time()
        self.count = 0
        self.fps = 0

    def Count(self):
        self.count += 1
        # second
        t_diff = time.time() - self.start_time
        if(t_diff) > 1:
            self.fps = self.count / t_diff
            self.start_time = time.time()
            self.count = 0

    def GetFps(self):
        return self.fps
