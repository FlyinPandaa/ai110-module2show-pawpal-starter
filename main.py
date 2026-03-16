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
    name="Joint Supplement",
    category="medical",
    duration_minutes=5,
    priority=5,
    frequency=Frequency.TWICE_DAILY,
    preferred_time=time(8, 0),
    description="Mix supplement into food",
))
biscuit_profile.add_task(Task(
    name="Grooming Brush",
    category="grooming",
    duration_minutes=15,
    priority=2,
    frequency=Frequency.DAILY,
    description="Brush coat to reduce shedding",
))

# ── Profile 2: Mochi the cat ──────────────────────────────────────────────────
mochi_profile = PetProfile(
    owner_name="James",
    pet_name="Mochi",
    species="Cat",
    available_minutes_per_day=60,
    special_needs=["indoor only", "anxiety"],
)

mochi_profile.add_task(Task(
    name="Anxiety Medication",
    category="medical",
    duration_minutes=5,
    priority=5,
    frequency=Frequency.DAILY,
    preferred_time=time(9, 0),
    description="Administer prescribed calming drops",
))
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

# ── Generate and print schedules ──────────────────────────────────────────────
today = date.today()

for profile in [biscuit_profile, mochi_profile]:
    scheduler = Scheduler(profile)
    plan = scheduler.generate_plan(today)
    print("=" * 50)
    print(f"Today's Schedule — {profile.pet_name} ({profile.owner_name})")
    print("=" * 50)
    print(plan.get_summary())
    print()
