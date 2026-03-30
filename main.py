from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
owner = Owner("Jordan", time_available=90)

dog = Pet("Buddy", "2020-05-01", "dog")
cat = Pet("Mochi", "2021-09-15", "cat")
owner.add_pet(dog)
owner.add_pet(cat)

# Add tasks OUT OF ORDER (times are intentionally shuffled) to prove sorting works
dog.add_task(Task("Evening walk",    duration=30, priority=3, frequency="daily",  time="18:00"))
dog.add_task(Task("Feed breakfast",  duration=10, priority=4, frequency="daily",  time="08:00"))
dog.add_task(Task("Bath time",       duration=40, priority=2, frequency="weekly", time="10:30"))
dog.add_task(Task("Morning walk",    duration=20, priority=5, frequency="daily",  time="07:30"))

cat.add_task(Task("Brush fur",       duration=15, priority=1, frequency="weekly", time="11:00"))
cat.add_task(Task("Feed breakfast",  duration=5,  priority=4, frequency="daily",  time="08:00"))  # conflicts with dog feed
cat.add_task(Task("Clean litter box",duration=10, priority=3, frequency="daily",  time="09:00"))

# ---------------------------------------------------------------------------
# Section 1 — Generate today's schedule (priority-sorted, time-budget limited)
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

print("=" * 50)
print("  TODAY'S SCHEDULE  (sorted by priority)")
print(f"  Owner: {owner.name}  |  Budget: {owner.time_available} min")
print("=" * 50)
time_used = 0
for i, (pet, task) in enumerate(plan, 1):
    print(f"{i}. [{pet.name}] {task.task_name}")
    print(f"   {task.duration} min | priority {task.priority} | {task.frequency} | @{task.time or 'no time'}")
    time_used += task.duration
print(f"{'—'*50}")
print(f"Total: {time_used} / {owner.time_available} min used")
if not plan:
    print("No tasks fit within today's available time.")

# ---------------------------------------------------------------------------
# Section 2 — Sort the plan by scheduled start time
# ---------------------------------------------------------------------------
scheduler.sort_by_time()

print()
print("=" * 50)
print("  TODAY'S SCHEDULE  (sorted by start time)")
print("=" * 50)
for i, (pet, task) in enumerate(scheduler.daily_plan, 1):
    slot = task.time if task.time else "no time"
    print(f"{i}. @{slot}  [{pet.name}] {task.task_name}  ({task.duration} min)")

# ---------------------------------------------------------------------------
# Section 3 — Conflict detection
# ---------------------------------------------------------------------------
conflicts = scheduler.detect_conflicts()

print()
print("=" * 50)
print("  CONFLICT DETECTION")
print("=" * 50)
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No scheduling conflicts found.")

# ---------------------------------------------------------------------------
# Section 4 — Filter tasks by pet / status
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("  FILTER: Buddy's pending tasks")
print("=" * 50)
buddy_pending = scheduler.filter_tasks(pet_name="Buddy", completed=False)
for pet, task in buddy_pending:
    print(f"  • {task.task_name} ({task.duration} min, priority {task.priority})")

print()
print("=" * 50)
print("  FILTER: All completed tasks (before any check-offs)")
print("=" * 50)
done = scheduler.filter_tasks(completed=True)
print(f"  {len(done)} task(s) completed so far.")

# ---------------------------------------------------------------------------
# Section 5 — Recurring task demo
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("  RECURRING TASK DEMO")
print("=" * 50)

morning_walk = dog.tasks[3]   # "Morning walk" — due today
print(f"Completing: {morning_walk.task_name}  (due {morning_walk.due_date})")
next_task = dog.complete_task(morning_walk)
if next_task:
    print(f"  → Next occurrence auto-added: {next_task.task_name}  due {next_task.due_date}")

# Daily tasks due tomorrow should NOT appear in today's plan
tomorrow_plan = scheduler.generate_plan()
tomorrow_names = [t.task_name for _, t in tomorrow_plan]
print(f"  Checking today's re-generated plan for '{morning_walk.task_name}': "
      f"{'present (unexpected)' if morning_walk.task_name in tomorrow_names else 'correctly excluded — original is done'}")
print(f"  New instance due tomorrow ({date.today() + timedelta(days=1)}) is correctly not scheduled today.")
