from datetime import datetime
from datetime import time as dtime
from datetime import timedelta
from zoneinfo import ZoneInfo


class Schedule:
    def first_run(self, now_epoch: float) -> float:
        # By default, first run behaves like a normal next run
        return self.next_after(now_epoch)

    def next_after(self, now_epoch: float) -> float:
        raise NotImplementedError


class Every(Schedule):
    def __init__(self, seconds: int, run_at_start: bool = True):
        if seconds <= 0:
            raise ValueError("Interval must be > 0")
        self.seconds = int(seconds)
        self.run_at_start = run_at_start

    def first_run(self, now_epoch: float) -> float:
        return now_epoch if self.run_at_start else now_epoch + self.seconds

    def next_after(self, now_epoch: float) -> float:
        return now_epoch + self.seconds


class DailyAt(Schedule):
    """Run once per day at HH:MM in given timezone."""

    def __init__(self, hour: int, minute: int = 0, tz: str = "Europe/Paris"):
        self.hour = hour
        self.minute = minute
        self.tz = ZoneInfo(tz)

    def next_after(self, now_epoch: float) -> float:
        now = datetime.fromtimestamp(now_epoch, tz=self.tz)
        candidate = datetime.combine(
            now.date(), dtime(self.hour, self.minute), tzinfo=self.tz
        )
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.timestamp()


def get_schedule_from_config(type: str, params: tuple[int, ...]) -> Schedule:
    if type == "every":
        if len(params) != 1:
            raise ValueError("Every schedule requires 1 parameter: seconds")
        return Every(params[0])

    elif type == "daily_at":
        if len(params) != 2:
            raise ValueError("DailyAt schedule requires 2 parameters: hour, minute")
        return DailyAt(params[0], params[1])

    else:
        raise ValueError(f"Unknown schedule type: {type}")
