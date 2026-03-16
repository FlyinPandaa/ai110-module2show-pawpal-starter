from pawpal_system import Frequency, PetProfile, Task


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
