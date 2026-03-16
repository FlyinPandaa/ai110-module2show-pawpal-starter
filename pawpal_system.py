from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional


@dataclass
class PetProfile:
    owner_name: str
    pet_name: str
    species: str
    available_minutes_per_day: int
    special_needs: list[str] = field(default_factory=list)

    def get_summary(self) -> str:
        pass


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: int  # 1 (low) to 5 (critical)
    preferred_time: Optional[time] = None

    def to_dict(self) -> dict:
        pass


@dataclass
class DailyPlan:
    date: date
    scheduled_items: list[tuple["Task", time]] = field(default_factory=list)
    skipped_tasks: list["Task"] = field(default_factory=list)
    reasoning: str = ""

    def add_item(self, task: "Task", start_time: time) -> None:
        self.scheduled_items.append((task, start_time))

    def get_summary(self) -> str:
        pass


@dataclass
class Scheduler:
    profile: PetProfile
    tasks: list[Task] = field(default_factory=list)

    def generate_plan(self, plan_date: date) -> DailyPlan:
        plan = DailyPlan(date=plan_date)
        prioritized = self.prioritize_tasks()
        budget = self.profile.available_minutes_per_day

        for task in prioritized:
            if task.duration_minutes <= budget:
                budget -= task.duration_minutes
                plan.add_item(task, task.preferred_time)
            else:
                plan.skipped_tasks.append(task)

        return plan

    def prioritize_tasks(self) -> list[Task]:
        # Sort by priority descending, then time-sensitive tasks first
        return sorted(
            self.tasks,
            key=lambda t: (-(t.priority), t.preferred_time is None)
        )

    async def explain_plan(self, plan: DailyPlan) -> str:
        pass
