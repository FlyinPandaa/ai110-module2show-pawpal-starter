from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Optional
from enum import Enum


class Frequency(str, Enum):
    DAILY = "daily"
    TWICE_DAILY = "twice-daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: int           # 1 (low) to 5 (critical)
    frequency: Frequency
    description: str = ""
    preferred_time: Optional[time] = None
    completions_today: int = 0
    next_due_date: Optional[date] = None  # auto-set by mark_complete()

    @property
    def times_per_day(self) -> int:
        return 2 if self.frequency == Frequency.TWICE_DAILY else 1

    def is_due(self, today: Optional[date] = None) -> bool:
        """Returns True if this task needs to run on `today`.
        - If next_due_date is None the task has never run, so it is always due.
        - TWICE_DAILY: also checks completions_today to allow a second run same day.
        - All others: due when today >= next_due_date.
        """
        today = today or date.today()
        if self.next_due_date is None:
            return True
        if self.frequency == Frequency.TWICE_DAILY:
            return today >= self.next_due_date and self.completions_today < self.times_per_day
        return today >= self.next_due_date

    def mark_complete(self, today: Optional[date] = None) -> None:
        """Mark this occurrence done and schedule the next one automatically."""
        today = today or date.today()
        self.completions_today += 1
        if self.frequency == Frequency.DAILY:
            self.next_due_date = today + timedelta(days=1)
        elif self.frequency == Frequency.TWICE_DAILY:
            # Still due today if second run hasn't happened yet; otherwise tomorrow
            if self.completions_today < self.times_per_day:
                self.next_due_date = today
            else:
                self.next_due_date = today + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            self.next_due_date = today + timedelta(days=7)

    def reset_daily(self, today: Optional[date] = None) -> None:
        """Reset daily/twice-daily counters at the start of a new day."""
        if self.frequency != Frequency.WEEKLY:
            self.completions_today = 0
            self.next_due_date = today or date.today()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency.value,
            "description": self.description,
            "preferred_time": str(self.preferred_time) if self.preferred_time else None,
            "completions_today": self.completions_today,
            "next_due_date": str(self.next_due_date) if self.next_due_date else None,
        }


@dataclass
class PetProfile:
    owner_name: str
    pet_name: str
    species: str
    available_minutes_per_day: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def get_summary(self) -> str:
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return (
            f"Owner: {self.owner_name} | Pet: {self.pet_name} ({self.species}) | "
            f"Daily budget: {self.available_minutes_per_day} min | Special needs: {needs}"
        )

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_all_tasks(self) -> list[Task]:
        return self.tasks

    # ── Filtering ─────────────────────────────────────────────────────────────

    def get_pending_tasks(self, today: Optional[date] = None) -> list[Task]:
        """Tasks that still need to run today."""
        return [t for t in self.tasks if t.is_due(today)]

    def get_completed_tasks(self, today: Optional[date] = None) -> list[Task]:
        """Tasks already completed / not due."""
        return [t for t in self.tasks if not t.is_due(today)]

    def get_tasks_by_category(self, category: str) -> list[Task]:
        """Filter tasks by category (e.g. 'medical', 'exercise')."""
        return [t for t in self.tasks if t.category == category]


