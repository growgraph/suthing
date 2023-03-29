from timeit import default_timer


class Timer:
    def __init__(self):
        self.timer = default_timer
        self.mins = 0
        self.secs = 0
        self.elapsed = 0

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed = end - self.start
        self.mins = int(self.elapsed / 60)
        self.secs = int(self.elapsed - (self.mins * 60))
