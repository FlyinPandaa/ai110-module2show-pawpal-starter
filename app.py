import streamlit as st
from datetime import date, time
from pawpal_system import Frequency, PetProfile, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input("Available minutes per day", min_value=10, max_value=480, value=120)
special_needs_input = st.text_input("Special needs (comma-separated)", placeholder="e.g. diabetic, senior")

PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "profile" not in st.session_state:
    st.session_state.profile = None

col1, col2, col3 = st.columns(3)
with col1:
    task_name = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    category = st.selectbox("Category", ["exercise", "feeding", "medical", "grooming", "enrichment"])
with col5:
    frequency = st.selectbox("Frequency", ["daily", "twice-daily", "weekly"])

use_preferred_time = st.checkbox("Set a preferred time for this task")
preferred_time_input = st.time_input("Preferred time", value=time(8, 0)) if use_preferred_time else None

if st.button("Add task"):
    st.session_state.tasks.append({
        "name": task_name,
        "duration_minutes": int(duration),
        "priority": PRIORITY_MAP[priority],
        "category": category,
        "frequency": frequency,
        "preferred_time": preferred_time_input,
    })

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        if st.session_state.profile is None:
            special_needs = [s.strip() for s in special_needs_input.split(",") if s.strip()]
            st.session_state.profile = PetProfile(
                owner_name=owner_name,
                pet_name=pet_name,
                species=species,
                available_minutes_per_day=int(available_minutes),
                special_needs=special_needs,
            )
            for t in st.session_state.tasks:
                st.session_state.profile.add_task(Task(
                    name=t["name"],
                    category=t["category"],
                    duration_minutes=t["duration_minutes"],
                    priority=t["priority"],
                    frequency=Frequency(t["frequency"]),
                    preferred_time=t.get("preferred_time"),
                ))

        scheduler = Scheduler(st.session_state.profile)
        plan = scheduler.generate_plan(date.today())
        st.success("Schedule generated!")
        st.text(plan.get_summary())
