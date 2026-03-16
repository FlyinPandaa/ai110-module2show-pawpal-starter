# PawPal+ Project Reflection

## 1. System Design

- Three core actions:
    - Enter owner and Pet info
    - Add/edit care tasks
    - Generate a daily schedule while taking into account priorities for the day

**a. Initial design**

The initial design had four classes: `PetProfile`, `Task`, `DailyPlan`, and `Scheduler`.

- `PetProfile` — merged owner and pet data into one class (name, species, time budget, special needs).
- `Task` — a single care activity with a name, category, duration, priority, and optional preferred time.
- `DailyPlan` — the schedule output; holds scheduled `(Task, time)` pairs, skipped tasks, and a `reasoning` string populated by the Claude API explaining why tasks were prioritized or skipped.
- `Scheduler` — the coordinator; prioritizes tasks, fits them into the time budget, and produces a `DailyPlan`.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Yes, at first I wanted to include both the Owner profile and the pet profile. I asked Claude for some help on simplifying my classes, and Claude proposed to just have `PetProfile` instead of 2 separate classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

- Some major considerations would be how much time the owner has, how urgent the tasks are, and when the tasks need to happen (for things like medication). Time and prioority matter moset because a pet owner with limited amount of time can't complete all tasks, so the scheduler needs to pick the most important tasks first and drop the rest or  save it for another time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- The scheduler always picks high-prioority tasks first, even if a lower-prioirty task  fits better in the remaining time. For example, if 10 minutes are remaining and a priority-5 task takes 15 minutes, it gets skipped, because a priority-2 task that takes 5 minutes could fit better into the schedule. This is reasonable because skipping a medication time versus skipping a grooming time are vastly different in priority. Feeding the medication to the pet is critical  compared to the grooming time.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used AI tools for brainstorming classes, debugging, refactoring code, and reviewing its own implementation. A useful prompt, was after generating the implementation, for `pawpal_system.py` I asked Claude Code the following, "You are a senior software engineer. Review the code you written and identify any bottlenecks or issues that might arise. Fix those issues and report back your findings and solutions."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- One time where I didn't accept an AI suggestion as-is is while generating the classes for the application. Claude Code generated 8 classes, and I realized that it was too many classes for the Pawpal app for now. So I asked it to reduce the number of classes to keep the application as simple as possible for now. I read through what was suggested by the AI and then I think about whether it was something I wanted or not. If I didn't want those changes or don't like the suggestion, I provide Claude what I didn't like and ask it to think again until I am satisfied.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- Verified that calling `mark_complete()` increments completions_today and makes `is_due()` return `False`. This matters because the scheduler skips completed tasks. If this logic broke, the same task could be scheduled twice in one day which is not what we want.

- Verified that `add_task()` grows the profile's task list. This is an important operation in the app, because if the `add_tak()` doesn't work, then  nothing else works.

- These tests are important  because they cover the two behaviors the entire scheduler depends on know what tasks  exist and knowing which ones to run.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

- I think the scheduler will work fine for the most part. Some examples would be priority ordering, time conflict detection, budget enforcement, and recurring  task tracking. The main gap is that our current tests only cover `Task` and `PetProfile`. The `Scheduler` doesn't have any automated tests, and it might be best to implement tests for `Scheduluer` if we had more time.

- For some possible edge cases, I asked Claude Code, and some edge cases that were suggested was the following:
    - What happens if all taks exceed the budget? Does the plan return an empty schedule without crashing?
    - Does a `TWICE_DAILY` task reset correctly at midnight and allow two runs the next day?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- The pawpal_system.py is probably the best part of the project, because we spent a decent amount of time on this portion of the application. It features the core functionality of the project. It also has the most lines of code haha. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- I would redesign the UI, it's a simple UI that allows testing the core functionality easy, but if I had another chance to work on this application, I would work  on the UI and make it look more robust. For example, once we generate the schedule, I would like to see a calendar or something like Google calender with the times and dates listed on the side and top.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

- One important thing I learned was to keep the Claude in check when it comes to implementing changes or brainstorming. For the most part the application is suppose to be simple, but one I asked Claude with ideas on what classes I need, I was recommended 8 different classes, which was alot for the lightweight application we were  going to build.
