from pawpal_system import Task, Pet, Owner, Scheduler

# Create owner with 90 minutes available today
owner = Owner("Jordan", time_available=90)
owner.login()

# Create two pets
dog = Pet("Buddy", "2020-05-01", "dog")
cat = Pet("Mochi", "2021-09-15", "cat")

owner.add_pet(dog)
owner.add_pet(cat)

# Add tasks to Buddy (dog)
dog.add_task(Task("Morning walk",    duration=30, priority=5, frequency="daily"))
dog.add_task(Task("Feed breakfast",  duration=10, priority=4, frequency="daily"))
dog.add_task(Task("Bath time",       duration=40, priority=2, frequency="weekly"))

# Add tasks to Mochi (cat)
cat.add_task(Task("Feed breakfast",  duration=5,  priority=4, frequency="daily"))
cat.add_task(Task("Clean litter box",duration=10, priority=3, frequency="daily"))
cat.add_task(Task("Brush fur",       duration=15, priority=1, frequency="weekly"))

# Generate today's schedule
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

# Print schedule
print("=" * 40)
print("       TODAY'S SCHEDULE")
print(f"       Owner: {owner.name}")
print(f"       Time available: {owner.time_available} min")
print("=" * 40)

time_used = 0
for i, (pet, task) in enumerate(plan, start=1):
    print(f"{i}. [{pet.name}] {task.task_name}")
    print(f"   Duration: {task.duration} min  |  Priority: {task.priority}  |  Frequency: {task.frequency}")
    time_used += task.duration

print("-" * 40)
print(f"Total time: {time_used} min / {owner.time_available} min available")

if not plan:
    print("No tasks fit within today's available time.")
