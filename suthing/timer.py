"""Simple timer utility for code performance measurement."""

from timeit import default_timer

seconds_per_minute = 60


class Timer:
    """Context manager for timing code execution."""

    def __init__(self):
        """Initialize timer with default settings."""
        self.timer = default_timer
        self.mins = 0
        self.secs = 0
        self.elapsed = 0

    def __enter__(self):
        """Start timing on context enter.

        Returns:
            self: Timer instance
        """
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        """Stop timing on context exit and calculate elapsed time."""
        end = self.timer()
        self.elapsed = end - self.start
        self.mins = int(self.elapsed / seconds_per_minute)
        self.secs = int(self.elapsed - (self.mins * seconds_per_minute))

    @property
    def elapsed_str(self, digits: int = 2) -> str:
        """Get formatted string of elapsed time.

        Args:
            digits: Number of decimal places for seconds

        Returns:
            Formatted time string (e.g. "1 min 30.5 sec")
        """
        mins = int(self.elapsed / seconds_per_minute)
        secs = round(self.elapsed - (mins * seconds_per_minute), digits)
        r = f"{secs} sec"
        if mins > 0:
            r = f"{mins} min " + r
        return r
