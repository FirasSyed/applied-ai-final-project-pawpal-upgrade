class Owner:
    def __init__(self):
        self.pets = []

    def login(self):
        pass

    def logout(self):
        pass

    def access_pets(self):
        pass

    def add_pet(self, _pet):
        pass

    def remove_pet(self, _pet):
        pass


class Pet:
    def __init__(self):
        self.name = ""
        self.dob = ""
        self.animal = ""
        self.tasks = []

    def edit_info(self):
        pass

    def add_task(self, task):
        pass


class Tasks:
    def __init__(self):
        self.task_name = ""
        self.task_deadline = ""
        self.task_duration = 0
        self.priority = 0

    def edit(self):
        pass

    def check_off(self):
        pass


class Planner:
    def __init__(self):
        self.calendar = []
        self.daily_plan = []

    def add_task(self, task):
        pass

    def remove_task(self, task):
        pass

    def generate_plan(self):
        pass
