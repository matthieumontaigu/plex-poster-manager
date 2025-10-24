from __future__ import annotations

import heapq
import logging
import signal
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime

from services.scheduler.schedules import Schedule

logger = logging.getLogger(__name__)


# ---------- Internal data ----------


@dataclass(order=True)
class _ScheduledTask:
    next_run: float
    name: str = field(compare=False)
    run: Callable[[], None] = field(compare=False, repr=False)
    schedule: Schedule = field(compare=False, repr=False)

    def reschedule(self) -> None:
        self.next_run = self.schedule.next_after(time.time())


# ---------- CPU-efficient scheduler ----------


class TaskSchedulerService:
    """
    Simple scheduler that sleeps until the next planned task.
    Extremely lightweight — ideal for low-power or embedded systems.
    """

    def __init__(self, tasks: Iterable[tuple[str, Callable[[], None], Schedule]]):
        self._heap: list[_ScheduledTask] = []
        now = time.time()
        for name, fn, sched in tasks:
            task = _ScheduledTask(
                # Use first_run() for the initial scheduling
                next_run=sched.first_run(now),
                name=name,
                run=fn,
                schedule=sched,
            )
            heapq.heappush(self._heap, task)

        self._running = False
        self._stopping = False
        self._install_signal_handlers()

    # Graceful shutdown support
    def _install_signal_handlers(self) -> None:
        def _handler(signum, _frame):
            logger.info(f"Received signal {signum}, stopping scheduler...")
            self.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _handler)
            except Exception:
                pass

    def start(self) -> None:
        logger.info("Starting TaskSchedulerService (efficient mode)")
        self._running = True
        try:
            while self._running and self._heap:
                # Peek next task
                next_task = self._heap[0]
                now = time.time()
                sleep_for = next_task.next_run - now

                if sleep_for > 0:
                    # Sleep until next scheduled task or shutdown
                    logger.debug(f"Sleeping {sleep_for:.1f}s until '{next_task.name}'")
                    self._sleep_until(next_task.next_run)
                    if self._stopping:
                        break
                    continue

                # Run due task
                task = heapq.heappop(self._heap)
                self._run_task(task)
                task.reschedule()
                heapq.heappush(self._heap, task)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt -> stopping")
            self.stop()
        except Exception:
            logger.exception("Scheduler crashed unexpectedly")
        finally:
            self._running = False
            logger.info("TaskSchedulerService stopped.")

    def stop(self) -> None:
        self._stopping = True
        self._running = False

    def _sleep_until(self, target_epoch: float) -> None:
        """Sleep efficiently until target time, allowing interrupt."""
        while not self._stopping:
            now = time.time()
            remaining = target_epoch - now
            if remaining <= 0:
                break
            # Sleep once for the full remaining time
            time.sleep(remaining)
            # If woken by signal handler, exit loop
            if self._stopping:
                break

    def _run_task(self, task: _ScheduledTask) -> None:
        start = time.time()
        logger.info(f"▶ Running task '{task.name}'")
        try:
            task.run()
        except Exception:
            logger.exception(f"Task '{task.name}' failed")
        finally:
            duration = time.time() - start
            logger.info(f"⏹ Finished '{task.name}' in {duration:.2f}s")
