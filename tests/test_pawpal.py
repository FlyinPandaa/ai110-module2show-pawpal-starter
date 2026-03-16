from datetime import date, time
from pawpal_system import Frequency, PetProfile, Task, Scheduler


def make_task() -> Task:
    return Task(
        name="Morning Walk",
        category="exercise",
        duration_minutes=30,
        priority=3,
        frequency=Frequency.DAILY,
    )


def make_profile() -> PetProfile:
    return PetProfile(
        owner_name="Sarah",
        pet_name="Biscuit",
        species="Dog",
        available_minutes_per_day=120,
    )


def test_mark_complete_increments_completions():
    task = make_task()
    assert task.completions_today == 0
    task.mark_complete()
    assert task.completions_today == 1


def test_mark_complete_makes_task_no_longer_due():
    task = make_task()
    assert task.is_due() is True
    task.mark_complete()
    assert task.is_due() is False


def test_add_task_increases_task_count():
    profile = make_profile()
    assert len(profile.get_all_tasks()) == 0
    profile.add_task(make_task())
    assert len(profile.get_all_tasks()) == 1
    profile.add_task(make_task())
    assert len(profile.get_all_tasks()) == 2


# ── Scheduling Logic ──────────────────────────────────────────────────────────

def test_all_tasks_over_budget_are_skipped():
    """Every task exceeds available_minutes_per_day → all land in skipped_tasks."""
    profile = PetProfile(
        owner_name="Sarah", pet_name="Biscuit", species="Dog",
        available_minutes_per_day=10,
    )
    profile.add_task(Task(name="Long Walk", category="exercise", duration_minutes=60, priority=3, frequency=Frequency.DAILY))
    profile.add_task(Task(name="Bath", category="grooming", duration_minutes=40, priority=2, frequency=Frequency.DAILY))
    plan = Scheduler(profile).generate_plan(date.today())
    assert len(plan.scheduled_items) == 0
    assert len(plan.skipped_tasks) == 2
    assert all(reason == "over budget" for _, reason in plan.skipped_tasks)


