# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Testing

To test run the following command: `python -m pytest`.

Below is a table of what tests are covered in the test_pawpal.py along with category and description of the test. Based on the test results: 5-stars for the system's realiability.

| Test | Category | Description |
|---|---|---|
| `test_mark_complete_increments_completions` | Task Completion | Calling `mark_complete()` increases `completions_today` by 1 |
| `test_mark_complete_makes_task_no_longer_due` | Task Completion | A DAILY task is no longer due after being marked complete |
| `test_add_task_increases_task_count` | Task Addition | Adding tasks to a profile correctly grows the task list |
| `test_all_tasks_over_budget_are_skipped` | Scheduling | All tasks exceeding the time budget are skipped with reason "over budget" |
| `test_conflicting_preferred_times_skips_second` | Scheduling | When two tasks share a preferred time, the lower-priority one is skipped with "time conflict" |
| `test_back_to_back_tasks_do_not_conflict` | Scheduling | Tasks ending exactly when the next begins are both scheduled without conflict |
| `test_empty_task_list_generates_empty_plan` | Scheduling | Generating a plan with no tasks does not crash and returns an empty plan |
| `test_twice_daily_first_completion_still_due_today` | Recurrence | A TWICE_DAILY task is still due after only the first completion |
| `test_twice_daily_second_completion_no_longer_due` | Recurrence | A TWICE_DAILY task is no longer due after both completions |
| `test_reset_daily_does_not_affect_weekly_task` | Recurrence | Calling `reset_daily()` on a WEEKLY task leaves `completions_today` unchanged |
| `test_task_with_future_due_date_is_not_due` | Recurrence | A task with a future `next_due_date` correctly reports as not due today |
| `test_higher_priority_task_scheduled_first` | Sorting | Higher-priority tasks appear before lower-priority tasks in the sorted order |
| `test_timed_task_sorted_before_flexible_same_priority` | Sorting | Tasks with a `preferred_time` sort before flexible tasks of equal priority |
| `test_sorting_correctness_chronological_order` | Sorting | Timed tasks of equal priority are returned in earliest-to-latest chronological order |
| `test_daily_task_due_next_day_after_complete` | Recurrence | Completing a DAILY task sets `next_due_date` to tomorrow and makes it due then |
| `test_detect_conflicts_flags_duplicate_times` | Conflict Detection | `detect_conflicts()` returns a warning when two tasks share the same preferred time |
| `test_detect_conflicts_no_warning_for_non_overlapping` | Conflict Detection | `detect_conflicts()` returns no warnings when tasks are well separated in time |

