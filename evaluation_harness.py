"""
Evaluation Harness for PawPal AI

This script runs predefined test cases on the PawPal AI system and reports:
- Pass/fail status for scheduling accuracy
- Confidence scores for AI explanations
- Logging of key interactions
- Overall reliability metrics
"""

import os
import sys
from datetime import date, timedelta
import json

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pawpal.system import Task, Pet, Owner, Scheduler


class EvaluationTest:
    """A single test case for the PawPal system."""

    def __init__(self, test_id, description, setup_fn, assertions_fn):
        self.test_id = test_id
        self.description = description
        self.setup_fn = setup_fn
        self.assertions_fn = assertions_fn
        self.passed = False
        self.error = None
        self.confidence = 0.0

    def run(self):
        """Run the test and capture results."""
        try:
            data = self.setup_fn()
            success, confidence = self.assertions_fn(data)
            self.passed = success
            self.confidence = confidence
            return True
        except Exception as e:
            self.error = str(e)
            self.passed = False
            self.confidence = 0.0
            return False


def test_priority_based_scheduling():
    """Test that high-priority tasks are scheduled first."""
    def setup():
        owner = Owner("TestOwner", time_available=60)
        pet = Pet("TestPet", "2020-01-01", "dog")
        owner.add_pet(pet)

        # Add tasks with varying priorities
        pet.add_task(Task("Low priority", duration=20, priority=1))
        pet.add_task(Task("High priority", duration=30, priority=5))

        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        return {"plan": plan, "pet": pet}

    def assertions(data):
        plan = data["plan"]
        if len(plan) != 2:
            return False, 0.0
        # High priority (5) should come before low priority (1)
        first_priority = plan[0][1].priority
        second_priority = plan[1][1].priority
        success = first_priority > second_priority
        confidence = 0.95 if success else 0.0
        return success, confidence

    return EvaluationTest("priority_scheduling", "High-priority tasks scheduled first", setup, assertions)


def test_time_budget_constraint():
    """Test that tasks respecting time budget are scheduled, others excluded."""
    def setup():
        owner = Owner("TestOwner", time_available=40)
        pet = Pet("TestPet", "2020-01-01", "dog")
        owner.add_pet(pet)

        pet.add_task(Task("Task A", duration=20, priority=3))
        pet.add_task(Task("Task B", duration=20, priority=3))
        pet.add_task(Task("Task C", duration=20, priority=2))

        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        return {"plan": plan, "budget": owner.time_available}

    def assertions(data):
        plan = data["plan"]
        budget = data["budget"]
        total_time = sum(task.duration for _, task in plan)
        # Should fit within budget
        success = total_time <= budget and len(plan) >= 2
        confidence = 0.9 if success else 0.0
        return success, confidence

    return EvaluationTest("time_budget", "Tasks scheduled within time budget", setup, assertions)


def test_recurring_task_rollover():
    """Test that completing a recurring task creates the next occurrence."""
    def setup():
        pet = Pet("TestPet", "2020-01-01", "dog")
        task = Task("Daily walk", duration=20, priority=3, frequency="daily")
        pet.add_task(task)

        original_date = task.due_date
        pet.complete_task(task)

        return {"pet": pet, "original_date": original_date}

    def assertions(data):
        pet = data["pet"]
        original_date = data["original_date"]

        # Should have two tasks now: original (completed) and new (pending)
        if len(pet.tasks) != 2:
            return False, 0.0

        new_task = pet.tasks[1]
        expected_date = original_date + timedelta(days=1)
        success = new_task.due_date == expected_date and not new_task.completed
        confidence = 0.95 if success else 0.0
        return success, confidence

    return EvaluationTest("recurring_rollover", "Recurring tasks roll over correctly", setup, assertions)


def test_conflict_detection():
    """Test that tasks with the same start time are flagged as conflicts."""
    def setup():
        owner = Owner("TestOwner", time_available=120)
        pet1 = Pet("Pet1", "2020-01-01", "dog")
        pet2 = Pet("Pet2", "2020-01-02", "cat")

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        # Both tasks at same time
        pet1.add_task(Task("Feed", duration=10, priority=3, time="08:00"))
        pet2.add_task(Task("Feed", duration=10, priority=3, time="08:00"))

        scheduler = Scheduler(owner)
        scheduler.generate_plan()
        conflicts = scheduler.detect_conflicts()

        return {"conflicts": conflicts, "conflict_count": len(conflicts)}

    def assertions(data):
        conflicts = data["conflicts"]
        # Should detect at least one conflict
        success = len(conflicts) > 0
        confidence = 0.9 if success else 0.0
        return success, confidence

    return EvaluationTest("conflict_detection", "Scheduling conflicts detected", setup, assertions)


