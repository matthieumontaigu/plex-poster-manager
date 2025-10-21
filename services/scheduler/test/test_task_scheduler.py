# services/tests/test_scheduler_service_unittest.py
from __future__ import annotations

import types
import unittest
import unittest.mock
from datetime import datetime
from zoneinfo import ZoneInfo

# Import the scheduler module so we can patch its 'time'
import services.scheduler.task_scheduler as sched_mod
from services.scheduler.schedules import DailyAt, Every
from services.scheduler.task_scheduler import TaskSchedulerService


class FakeClock:
    """Deterministic clock; advances only when sleep() is called."""

    def __init__(self, start_epoch: float):
        self.now = start_epoch

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            self.now += seconds


class BaseSchedulerTest(unittest.TestCase):
    def setUp(self):
        # Each test will set these explicitly
        self.clock: FakeClock | None = None
        self.time_patcher = None

    def _patch_time(self, clock: FakeClock):
        """Patch services.scheduler.service.time with a fake providing time() and sleep()."""
        self.clock = clock
        fake_time_module = types.SimpleNamespace(time=clock.time, sleep=clock.sleep)
        self.time_patcher = unittest.mock.patch.object(
            sched_mod, "time", fake_time_module
        )
        self.time_patcher.start()

    def tearDown(self):
        if self.time_patcher:
            self.time_patcher.stop()


class TestTaskSchedulerService(BaseSchedulerTest):
    def test_every_runs_immediately_and_then_on_interval(self):
        """
        Expect: Every(10) runs at t0, then t0+10, then t0+20.
        """
        t0 = 1_700_000_000.0
        clock = FakeClock(start_epoch=t0)
        self._patch_time(clock)

        events: list[float] = []
        holder: dict[str, TaskSchedulerService | None] = {"scheduler": None}

        def run_task():
            events.append(clock.now)
            if len(events) >= 3 and holder["scheduler"] is not None:
                holder["scheduler"].stop()

        holder["scheduler"] = TaskSchedulerService(
            [
                (
                    "every10",
                    run_task,
                    Every(10),
                ),
            ]
        )

        holder["scheduler"].start()
        self.assertEqual(events, [t0, t0 + 10, t0 + 20])

    def test_two_every_tasks_both_fire_at_start_then_follow_intervals(self):
        """
        Two tasks:
          - A: Every(10)
          - B: Every(15)
        Both should run at t0; subsequent executions follow their intervals.
        """
        t0 = 2_000_000_000.0
        clock = FakeClock(start_epoch=t0)
        self._patch_time(clock)

        events: list[tuple[str, float]] = []
        holder: dict[str, TaskSchedulerService | None] = {"scheduler": None}

        def make_runner(name: str):
            def _run():
                events.append((name, clock.now))
                # Stop after we see 4 events to keep the test bounded
                if len(events) >= 4 and holder["scheduler"] is not None:
                    holder["scheduler"].stop()

            return _run

        holder["scheduler"] = TaskSchedulerService(
            [
                ("A", make_runner("A"), Every(10)),
                ("B", make_runner("B"), Every(15)),
            ]
        )

        holder["scheduler"].start()

        times_A = [t for (n, t) in events if n == "A"]
        times_B = [t for (n, t) in events if n == "B"]

        # Both have run at t0
        self.assertIn(t0, times_A)
        self.assertIn(t0, times_B)

        # Next occurrences should align with intervals
        self.assertTrue((t0 + 10 in times_A) or (t0 + 20 in times_A))
        self.assertTrue((t0 + 15 in times_B) or (t0 + 30 in times_B))

    def test_dailyat_runs_at_next_6am_paris(self):
        """
        A DailyAt(06:00 Europe/Paris) task scheduled at 05:58 should run at 06:00 local.
        """
        paris = ZoneInfo("Europe/Paris")
        start_dt = datetime(2025, 10, 21, 5, 58, tzinfo=paris)
        run_dt = datetime(2025, 10, 21, 6, 0, tzinfo=paris)

        clock = FakeClock(start_epoch=start_dt.timestamp())
        self._patch_time(clock)

        fired_at: list[float] = []
        holder: dict[str, TaskSchedulerService | None] = {"scheduler": None}

        def daily_job():
            fired_at.append(clock.now)
            if holder["scheduler"] is not None:
                holder["scheduler"].stop()

        holder["scheduler"] = TaskSchedulerService(
            [
                ("logo_cleaner", daily_job, DailyAt(6, 0, tz="Europe/Paris")),
            ]
        )

        holder["scheduler"].start()

        self.assertEqual(len(fired_at), 1)
        self.assertAlmostEqual(fired_at[0], run_dt.timestamp(), delta=1e-6)

    def test_every_can_delay_first_run_if_supported(self):
        """
        If Every supports run_at_start=False via first_run(), the first run should be delayed by the interval.
        Otherwise, skip this test.
        """
        # Check capability dynamically
        try:
            supports_first_run = hasattr(Every(1), "first_run")
        except Exception:  # constructor might be strict; still fine
            supports_first_run = False

        if not supports_first_run:
            self.skipTest("Every.first_run not implemented")

        t0 = 3_000_000_000.0
        clock = FakeClock(start_epoch=t0)
        self._patch_time(clock)

        events: list[float] = []
        holder: dict[str, TaskSchedulerService | None] = {"scheduler": None}

        def run_task():
            events.append(clock.now)
            if holder["scheduler"] is not None:
                holder["scheduler"].stop()

        # Try creating a delayed Every; if constructor doesn't accept the kw, skip.
        try:
            delayed_every = Every(10, run_at_start=False)  # type: ignore[arg-type]
        except TypeError:
            self.skipTest("Every(run_at_start=...) not supported")

        holder["scheduler"] = TaskSchedulerService(
            [
                ("delayed", run_task, delayed_every),
            ]
        )

        holder["scheduler"].start()

        self.assertEqual(events, [t0 + 10])


if __name__ == "__main__":
    # Allows running the tests directly: `python -m services.tests.test_scheduler_service_unittest`
    import unittest.mock  # needed because we reference unittest.mock in BaseSchedulerTest

    unittest.main()
