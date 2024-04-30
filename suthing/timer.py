from timeit import default_timer

seconds_per_minute = 60


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
        self.mins = int(self.elapsed / seconds_per_minute)
        self.secs = int(self.elapsed - (self.mins * seconds_per_minute))

    @property
    def elapsed_str(self, digits=2):
        mins = int(self.elapsed / seconds_per_minute)
        secs = round(self.elapsed - (mins * seconds_per_minute), digits)
        r = f"{secs} sec"
        if mins > 0:
            r = f"{mins} min " + r

        return r
