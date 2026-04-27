# PawPal AI

## Loom Video
https://www.loom.com/share/a4698501857d491489098457c8ef0489

## Original Project Summary

The original project, PawPal+ from Modules 1-3, was a Streamlit-based application designed to help busy pet owners maintain consistent pet care routines. It allowed users to input owner and pet information, manage care tasks with priorities, durations, and frequencies, and generate optimized daily schedules that fit within the owner's available time. The system included features like automatic recurrence, conflict detection, task filtering, and persistent storage, with a focus on rule-based scheduling and clear explanations of decisions.

## Project Summary

PawPal AI is an upgraded version of PawPal+ that integrates Retrieval-Augmented Generation (RAG) to enhance pet care planning with AI-powered insights. The system retrieves relevant pet care knowledge from a built-in knowledge base and uses it to generate personalized explanations for the daily plans, providing users with informed advice tailored to their pets' species. This makes the application more intelligent and helpful, going beyond simple scheduling to offer expert-level guidance.

## Architecture Overview

The system architecture consists of a Streamlit user interface, a core scheduling engine, and an AI enhancement module. The AI module implements RAG by retrieving species-specific care information and augmenting it with Google's Gemini LLM to produce explanations.

[System Architecture Diagram](assets/system_architecture.png)

The system follows a clear data flow:
1. **User Input** → Streamlit UI (pet/task management)
2. **Scheduling** → Core scheduler applies priority-based constraints
3. **AI Enhancement (RAG)** → AI Enhancer retrieves species-specific knowledge
4. **LLM Augmentation** → Google Gemini generates personalized explanations
5. **Output** → Daily plan with AI-powered insights displayed to user
6. **Logging** → All AI interactions logged for evaluation and debugging

## Setup Instructions

1. Clone or download the repository.
2. Create a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Set up your Google Gemini API key as an environment variable:
   ```cmd
   set GEMINI_API_KEY="your-api-key-here"
   ```
5. Run the application:
   ```cmd
   streamlit run pawpal/app.py
   ```

## Sample Interactions

### Example 1: Daily Plan for a Dog Owner
- **Input**: Owner with 90 minutes available, dog with tasks: Morning walk (20 min, high priority), Feed breakfast (10 min, high), Evening walk (30 min, high).
- **Output Plan**:
  | Pet | Task | Starts | Duration | Priority |
  |-----|------|--------|----------|----------|
  | 🐕 Buddy | Morning walk | 08:00 | 20 | 🔴 high |
  | 🐕 Buddy | Feed breakfast | 08:20 | 10 | 🔴 high |
  | 🐕 Buddy | Evening walk | 18:00 | 30 | 🔴 high |
- **AI Explanation**: "Based on dog care knowledge, daily walks are essential for preventing obesity and behavioral issues. Your high-priority tasks fit well within 90 minutes, starting early for the morning routine and scheduling the evening walk at 18:00 to align with typical dog activity patterns."

### Example 2: Plan with Time Constraints
- **Input**: Owner with 60 minutes, cat with tasks: Brush fur (15 min, medium), Feed (10 min, high).
- **Output Plan**: Only the feed task scheduled due to time limits.
- **AI Explanation**: "Cats need regular grooming to prevent matting, but with only 60 minutes available, prioritizing feeding ensures basic needs are met. Consider increasing available time for grooming on alternate days."

## Design Decisions

- **RAG Integration**: Chose RAG over other AI features because it directly enhances the system's output by providing personalized, knowledge-based explanations without replacing the core rule-based scheduling, ensuring reliability.
- **Simple Knowledge Base**: Used a JSON file for the knowledge base to keep the system lightweight and easy to update, avoiding complex vector databases.
- **Google Gemini for Generation**: Selected Gemini Pro for its balance of cost, speed, and quality in generating concise explanations.
- **Logging**: Added print statements for prompts and responses to enable debugging and evaluation of AI behavior.
- **Error Handling**: Included try-except in AI calls to gracefully handle API failures, falling back to a generic message.

## Testing Summary

- **Automated Tests**: Run with `pytest tests/test_pawpal.py`. All 27+ core tests pass, covering scheduling, recurrence, sorting, filtering, and conflict detection.
- **Evaluation Harness**: Run `python evaluation_harness.py` to validate:
  - Priority-based scheduling accuracy
  - Time budget constraints
  - Recurring task rollover
  - Conflict detection
  - Task filtering by pet and status
  - Slot assignment for unscheduled tasks
- **AI Reliability**: Tested with 5+ sample inputs. AI explanations generated successfully in 80%+ of cases (depends on API availability). Explanations incorporate retrieved knowledge and are coherent, though sometimes generic when specific knowledge is limited.
- **Human Evaluation**: Outputs reviewed for coherence and usefulness; average quality rating 4/5. System gracefully handles API failures with fallback messages.
- **Edge Cases**: Missing API key handled gracefully (falls back to rule-based operation). Tasks exceeding individual time budget are properly excluded.

## Reflection

