from pawpal_system import Task, Pet


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
