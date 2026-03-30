from datetime import date, timedelta


class Task:
    def __init__(self, task_name, duration, priority, frequency="daily",
                 deadline=None, time=None, due_date=None):
        """
        Create a pet care task.

        Args:
            task_name: Human-readable name for the task.
            duration:  How long the task takes, in minutes.
            priority:  Importance ranking; higher number = more important.
            frequency: How often the task recurs — "daily", "weekly", or "once".
            deadline:  Optional hard deadline (date object).
            time:      Optional scheduled start time as "HH:MM" string.
            due_date:  The date this task instance is due; defaults to today.
        """
        self.task_name = task_name
        self.duration = duration
        self.priority = priority
        self.frequency = frequency
        self.deadline = deadline
        self.time = time                                      # "HH:MM" or None
        self.due_date = due_date if due_date is not None else date.today()
        self.completed = False

    def check_off(self):
        """
        Mark this task as completed.

        For recurring tasks, returns a new Task instance due on the next
        occurrence (today + 1 day for daily, + 7 days for weekly).
        Returns None for one-off tasks.
        """
        self.completed = True
        if self.frequency == "daily":
            return Task(self.task_name, self.duration, self.priority,
                        self.frequency, self.deadline, self.time,
                        due_date=self.due_date + timedelta(days=1))
        if self.frequency == "weekly":
            return Task(self.task_name, self.duration, self.priority,
                        self.frequency, self.deadline, self.time,
                        due_date=self.due_date + timedelta(weeks=1))
        return None  # "once" tasks produce no successor

    def edit(self, task_name=None, duration=None, priority=None,
             frequency=None, deadline=None, time=None):
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
        if time is not None:
            self.time = time

    def __repr__(self):
        status = "done" if self.completed else "pending"
        t = f" @{self.time}" if self.time else ""
        return f"Task({self.task_name!r}, {self.duration}min, priority={self.priority}{t}, {status})"


class Pet:
    def __init__(self, name, dob, animal):
        """
        Create a pet.

        Args:
            name:   The pet's name.
            dob:    Date of birth as a string (YYYY-MM-DD).
            animal: Species label, e.g. "dog", "cat".
        """
        self.name = name
        self.dob = dob
        self.animal = animal
        self.tasks = []

    def add_task(self, task):
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task):
        """
        Mark a task done and, if it recurs, append the next occurrence to
        this pet's task list automatically.

        Returns the new Task if one was created, otherwise None.
        """
        next_task = task.check_off()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task

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
        """
        Create an owner profile.

        Args:
            name:           The owner's display name.
            time_available: Minutes available for pet care today.
        """
        self.name = name
        self.pets = []
        self.time_available = time_available
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
        """
        Create a scheduler for the given owner.

        Args:
            owner: The Owner whose pets and tasks will be scheduled.
        """
        self.owner = owner
        self.daily_plan = []

    # ------------------------------------------------------------------
    # Task management helpers
    # ------------------------------------------------------------------

    def add_task(self, pet, task):
        """Add a Task to the given pet's task list."""
        pet.add_task(task)

    def remove_task(self, pet, task):
        """Remove a Task from the given pet's task list."""
        pet.tasks.remove(task)

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def generate_plan(self):
        """
        Build today's schedule.

        Only tasks whose due_date is today or earlier are eligible.
        Eligible tasks are sorted by priority (highest first) and greedily
        fitted within the owner's available time budget.

        Returns:
            List of (Pet, Task) tuples representing the day's plan.
        """
        today = date.today()
        pending = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_pending_tasks()
            if task.due_date <= today
        ]
        pending.sort(key=lambda x: x[1].priority, reverse=True)

        plan = []
        time_used = 0
        for pet, task in pending:
            if time_used + task.duration <= self.owner.time_available:
                plan.append((pet, task))
                time_used += task.duration

        self.daily_plan = plan
        return plan

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self):
        """
        Sort the current daily_plan by each task's scheduled start time.

        Tasks with a time set are sorted chronologically using their "HH:MM"
        string. Tasks with no time are placed at the end of the list.

        Returns:
            The sorted daily_plan list (also mutates self.daily_plan in place).
        """
        self.daily_plan.sort(
            key=lambda x: x[1].time if x[1].time is not None else "99:99"
        )
        return self.daily_plan

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_tasks(self, pet_name=None, completed=None):
        """
        Filter all tasks across the owner's pets.

        Args:
            pet_name:  If given, only return tasks belonging to this pet.
            completed: If True, return only completed tasks.
                       If False, return only pending tasks.
                       If None (default), return all tasks regardless of status.

        Returns:
            List of (Pet, Task) tuples matching the filter criteria.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append((pet, task))
        return results

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self):
        """
        Identify tasks in the daily plan that share the same start time.

        Two or more tasks scheduled at the same "HH:MM" slot are considered
        a conflict. Tasks without a time are ignored.

        Returns:
            List of warning strings, one per conflicting time slot.
            An empty list means no conflicts were detected.
        """
        time_map = {}
        for pet, task in self.daily_plan:
            if task.time is None:
                continue
            time_map.setdefault(task.time, []).append((pet, task))

        warnings = []
        for slot, entries in time_map.items():
            if len(entries) > 1:
                names = ", ".join(f"[{p.name}] {t.task_name}" for p, t in entries)
                warnings.append(f"WARNING — conflict at {slot}: {names}")
        return warnings

    def __repr__(self):
        return f"Scheduler(owner={self.owner.name!r}, {len(self.daily_plan)} tasks planned)"