def test_conflicting_preferred_times_skips_second():
    """Two tasks at the same preferred_time → second is skipped with 'time conflict'."""
    profile = PetProfile(
        owner_name="Sarah", pet_name="Biscuit", species="Dog",
        available_minutes_per_day=120,
    )
    profile.add_task(Task(name="Supplement", category="medical", duration_minutes=5, priority=5, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    profile.add_task(Task(name="Breakfast", category="feeding", duration_minutes=10, priority=4, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    plan = Scheduler(profile).generate_plan(date.today())
    assert len(plan.scheduled_items) == 1
    assert plan.scheduled_items[0][0].name == "Supplement"
    assert len(plan.skipped_tasks) == 1
    assert plan.skipped_tasks[0][1] == "time conflict"


def test_back_to_back_tasks_do_not_conflict():
    """Tasks that end exactly when the next begins should both be scheduled."""
    profile = PetProfile(
        owner_name="Sarah", pet_name="Biscuit", species="Dog",
        available_minutes_per_day=120,
    )
    profile.add_task(Task(name="First", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    profile.add_task(Task(name="Second", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(8, 10)))
    plan = Scheduler(profile).generate_plan(date.today())
    assert len(plan.scheduled_items) == 2
    assert len(plan.skipped_tasks) == 0


def test_empty_task_list_generates_empty_plan():
    """generate_plan() on a profile with no tasks should not crash."""
    plan = Scheduler(make_profile()).generate_plan(date.today())
    assert len(plan.scheduled_items) == 0
    assert len(plan.skipped_tasks) == 0


# ── Recurring Task Logic ──────────────────────────────────────────────────────

def test_twice_daily_first_completion_still_due_today():
    """After the first mark_complete, a TWICE_DAILY task should still be due."""
    task = Task(name="Pill", category="medical", duration_minutes=5, priority=5, frequency=Frequency.TWICE_DAILY)
    task.mark_complete()
    assert task.completions_today == 1
    assert task.is_due() is True


def test_twice_daily_second_completion_no_longer_due():
    """After both completions, a TWICE_DAILY task should not be due today."""
    task = Task(name="Pill", category="medical", duration_minutes=5, priority=5, frequency=Frequency.TWICE_DAILY)
    task.mark_complete()
    task.mark_complete()
    assert task.completions_today == 2
    assert task.is_due() is False


def test_reset_daily_does_not_affect_weekly_task():
    """reset_daily() on a WEEKLY task should leave completions_today unchanged."""
    task = Task(name="Bath", category="grooming", duration_minutes=40, priority=1, frequency=Frequency.WEEKLY)
    task.mark_complete()
    task.reset_daily()
    assert task.completions_today == 1  # unchanged


def test_task_with_future_due_date_is_not_due():
    """A task whose next_due_date is in the future should not be due today."""
    from datetime import timedelta
    task = make_task()
    task.next_due_date = date.today() + timedelta(days=3)
    assert task.is_due() is False


# ── Sorting & Prioritization ──────────────────────────────────────────────────

def test_higher_priority_task_scheduled_first():
    """prioritize_tasks() should place higher-priority tasks before lower ones."""
    profile = make_profile()
    profile.add_task(Task(name="Low", category="grooming", duration_minutes=10, priority=1, frequency=Frequency.DAILY))
    profile.add_task(Task(name="High", category="medical", duration_minutes=10, priority=5, frequency=Frequency.DAILY))
    ordered = Scheduler(profile).prioritize_tasks()
    assert ordered[0].name == "High"
    assert ordered[1].name == "Low"


def test_timed_task_sorted_before_flexible_same_priority():
    """With equal priority, a task with preferred_time should sort before one without."""
    profile = make_profile()
    profile.add_task(Task(name="Flexible", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY))
    profile.add_task(Task(name="Timed", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(9, 0)))
    ordered = Scheduler(profile).prioritize_tasks()
    assert ordered[0].name == "Timed"


def test_sorting_correctness_chronological_order():
    """Timed tasks should be returned in chronological (earliest-first) order when priority is equal."""
    profile = make_profile()
    profile.add_task(Task(name="Evening Walk", category="exercise", duration_minutes=20, priority=3, frequency=Frequency.DAILY, preferred_time=time(18, 0)))
    profile.add_task(Task(name="Afternoon Pill", category="medical", duration_minutes=5, priority=3, frequency=Frequency.DAILY, preferred_time=time(13, 0)))
    profile.add_task(Task(name="Morning Feed", category="feeding", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(7, 0)))
    ordered = Scheduler(profile).prioritize_tasks()
    times = [t.preferred_time for t in ordered]
    assert times == sorted(times)


# ── Recurrence Logic ──────────────────────────────────────────────────────────

def test_daily_task_due_next_day_after_complete():
    """Marking a DAILY task complete should set next_due_date to tomorrow."""
    from datetime import timedelta
    task = make_task()
    today = date.today()
    task.mark_complete(today)
    assert task.next_due_date == today + timedelta(days=1)
    assert task.is_due(today) is False
    assert task.is_due(today + timedelta(days=1)) is True


# ── Conflict Detection ────────────────────────────────────────────────────────

def test_detect_conflicts_flags_duplicate_times():
    """detect_conflicts() should return a warning when two tasks share the same preferred_time."""
    profile = make_profile()
    profile.add_task(Task(name="Supplement", category="medical", duration_minutes=5, priority=5, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    profile.add_task(Task(name="Breakfast", category="feeding", duration_minutes=10, priority=4, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    warnings = Scheduler(profile).detect_conflicts(date.today())
    assert len(warnings) == 1
    assert "Supplement" in warnings[0]
    assert "Breakfast" in warnings[0]


def test_detect_conflicts_no_warning_for_non_overlapping():
    """detect_conflicts() should return no warnings when tasks don't overlap."""
    profile = make_profile()
    profile.add_task(Task(name="Morning", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(8, 0)))
    profile.add_task(Task(name="Afternoon", category="exercise", duration_minutes=10, priority=3, frequency=Frequency.DAILY, preferred_time=time(14, 0)))
    warnings = Scheduler(profile).detect_conflicts(date.today())
    assert len(warnings) == 0
