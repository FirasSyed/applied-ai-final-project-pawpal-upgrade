from datetime import date, timedelta
import pytest
from pawpal.system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def buddy():
    return Pet("Buddy", "2020-05-01", "dog")


@pytest.fixture
def mochi():
    return Pet("Mochi", "2021-03-10", "cat")


@pytest.fixture
def owner(buddy):
    o = Owner("Alex", time_available=120)
    o.add_pet(buddy)
    return o


@pytest.fixture
def scheduler(owner):
    return Scheduler(owner)


# ===========================================================================
# 1. EXISTING TESTS (kept)
# ===========================================================================

def test_check_off_marks_task_complete():
    task = Task("Walk", duration=30, priority=3)
    assert task.completed == False
    task.check_off()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "2020-05-01", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed", duration=10, priority=4))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Walk", duration=30, priority=3))
    assert len(pet.tasks) == 2


# ===========================================================================
# 2. RECURRING TASK ROLLOVER
# ===========================================================================

class TestRecurringTasks:
    """check_off() creates the right successor (or none)."""

    def test_daily_task_rolls_over_by_one_day(self):
        today = date.today()
        task = Task("Feed", duration=10, priority=3, frequency="daily")
        task.due_date = today
        next_task = task.check_off()

        assert task.completed is True
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.task_name == "Feed"
        assert next_task.completed is False          # fresh, not pre-completed

    def test_weekly_task_rolls_over_by_seven_days(self):
        today = date.today()
        task = Task("Bath", duration=20, priority=2, frequency="weekly")
        task.due_date = today
        next_task = task.check_off()

        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_task_returns_none(self):
        task = Task("Vet visit", duration=60, priority=5, frequency="once")
        result = task.check_off()

        assert task.completed is True
        assert result is None                        # no successor

    def test_pet_complete_task_appends_next_occurrence(self, buddy):
        """Pet.complete_task should auto-append the daily successor."""
        task = Task("Feed", duration=10, priority=4, frequency="daily")
        buddy.add_task(task)
        buddy.complete_task(task)

        # original task + one new daily occurrence
        assert len(buddy.tasks) == 2
        assert buddy.tasks[0].completed is True
        assert buddy.tasks[1].completed is False

    def test_once_task_does_not_append_next_occurrence(self, buddy):
        task = Task("Grooming", duration=30, priority=2, frequency="once")
        buddy.add_task(task)
        buddy.complete_task(task)

        assert len(buddy.tasks) == 1                # no extra task added


# ===========================================================================
# 3. generate_plan — PRIORITY ORDER & TIME BUDGET
# ===========================================================================

class TestGeneratePlan:
    """Scheduler.generate_plan() respects priority and time budget."""

    def test_happy_path_highest_priority_task_is_first(self, buddy, scheduler):
        low  = Task("Play",  duration=20, priority=1)
        high = Task("Meds",  duration=10, priority=5)
        buddy.add_task(low)
        buddy.add_task(high)

        plan = scheduler.generate_plan()

        assert plan[0][1] is high                   # highest priority leads
        assert plan[1][1] is low

    def test_tasks_fitting_within_budget_are_included(self, buddy, scheduler):
        buddy.add_task(Task("Feed",  duration=10, priority=3))
        buddy.add_task(Task("Walk",  duration=30, priority=2))
        plan = scheduler.generate_plan()

        assert len(plan) == 2                        # both fit in 120 min

    def test_task_exceeding_time_budget_is_excluded(self, buddy):
        tight_owner = Owner("Sam", time_available=15)
        tight_owner.add_pet(buddy)
        scheduler = Scheduler(tight_owner)

        buddy.add_task(Task("Long walk", duration=60, priority=1))
        buddy.add_task(Task("Feed",      duration=10, priority=2))

        plan = scheduler.generate_plan()

        assert len(plan) == 1
        assert plan[0][1].task_name == "Feed"        # higher-priority but fits

    def test_zero_time_available_yields_empty_plan(self, buddy):
        empty_owner = Owner("Sam", time_available=0)
        empty_owner.add_pet(buddy)
        s = Scheduler(empty_owner)
        buddy.add_task(Task("Feed", duration=10, priority=3))

        assert s.generate_plan() == []

    def test_future_dated_task_excluded_from_plan(self, buddy, scheduler):
        tomorrow = date.today() + timedelta(days=1)
        buddy.add_task(Task("Vet", duration=30, priority=5, due_date=tomorrow))
        plan = scheduler.generate_plan()

        assert plan == []

    def test_completed_tasks_excluded_from_plan(self, buddy, scheduler):
        task = Task("Feed", duration=10, priority=3)
        task.completed = True
        buddy.add_task(task)

        assert scheduler.generate_plan() == []

    # Edge case: pet with no tasks at all
    def test_pet_with_no_tasks_yields_empty_plan(self, scheduler):
        assert scheduler.generate_plan() == []


# ===========================================================================
# 4. sort_by_time
# ===========================================================================

