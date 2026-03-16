from datetime import date, time
from pawpal_system import Frequency, PetProfile, Task, Scheduler

# ── Profile 1: Biscuit the dog ────────────────────────────────────────────────
biscuit_profile = PetProfile(
    owner_name="Sarah",
    pet_name="Biscuit",
    species="Dog",
    available_minutes_per_day=120,
    special_needs=["senior", "joint supplements"],
)

# Added out of order: low priority grooming first, critical medical last
biscuit_profile.add_task(Task(
    name="Grooming Brush",
    category="grooming",
    duration_minutes=15,
    priority=2,
    frequency=Frequency.DAILY,
    description="Brush coat to reduce shedding",
))
biscuit_profile.add_task(Task(
    name="Morning Walk",
    category="exercise",
    duration_minutes=30,
    priority=4,
    frequency=Frequency.DAILY,
    preferred_time=time(7, 0),
    description="Slow-paced walk around the block",
))
biscuit_profile.add_task(Task(
    name="Bath",
    category="grooming",
    duration_minutes=40,
    priority=1,
    frequency=Frequency.WEEKLY,
    description="Full bath and dry",
))
biscuit_profile.add_task(Task(
    name="Joint Supplement",
    category="medical",
    duration_minutes=5,
    priority=5,
    frequency=Frequency.TWICE_DAILY,
    preferred_time=time(8, 0),
    description="Mix supplement into food",
))
# Intentional conflict: overlaps with Joint Supplement at 08:00
biscuit_profile.add_task(Task(
    name="Breakfast Feeding",
    category="feeding",
    duration_minutes=10,
    priority=4,
    frequency=Frequency.DAILY,
    preferred_time=time(8, 0),
    description="Morning kibble portion",
))

# ── Profile 2: Mochi the cat ──────────────────────────────────────────────────
mochi_profile = PetProfile(
    owner_name="James",
    pet_name="Mochi",
    species="Cat",
    available_minutes_per_day=60,
    special_needs=["indoor only", "anxiety"],
)

# Added out of order: enrichment first, critical medication last
mochi_profile.add_task(Task(
    name="Interactive Play",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=time(18, 0),
    description="Wand toy or laser pointer session",
))
mochi_profile.add_task(Task(
    name="Litter Box Clean",
    category="grooming",
    duration_minutes=10,
    priority=4,
    frequency=Frequency.DAILY,
    description="Scoop and refresh litter",
))
mochi_profile.add_task(Task(
    name="Anxiety Medication",
    category="medical",
    duration_minutes=5,
    priority=5,
    frequency=Frequency.DAILY,
    preferred_time=time(9, 0),
    description="Administer prescribed calming drops",
))

# ── Generate schedules, then test sorting and filtering ───────────────────────
today = date.today()

for profile in [biscuit_profile, mochi_profile]:
    scheduler = Scheduler(profile)

    conflicts = scheduler.detect_conflicts(today)
    if conflicts:
        print(f"\n-- Conflict warnings for {profile.pet_name} --")
        for w in conflicts:
            print(f"  {w}")

    plan = scheduler.generate_plan(today)

    print("=" * 50)
    print(f"Today's Schedule -- {profile.pet_name} ({profile.owner_name})")
    print("=" * 50)
    print(plan.get_summary())

    print(f"\n-- Sorted task order (priority + time) --")
    for task in scheduler.prioritize_tasks():
        t = str(task.preferred_time) if task.preferred_time else "flexible"
        print(f"  [{task.priority}] {task.name} @ {t}")

    print(f"\n-- Pending tasks --")
    for task in profile.get_pending_tasks(today):
        print(f"  {task.name} (due: {task.is_due(today)})")

    print(f"\n-- Completed tasks --")
    completed = profile.get_completed_tasks(today)
    print(f"  {[t.name for t in completed] or 'none yet'}")

    print(f"\n-- Medical tasks --")
    for task in profile.get_tasks_by_category("medical"):
        print(f"  {task.name} (priority {task.priority})")

    print(f"\n-- Conflict check --")
    print(f"  Plan has conflict: {plan.has_conflict()}")
    print()
