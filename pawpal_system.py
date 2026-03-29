class Task:
    def __init__(self, task_name, duration, priority, frequency="daily", deadline=None):
        self.task_name = task_name
        self.duration = duration      # minutes
        self.priority = priority      # higher number = more important
        self.frequency = frequency    # e.g. "daily", "weekly"
        self.deadline = deadline
        self.completed = False

    def check_off(self):
        """Mark this task as completed."""
        self.completed = True

    def edit(self, task_name=None, duration=None, priority=None, frequency=None, deadline=None):
        """Update any combination of task fields; unchanged fields keep their current values."""
        if task_name is not None:
            self.task_name = task_name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency
        if deadline is not None:
            self.deadline = deadline

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task({self.task_name!r}, {self.duration}min, priority={self.priority}, {status})"


class Pet:
    def __init__(self, name, dob, animal):
        self.name = name
        self.dob = dob
        self.animal = animal
        self.tasks = []

    def add_task(self, task):
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def edit_info(self, name=None, dob=None, animal=None):
        """Update any combination of pet info fields; unchanged fields keep their current values."""
        if name is not None:
            self.name = name
        if dob is not None:
            self.dob = dob
        if animal is not None:
            self.animal = animal

    def get_pending_tasks(self):
        """Return all tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def __repr__(self):
        return f"Pet({self.name!r}, {self.animal})"


class Owner:
    def __init__(self, name, time_available=120):
        self.name = name
        self.pets = []
        self.time_available = time_available  # minutes available per day
        self._logged_in = False

    def login(self):
        """Mark the owner as logged in."""
        self._logged_in = True

    def logout(self):
        """Mark the owner as logged out."""
        self._logged_in = False

    def access_pets(self):
        """Return the list of the owner's pets."""
        return self.pets

    def add_pet(self, pet):
        """Add a Pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet):
        """Remove a Pet from the owner's pet list."""
        self.pets.remove(pet)

    def get_all_tasks(self):
        """Return every task across all of the owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def __repr__(self):
        return f"Owner({self.name!r}, {len(self.pets)} pets)"


class Scheduler:
    def __init__(self, owner):
        self.owner = owner
        self.daily_plan = []

    def add_task(self, pet, task):
        """Add a Task to the given pet's task list."""
        pet.add_task(task)

    def remove_task(self, pet, task):
        """Remove a Task from the given pet's task list."""
        pet.tasks.remove(task)

    def generate_plan(self):
        """Build today's schedule by sorting pending tasks by priority and fitting them within available time."""
        # Collect all pending tasks across all pets
        pending = []
        for pet in self.owner.pets:
            for task in pet.get_pending_tasks():
                pending.append((pet, task))

        # Sort by priority, highest first
        pending.sort(key=lambda x: x[1].priority, reverse=True)

        # Fit tasks within the owner's available time
        plan = []
        time_used = 0
        for pet, task in pending:
            if time_used + task.duration <= self.owner.time_available:
                plan.append((pet, task))
                time_used += task.duration

        self.daily_plan = plan
        return plan

    def __repr__(self):
        return f"Scheduler(owner={self.owner.name!r}, {len(self.daily_plan)} tasks planned)"