def test_task_filtering():
    """Test that task filtering by pet and status works correctly."""
    def setup():
        owner = Owner("TestOwner", time_available=120)
        pet1 = Pet("Pet1", "2020-01-01", "dog")
        pet2 = Pet("Pet2", "2020-01-02", "cat")

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        task1 = Task("Task1", duration=10, priority=3)
        task2 = Task("Task2", duration=10, priority=3)
        task3 = Task("Task3", duration=10, priority=3)

        pet1.add_task(task1)
        pet1.add_task(task2)
        pet2.add_task(task3)

        # Complete one task
        pet1.complete_task(task1)

        scheduler = Scheduler(owner)
        pending = scheduler.filter_tasks(completed=False)
        pet1_tasks = scheduler.filter_tasks(pet_name="Pet1")

        return {"pending": pending, "pet1_tasks": pet1_tasks, "total_tasks": 3}

    def assertions(data):
        pending = data["pending"]
        pet1_tasks = data["pet1_tasks"]
        # 2 pending (task2, task3)
        pending_ok = len(pending) == 2
        # 2 for Pet1 (task1 completed, task2 pending)
        pet_filter_ok = len(pet1_tasks) == 2
        success = pending_ok and pet_filter_ok
        confidence = 0.9 if success else 0.0
        return success, confidence

    return EvaluationTest("task_filtering", "Task filtering by pet and status", setup, assertions)


def test_slot_assignment():
    """Test that unscheduled tasks get assigned time slots."""
    def setup():
        owner = Owner("TestOwner", time_available=120)
        pet = Pet("TestPet", "2020-01-01", "dog")
        owner.add_pet(pet)

        # Tasks with no time slot
        pet.add_task(Task("Task1", duration=20, priority=3))
        pet.add_task(Task("Task2", duration=30, priority=2))

        scheduler = Scheduler(owner)
        scheduler.generate_plan()
        scheduler.assign_slots("08:00")

        return {"daily_plan": scheduler.daily_plan}

    def assertions(data):
        plan = data["daily_plan"]
        # All tasks should have time assigned
        all_have_time = all(task.time is not None for _, task in plan)
        # Times should be in order
        times = [task.time for _, task in plan]
        times_increasing = times == sorted(times)
        success = all_have_time and times_increasing
        confidence = 0.9 if success else 0.0
        return success, confidence

    return EvaluationTest("slot_assignment", "Unscheduled tasks assigned time slots", setup, assertions)


def run_all_tests():
    """Run all evaluation tests and produce a report."""
    tests = [
        test_priority_based_scheduling(),
        test_time_budget_constraint(),
        test_recurring_task_rollover(),
        test_conflict_detection(),
        test_task_filtering(),
        test_slot_assignment(),
    ]

    print("\n" + "=" * 70)
    print("  PAWPAL AI EVALUATION HARNESS")
    print("=" * 70)
    print()

    results = []
    passed_count = 0

    for test in tests:
        print(f"Running: {test.test_id}")
        print(f"  {test.description}...", end=" ")
        test.run()

        if test.passed:
            print(f"✅ PASS (confidence: {test.confidence:.2f})")
            passed_count += 1
        else:
            if test.error:
                print(f"❌ FAIL - {test.error}")
            else:
                print(f"❌ FAIL (confidence: {test.confidence:.2f})")

        results.append(
            {
                "test_id": test.test_id,
                "description": test.description,
                "passed": test.passed,
                "confidence": test.confidence,
                "error": test.error,
            }
        )

    # Summary
    print()
    print("=" * 70)
    print(f"  RESULTS: {passed_count}/{len(tests)} tests passed")
    print("=" * 70)

    total_confidence = sum(r["confidence"] for r in results) / len(results)
    print(f"Average Confidence Score: {total_confidence:.2f} / 1.00")
    print()

    # Detailed summary
    print("Test Summary:")
    for r in results:
        status = "✅" if r["passed"] else "❌"
        print(
            f"  {status} {r['test_id']}: {r['description']} "
            f"(confidence: {r['confidence']:.2f})"
        )

    print()
    print("Key Findings:")
    print(f"  - {passed_count} out of {len(tests)} tests passed")
    print(f"  - Average confidence: {total_confidence:.2%}")
    if passed_count == len(tests):
        print("  - ✅ All core scheduling features working as expected")
    else:
        print("  - ⚠️ Some features need attention")

    # Log evaluation summary
    log_file = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(log_file, "w") as f:
        json.dump(
            {
                "timestamp": str(date.today()),
                "total_tests": len(tests),
                "passed": passed_count,
                "average_confidence": total_confidence,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n✅ Evaluation results saved to: {log_file}")
    return passed_count == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
