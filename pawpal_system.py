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

    @property
    def times_per_day(self) -> int:
        return 2 if self.frequency == Frequency.TWICE_DAILY else 1

    def is_due(self) -> bool:
        return self.completions_today < self.times_per_day

    def mark_complete(self) -> None:
        self.completions_today += 1

    def reset_daily(self) -> None:
        self.completions_today = 0

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


@dataclass
class DailyPlan:
    date: date
    scheduled_items: list[tuple[Task, time]] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def add_item(self, task: Task, start_time: time) -> None:
        self.scheduled_items.append((task, start_time))

    def get_summary(self) -> str:
        lines = [f"Daily Plan for {self.date}\n"]
        for task, start_time in self.scheduled_items:
            lines.append(f"  [{start_time}] {task.name} ({task.duration_minutes} min)")
        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.name} (not enough time)")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, profile: PetProfile):
        self.profile = profile

    def generate_plan(self, plan_date: date) -> DailyPlan:
        plan = DailyPlan(date=plan_date)
        prioritized = self.prioritize_tasks()
        budget = self.profile.available_minutes_per_day
        occupied: list[tuple[datetime, datetime]] = []
        # Flexible tasks start at 8:00 AM and are placed sequentially
        flex_cursor = datetime.combine(plan_date, time(8, 0))

        for task in prioritized:
            if not task.is_due():
                continue
            if task.duration_minutes > budget:
                plan.skipped_tasks.append(task)
                continue

            if task.preferred_time:
                start_dt = datetime.combine(plan_date, task.preferred_time)
                end_dt = start_dt + timedelta(minutes=task.duration_minutes)
                if any(start_dt < occ_end and end_dt > occ_start for occ_start, occ_end in occupied):
                    plan.skipped_tasks.append(task)
                    continue
                occupied.append((start_dt, end_dt))
                plan.add_item(task, task.preferred_time)
            else:
                # Advance flex_cursor past any conflicting occupied windows
                flex_cursor = self._next_free_slot(flex_cursor, task.duration_minutes, occupied)
                end_dt = flex_cursor + timedelta(minutes=task.duration_minutes)
                occupied.append((flex_cursor, end_dt))
                plan.add_item(task, flex_cursor.time())
                flex_cursor = end_dt

            budget -= task.duration_minutes

        return plan

    def prioritize_tasks(self) -> list[Task]:
        # Sort by priority descending, then time-sensitive tasks first
        return sorted(
            self.profile.get_all_tasks(),
            key=lambda t: (-(t.priority), t.preferred_time is None)
        )

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
