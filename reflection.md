# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Core actions the user should be able to do:
1. Add pet care task
2. See duration of task
3. Add pet to do each task
4. Edit info for each task

Objects for system:
Owner,
    Attributes: has pets
    Methods: Can be logged into, can access pets to edit, add pets, can log out of, and can remove pets.
Pet, 
    Attributes: tasks, name, DOB, animal
    Methods: add tasks, or edit info.
Tasks, 
    Attributes:has task name, task deadline, task duration, priority. 
    Methods: can check off tasks, and edited.
Scheduler,
    Attributes: calendar, something to be able to take tasks and create a daily plan
    Methods: Can add task, can remove task, can generate plans putting higher priority tasks first


- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

I initially wrote that you could add tasks in the task view but changed that to be part of the higher class scheduler. I also initially made the information of the pet it's own class, and also allowed for the pet class to add or delete pets but changed that so the owner can do it.
- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler primarily checks for the hour and minute time selected for the beginning of the task.

**b. Tradeoffs**
The detector only flags issues when tasks occur with the same start time in both minutes or hours. The logic doesn't extend to checking if the durations overlap. Adding in this functionality would necessitate to add logic like comparing if the ranges don't collide.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I Used AI to help me write the code for things like the mermaid js and for complicated parts of the python code in the tests and the streamlit additions. The prompts that got me the furthest with regards to the help I got was when I properly used the features to direct the AI to the right file beforehand instead of making it search for the file. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Once the AI recommended me to add in a system to log in and log out for security in the app. I eventually decided not to include this because adding in a proper log in system would be too complicated for the scope of this streamlit app.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I had some tests for recurring activities, the schedule, sorting tasks by time for each pet, detecting conflicts in time if two tasks were at the same time, and for filtering the pets' tasks. These are important tests because they are functionalities the user will see a lot in the program so ensuring that they work is essential.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am generally confident that the schedule works correctly seeing as my run throughs of the app and the test functions all ran successfully. 

- What edge cases would you test next if you had more time?

I would add edge cases for a task with a duration that exceeds the available time by itself. It won't be scheduled, but no warning is given to the user about it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm happy with how the project was able to incorporate new pets and edit them, along with the tasks.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I'd redesign the sorting to allow for new ways to sort the tasks after the full scheduler is made and to also see tasks that are there in the future or tasks that weren't able to be put on the scheduler. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned about the importance of ensuring to use different AI chat sessions to keep the contexts separate, as it allowed me to have much more focused and high quality feedback for the specific contexts I used for each of the sessions.