class TestSortByTime:
    """Scheduler.sort_by_time() orders chronologically; untimed tasks last."""

    def _load_plan(self, scheduler, buddy, tasks):
        for t in tasks:
            buddy.add_task(t)
        scheduler.generate_plan()

    def test_happy_path_chronological_order(self, buddy, scheduler):
        t1 = Task("Breakfast", duration=10, priority=3, time="08:00")
        t2 = Task("Lunch",     duration=10, priority=3, time="12:00")
        t3 = Task("Dinner",    duration=10, priority=3, time="18:00")
        self._load_plan(scheduler, buddy, [t3, t1, t2])   # shuffled

        result = scheduler.sort_by_time()

        times = [pair[1].time for pair in result]
        assert times == ["08:00", "12:00", "18:00"]

    def test_untimed_tasks_placed_at_end(self, buddy, scheduler):
        timed   = Task("Meds",  duration=10, priority=3, time="09:00")
        untimed = Task("Play",  duration=20, priority=3, time=None)
        self._load_plan(scheduler, buddy, [untimed, timed])

        result = scheduler.sort_by_time()

        assert result[0][1].time == "09:00"
        assert result[1][1].time is None

    def test_two_tasks_same_time_both_appear(self, buddy, mochi, scheduler):
        """Same-time tasks should both remain in the sorted list."""
        scheduler.owner.add_pet(mochi)
        t1 = Task("Feed", duration=10, priority=3, time="08:00")
        t2 = Task("Feed", duration=10, priority=3, time="08:00")
        buddy.add_task(t1)
        mochi.add_task(t2)
        scheduler.generate_plan()

        result = scheduler.sort_by_time()
        times = [pair[1].time for pair in result]

        assert len(result) == 2
        assert times == ["08:00", "08:00"]


# ===========================================================================
# 5. detect_conflicts
# ===========================================================================

class TestDetectConflicts:
    """Scheduler.detect_conflicts() flags same-slot tasks, ignores no-time tasks."""

    def test_happy_path_no_conflicts(self, buddy, scheduler):
        buddy.add_task(Task("Feed", duration=10, priority=3, time="08:00"))
        buddy.add_task(Task("Walk", duration=30, priority=2, time="09:00"))
        scheduler.generate_plan()

        assert scheduler.detect_conflicts() == []

    def test_two_tasks_at_same_time_raises_warning(self, buddy, mochi, scheduler):
        scheduler.owner.add_pet(mochi)
        buddy.add_task(Task("Feed", duration=10, priority=3, time="08:00"))
        mochi.add_task(Task("Feed", duration=10, priority=3, time="08:00"))
        scheduler.generate_plan()

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "08:00" in warnings[0]
        assert "Buddy" in warnings[0]
        assert "Mochi" in warnings[0]

    def test_tasks_without_time_do_not_trigger_conflict(self, buddy, mochi, scheduler):
        scheduler.owner.add_pet(mochi)
        buddy.add_task(Task("Play", duration=20, priority=2, time=None))
        mochi.add_task(Task("Play", duration=20, priority=2, time=None))
        scheduler.generate_plan()

        assert scheduler.detect_conflicts() == []

    def test_single_task_at_a_slot_is_not_a_conflict(self, buddy, scheduler):
        buddy.add_task(Task("Feed", duration=10, priority=3, time="08:00"))
        scheduler.generate_plan()

        assert scheduler.detect_conflicts() == []

    def test_three_tasks_same_slot_single_warning(self, buddy, mochi, scheduler):
        """Three-way collision should still produce exactly one warning line."""
        rex = Pet("Rex", "2019-01-01", "dog")
        scheduler.owner.add_pet(mochi)
        scheduler.owner.add_pet(rex)

        for pet in (buddy, mochi, rex):
            pet.add_task(Task("Feed", duration=10, priority=3, time="07:00"))

        scheduler.generate_plan()
        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "07:00" in warnings[0]


# ===========================================================================
# 6. filter_tasks
# ===========================================================================

class TestFilterTasks:
    """Scheduler.filter_tasks() narrows by pet name and/or completion status."""

    def test_filter_by_pet_name(self, buddy, mochi, scheduler):
        scheduler.owner.add_pet(mochi)
        buddy.add_task(Task("Feed", duration=10, priority=3))
        mochi.add_task(Task("Feed", duration=10, priority=3))

        results = scheduler.filter_tasks(pet_name="Buddy")

        assert all(pet.name == "Buddy" for pet, _ in results)
        assert len(results) == 1

    def test_filter_completed_tasks(self, buddy, scheduler):
        t1 = Task("Feed", duration=10, priority=3)
        t2 = Task("Walk", duration=30, priority=2)
        t1.check_off()
        buddy.add_task(t1)
        buddy.add_task(t2)

        results = scheduler.filter_tasks(completed=True)

        assert len(results) == 1
        assert results[0][1].task_name == "Feed"

    def test_filter_pending_tasks(self, buddy, scheduler):
        t1 = Task("Feed", duration=10, priority=3)
        t2 = Task("Walk", duration=30, priority=2)
        t1.check_off()
        buddy.add_task(t1)
        buddy.add_task(t2)

        results = scheduler.filter_tasks(completed=False)

        assert len(results) == 1
        assert results[0][1].task_name == "Walk"

    def test_no_filter_returns_all_tasks(self, buddy, mochi, scheduler):
        scheduler.owner.add_pet(mochi)
        buddy.add_task(Task("Feed", duration=10, priority=3))
        mochi.add_task(Task("Feed", duration=10, priority=3))

        assert len(scheduler.filter_tasks()) == 2

    def test_filter_on_pet_with_no_tasks_returns_empty(self, buddy, scheduler):
        # Buddy has no tasks at all
        results = scheduler.filter_tasks(pet_name="Buddy")
        assert results == []
