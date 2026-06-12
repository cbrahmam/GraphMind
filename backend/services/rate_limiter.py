import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._hour_windows: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> dict:
        now = time.time()
        self._cleanup(key, now)

        minute_count = len(self._minute_windows[key])
        hour_count = len(self._hour_windows[key])

        if minute_count >= self.rpm:
            wait = 60 - (now - self._minute_windows[key][0])
            return {
                "allowed": False,
                "reason": "rate_limit_minute",
                "limit": self.rpm,
                "remaining": 0,
                "retry_after": round(max(0, wait), 1),
            }

        if hour_count >= self.rph:
            wait = 3600 - (now - self._hour_windows[key][0])
            return {
                "allowed": False,
                "reason": "rate_limit_hour",
                "limit": self.rph,
                "remaining": 0,
                "retry_after": round(max(0, wait), 1),
            }

        return {
            "allowed": True,
            "minute_remaining": self.rpm - minute_count,
            "hour_remaining": self.rph - hour_count,
        }

    def record(self, key: str):
        now = time.time()
        self._minute_windows[key].append(now)
        self._hour_windows[key].append(now)

    def _cleanup(self, key: str, now: float):
        minute_cutoff = now - 60
        hour_cutoff = now - 3600
        self._minute_windows[key] = [t for t in self._minute_windows[key] if t > minute_cutoff]
        self._hour_windows[key] = [t for t in self._hour_windows[key] if t > hour_cutoff]

    def get_stats(self) -> dict:
        now = time.time()
        stats = {}
        all_keys = set(list(self._minute_windows.keys()) + list(self._hour_windows.keys()))
        for key in all_keys:
            self._cleanup(key, now)
            stats[key] = {
                "minute_count": len(self._minute_windows[key]),
                "hour_count": len(self._hour_windows[key]),
                "minute_limit": self.rpm,
                "hour_limit": self.rph,
            }
        return stats

    def reset(self, key: str | None = None):
        if key:
            self._minute_windows.pop(key, None)
            self._hour_windows.pop(key, None)
        else:
            self._minute_windows.clear()
            self._hour_windows.clear()


rate_limiter = RateLimiter()