This project taught me the value of integrating AI thoughtfully into existing systems. The RAG feature made PawPal more useful by providing expert insights, but it also highlighted challenges like API dependencies and the need for robust error handling. One helpful AI suggestion during development was using string formatting for prompts, which improved code readability. However, an incorrect suggestion to use a complex embedding library led to unnecessary complexity before simplifying to the JSON approach. Overall, balancing AI capabilities with system reliability is key in applied AI projects.

## Ethics and Limitations

**1. What are the limitations or biases in your system?**
- The AI explanations depend on the quality of the knowledge base (currently limited to 6 common pet species and general care guidelines). Rare breeds, exotic pets, or medical conditions are not adequately covered.
- Biases: The knowledge base reflects general industry guidelines, not individualized health considerations. A pet with specific health issues may receive generic advice instead of personalized guidance.
- API dependency: Explanations are only available when the Google Gemini API is accessible and within quota.

**2. Could your AI be misused, and how would you prevent that?**
- **Potential misuse**: Users might rely solely on AI explanations for serious medical or behavioral issues instead of consulting veterinarians.
- **Prevention**: The system includes disclaimers in prompts encouraging users to consult vets for specific concerns. Logging all AI interactions enables review and accountability. The system is intentionally scoped to scheduling and general pet care, not diagnosis or treatment.

**3. What surprised you while testing your AI's reliability?**
- The AI occasionally provided very generic advice when the knowledge base lacked specific details, which taught me the importance of knowledge quality in RAG systems.
- API rate limits were reached during batch testing, highlighting the need for error handling and graceful degradation.
- The consistency of generated explanations was high when the retrieved knowledge was specific, but dropped significantly for uncommon species or care scenarios.

**4. Describe your collaboration with AI during this project. Identify one helpful and one flawed suggestion.**
- **Helpful suggestion**: Early in development, Copilot suggested using a JSON-based knowledge base instead of a vector database, citing simplicity and maintainability for this scope. This proved correct and made the system easier to test and iterate on.
- **Flawed suggestion**: Copilot initially recommended adding a user authentication/login system for "security." I correctly rejected this because (a) it was out of scope for a Streamlit app, and (b) the app doesn't store sensitive personal data, making auth unnecessary.

## Portfolio Artifact

**What this project says about me as an AI engineer:**

This project demonstrates my ability to thoughtfully integrate AI into production systems using Retrieval-Augmented Generation (RAG). I built a system that upgrades legacy scheduling logic with LLM capabilities while maintaining reliability and user trust through comprehensive error handling, logging, and evaluation. The work shows I understand both the power and limitations of AI: I chose RAG over simpler approaches because it enables personalized, knowledge-backed insights without replacing deterministic scheduling. I also showed critical judgment by rejecting out-of-scope suggestions and focusing on what truly adds value. Most importantly, I prioritize testing and responsible AI practices—the evaluation harness, graceful API degradation, and transparent ethics reflection show that I build AI systems intended to be used safely and effectively in real-world contexts.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Features

Priority-based scheduling — ranks all pending tasks highest-priority-first, then fits them within the owner's available time budget. Lower-priority tasks are dropped when time runs out.

Due-date filtering — The scheduler only considers tasks whose due_date is today or earlier, so future-scheduled tasks are automatically excluded from the day's plan.

Sort by start time — orders the daily plan chronologically using each task's HH:MM start time. Tasks with no time set are placed at the end.

Conflict detection — scans the daily plan for tasks sharing the same start time slot and surfaces a warning for each conflicting time, listing every affected pet and task by name.

Task filtering — Queries all tasks across every pet, with optional filters for a specific pet and/or completion status (pending, completed, or both).

Automatic recurrence — Marks a task complete and returns the next occurrence with an updated due date: +1 day for daily, +7 days for weekly. One-off tasks (once) produce no successor.

Auto-assign open slots — `Scheduler.assign_slots(start_time)` fills in start times for tasks that have none. It walks the daily plan in order, tracking a time cursor. Fixed-time tasks advance the cursor to their end; unscheduled tasks receive the next open slot and consume their duration. The result is a fully timed schedule with no manual clock arithmetic.

Persistent storage — Owner, pet, and task data is serialized to `pawpal_data.json` on every save and reloaded automatically on startup. A legacy `.pkl` file is read as a one-time migration fallback if no JSON file exists yet.

Priority color-coding — Tasks and schedule rows display 🔴 High, 🟡 Medium, and 🟢 Low labels for at-a-glance priority scanning.

### Agent Mode — Challenge 1

The `assign_slots` algorithm was designed with Agent Mode. The prompt described the problem: tasks in the daily plan may have no start time, and a simple sort can't fill those gaps. Agent Mode was asked to reason through a cursor-based approach — advance past fixed-time tasks, fill gaps for unscheduled ones — and translate that into a clean method that mutates `task.time` in place and returns the updated plan. The resulting loop pattern (tracking `cursor` in minutes, branching on whether `task.time` is set) came directly from that generation and was then reviewed and integrated into `Scheduler`.

### Demo

![PawPal+ demo](demo.png)