@dataclass
class DailyPlan:
    date: date
    scheduled_items: list[tuple[Task, time]] = field(default_factory=list)
    skipped_tasks: list[tuple[Task, str]] = field(default_factory=list)  # (task, reason)
    reasoning: str = ""

    def add_item(self, task: Task, start_time: time) -> None:
        self.scheduled_items.append((task, start_time))

    def add_skip(self, task: Task, reason: str) -> None:
        self.skipped_tasks.append((task, reason))

    def has_conflict(self) -> bool:
        """Returns True if any two scheduled items overlap in time."""
        windows = []
        for task, start_time in self.scheduled_items:
            start_dt = datetime.combine(self.date, start_time)
            end_dt = start_dt + timedelta(minutes=task.duration_minutes)
            windows.append((start_dt, end_dt))
        for i, (s1, e1) in enumerate(windows):
            for s2, e2 in windows[i + 1:]:
                if s1 < e2 and e1 > s2:
                    return True
        return False

    def get_summary(self) -> str:
        lines = [f"Daily Plan for {self.date}\n"]
        for task, start_time in self.scheduled_items:
            lines.append(f"  [{start_time}] {task.name} ({task.duration_minutes} min)")
        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task, reason in self.skipped_tasks:
                lines.append(f"  - {task.name} ({reason})")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, profile: PetProfile):
        self.profile = profile

    def generate_plan(self, plan_date: date) -> DailyPlan:
        plan = DailyPlan(date=plan_date)
        budget = self.profile.available_minutes_per_day
        occupied: list[tuple[datetime, datetime]] = []
        flex_cursor = datetime.combine(plan_date, time(8, 0))

        for task in self.prioritize_tasks():
            if not task.is_due(plan_date):
                continue
            if task.duration_minutes > budget:
                plan.add_skip(task, "over budget")
                continue
            result = self._place_task(task, plan_date, plan, occupied, flex_cursor)
            if result is not None:
                flex_cursor = result
                budget -= task.duration_minutes

        return plan

    def prioritize_tasks(self) -> list[Task]:
        """Sort by priority (desc), then time-sensitive first, then by preferred_time."""
        return sorted(
            self.profile.get_all_tasks(),
            key=lambda t: (
                -(t.priority),
                t.preferred_time is None,
                t.preferred_time or time.max,
            )
        )

    def detect_conflicts(self, plan_date: date) -> list[str]:
        """Check all due tasks with a preferred_time for overlapping windows.
        Returns a list of warning strings — one per conflict pair.
        Does not raise exceptions or modify any state.
        """
        warnings = []
        timed_tasks = [
            t for t in self.profile.get_all_tasks()
            if t.preferred_time and t.is_due(plan_date)
        ]
        for i, a in enumerate(timed_tasks):
            a_start = datetime.combine(plan_date, a.preferred_time)
            a_end = a_start + timedelta(minutes=a.duration_minutes)
            for b in timed_tasks[i + 1:]:
                b_start = datetime.combine(plan_date, b.preferred_time)
                b_end = b_start + timedelta(minutes=b.duration_minutes)
                if a_start < b_end and a_end > b_start:
                    warnings.append(
                        f"WARNING: '{a.name}' ({a.preferred_time}, {a.duration_minutes} min) "
                        f"conflicts with '{b.name}' ({b.preferred_time}, {b.duration_minutes} min)"
                    )
        return warnings

    def _place_task(
        self,
        task: Task,
        plan_date: date,
        plan: DailyPlan,
        occupied: list[tuple[datetime, datetime]],
        flex_cursor: datetime,
    ) -> Optional[datetime]:
        """Schedule one task. Returns updated flex_cursor if placed, None if skipped due to conflict."""
        if task.preferred_time:
            start_dt = datetime.combine(plan_date, task.preferred_time)
            end_dt = start_dt + timedelta(minutes=task.duration_minutes)
            for occ_start, occ_end in sorted(occupied):
                if occ_start >= end_dt:
                    break  # no further overlap possible
                if start_dt < occ_end and end_dt > occ_start:
                    plan.add_skip(task, "time conflict")
                    return None
            occupied.append((start_dt, end_dt))
            plan.add_item(task, task.preferred_time)
            return flex_cursor  # unchanged for timed tasks
        else:
            flex_cursor = self._next_free_slot(flex_cursor, task.duration_minutes, occupied)
            end_dt = flex_cursor + timedelta(minutes=task.duration_minutes)
            occupied.append((flex_cursor, end_dt))
            plan.add_item(task, flex_cursor.time())
            return end_dt

    async def explain_plan(self, plan: DailyPlan) -> str:
        # To be implemented: calls Claude API with plan context
        # and returns a natural language explanation of scheduling decisions
        pass

    @staticmethod
    def _next_free_slot(
        cursor: datetime, duration: int, occupied: list[tuple[datetime, datetime]]
    ) -> datetime:
        """Advance cursor forward until it no longer conflicts with any occupied window."""
        end = cursor + timedelta(minutes=duration)
        for occ_start, occ_end in sorted(occupied):
            if cursor < occ_end and end > occ_start:
                cursor = occ_end
                end = cursor + timedelta(minutes=duration)
        return cursor
