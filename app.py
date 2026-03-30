import os
import pickle
from datetime import date
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
PRIORITY_LABEL = {1: "low", 2: "medium", 3: "high"}
PRIORITY_EMOJI = {1: "🟢 low", 2: "🟡 medium", 3: "🔴 high"}
SPECIES_EMOJI = {"dog": "🐕", "cat": "🐈", "rabbit": "🐇", "bird": "🐦", "fish": "🐠", "hamster": "🐹"}

JSON_FILE = "pawpal_data.json"
LEGACY_PKL = "pawpal_data.pkl"


def species_icon(animal):
    return SPECIES_EMOJI.get(animal.lower().strip(), "🐾")


def load_owner():
    if os.path.exists(JSON_FILE):
        return Owner.load_from_json(JSON_FILE)
    if os.path.exists(LEGACY_PKL):
        with open(LEGACY_PKL, "rb") as f:
            old = pickle.load(f)
        # Reconstruct using the current class so new methods are available
        fresh = Owner(old.name, time_available=old.time_available)
        fresh.pets = old.pets
        return fresh
    return Owner("Jordan", time_available=90)


def save_owner(owner):
    owner.save_to_json(JSON_FILE)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")

# --- Initialize session state ---
# Evict any stale Owner instance loaded before save_to_json was added
if "owner" in st.session_state and not hasattr(st.session_state.owner, "save_to_json"):
    del st.session_state["owner"]

if "owner" not in st.session_state:
    st.session_state.owner = load_owner()
if "editing_task" not in st.session_state:
    st.session_state.editing_task = None
if "editing_pet" not in st.session_state:
    st.session_state.editing_pet = None

owner = st.session_state.owner

# --- Owner Info ---
st.subheader("Owner Info")
owner_name = st.text_input("Owner name", value=owner.name)
time_available = st.number_input(
    "Time available today (minutes)", min_value=10, max_value=480, value=owner.time_available
)
if st.button("Save owner info"):
    owner.name = owner_name
    owner.time_available = time_available
    save_owner(owner)
    st.success("Owner info saved.")

st.divider()

# --- Pets ---
st.subheader("Pets")

with st.expander("Add a new pet"):
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        new_pet_name = st.text_input("Pet name")
    with p_col2:
        new_pet_dob = st.date_input("Date of birth", key="new_pet_dob")
    with p_col3:
        new_pet_species = st.text_input("Species (e.g. dog, cat, rabbit...)")

    if st.button("Add pet"):
        if new_pet_name:
            owner.add_pet(Pet(new_pet_name, str(new_pet_dob), new_pet_species))
            save_owner(owner)
            st.success(f"Added {new_pet_name}!")
            st.rerun()
        else:
            st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    for i, pet in enumerate(owner.pets):
        p_col1, p_col2, p_col3, p_col4 = st.columns([3, 3, 1, 1])
        p_col1.write(f"{species_icon(pet.animal)} **{pet.name}** ({pet.animal})")
        p_col2.write(f"DOB: {pet.dob}")
        if p_col3.button("Edit", key=f"edit_pet_{i}", use_container_width=True):
            st.session_state.editing_pet = i
        if p_col4.button("Remove", key=f"remove_pet_{i}", use_container_width=True):
            owner.remove_pet(pet)
            st.session_state.editing_task = None
            st.session_state.editing_pet = None
            save_owner(owner)
            st.rerun()

    if st.session_state.editing_pet is not None:
        idx = st.session_state.editing_pet
        if idx < len(owner.pets):
            pet_to_edit = owner.pets[idx]
            st.markdown(f"**Editing pet:** {pet_to_edit.name}")
            ep_col1, ep_col2, ep_col3 = st.columns(3)
            with ep_col1:
                ep_name = st.text_input("Name", value=pet_to_edit.name, key="ep_name")
            with ep_col2:
                ep_dob = st.date_input(
                    "Date of birth", value=date.fromisoformat(pet_to_edit.dob), key="ep_dob"
                )
            with ep_col3:
                ep_species = st.text_input("Species", value=pet_to_edit.animal, key="ep_species")
            if st.button("Save pet changes"):
                pet_to_edit.edit_info(name=ep_name, dob=str(ep_dob), animal=ep_species)
                st.session_state.editing_pet = None
                save_owner(owner)
                st.rerun()

st.divider()

# --- Tasks ---
if not owner.pets:
    st.info("Add a pet above to start managing tasks.")
else:
    st.subheader("Tasks")

    pet_names = [p.name for p in owner.pets]
    selected_name = st.selectbox("Managing tasks for:", pet_names)
    pet = owner.pets[pet_names.index(selected_name)]

    st.markdown("**Add a task**")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with t_col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with t_col3:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with t_col4:
        task_time = st.text_input("Start time (HH:MM)", value="", placeholder="e.g. 08:00")

    t_col5, t_col6, t_col7 = st.columns(3)
    with t_col5:
        frequency = st.selectbox("Recurrence", ["daily", "weekly", "once"], index=0)
    with t_col6:
        task_due_date = st.date_input("Due date", value=date.today(), key="new_task_due")
    with t_col7:
        task_deadline = st.date_input("Deadline (optional)", value=None, key="new_task_deadline")

    if st.button("Add task"):
        time_value = task_time.strip() if task_time.strip() else None
        pet.add_task(Task(
            task_title,
            duration=int(duration),
            priority=PRIORITY_MAP[priority_label],
            frequency=frequency,
            deadline=task_deadline,
            time=time_value,
            due_date=task_due_date,
        ))
        save_owner(owner)
        st.success(f"Added '{task_title}' to {pet.name}'s tasks.")

    st.markdown(f"**{pet.name}'s tasks:**")
    if not pet.tasks:
        st.info("No tasks yet.")
    else:
        # Header row
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([3, 2, 2, 2, 2, 1, 1, 1])
        h1.caption("Task")
        h2.caption("Duration")
        h3.caption("Priority")
        h4.caption("Starts")
        h5.caption("Recurs / Next due")
        h6.caption("Done")
        h7.caption("Edit")
        h8.caption("Delete")

        for i, task in enumerate(pet.tasks):
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([3, 2, 2, 2, 2, 1, 1, 1])
            label = f"~~{task.task_name}~~" if task.completed else task.task_name
            c1.write(label)
            c2.write(f"{task.duration} min")
            c3.write(PRIORITY_EMOJI[task.priority])
            c4.write(task.time if task.time else "—")
            recur_info = task.frequency
            if not task.completed:
                recur_info += f" · {task.due_date}"
            if task.deadline:
                recur_info += f" (by {task.deadline})"
            c5.write(recur_info)

            if not task.completed:
                if c6.button("✓", key=f"done_{i}", use_container_width=True, help="Mark complete"):
                    pet.complete_task(task)
                    save_owner(owner)
                    st.rerun()
            else:
                c6.write("✓")

            if c7.button("Edit", key=f"edit_{i}", use_container_width=True):
                st.session_state.editing_task = i
            if c8.button("Del", key=f"delete_{i}", use_container_width=True):
                pet.tasks.pop(i)
                st.session_state.editing_task = None
                save_owner(owner)
                st.rerun()

        if st.session_state.editing_task is not None:
            idx = st.session_state.editing_task
            if idx < len(pet.tasks):
                task = pet.tasks[idx]
                st.markdown(f"**Editing:** {task.task_name}")
                e_col1, e_col2, e_col3, e_col4 = st.columns(4)
                with e_col1:
                    new_name = st.text_input("New title", value=task.task_name, key=f"e_name_{idx}")
                with e_col2:
                    new_duration = st.number_input(
                        "New duration", min_value=1, max_value=240, value=task.duration, key=f"e_dur_{idx}"
                    )
                with e_col3:
                    current_label = PRIORITY_LABEL[task.priority]
                    new_priority_label = st.selectbox(
                        "New priority", ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(current_label),
                        key=f"e_pri_{idx}"
                    )
                with e_col4:
                    new_time = st.text_input(
                        "Start time (HH:MM)", value=task.time if task.time else "", key=f"e_time_{idx}"
                    )
                e_col5, e_col6, e_col7 = st.columns(3)
                with e_col5:
                    new_frequency = st.selectbox(
                        "Recurrence", ["daily", "weekly", "once"],
                        index=["daily", "weekly", "once"].index(task.frequency),
                        key=f"e_freq_{idx}"
                    )
                with e_col6:
                    new_due_date = st.date_input("Due date", value=task.due_date, key=f"e_due_{idx}")
                with e_col7:
                    new_deadline = st.date_input(
                        "Deadline (optional)", value=task.deadline, key=f"e_deadline_{idx}"
                    )
                if st.button("Save changes"):
                    time_value = new_time.strip() if new_time.strip() else None
                    task.edit(
                        task_name=new_name,
                        duration=int(new_duration),
                        priority=PRIORITY_MAP[new_priority_label],
                        frequency=new_frequency,
                        deadline=new_deadline,
                        time=time_value,
                    )
                    task.due_date = new_due_date
                    st.session_state.editing_task = None
                    save_owner(owner)
                    st.rerun()

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

s_col1, s_col2, s_col3 = st.columns(3)
with s_col1:
    sort_by_time = st.checkbox("Sort by start time", value=True)
with s_col2:
    auto_assign = st.checkbox("Auto-assign open slots", value=False)
with s_col3:
    slot_start = st.text_input("Slot start time (HH:MM)", value="08:00", disabled=not auto_assign)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    if not plan:
        st.warning("No tasks could be scheduled. Add tasks above or increase available time.")
    else:
        if sort_by_time:
            plan = scheduler.sort_by_time()
        if auto_assign:
            plan = scheduler.assign_slots(start_time=slot_start.strip() or "08:00")
            if sort_by_time:
                plan = scheduler.sort_by_time()

        # Conflict warnings — shown before the table so the owner can act first
        conflicts = scheduler.detect_conflicts()
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

        if conflicts:
            st.info(
                f"{len(plan)} tasks scheduled — please resolve the time conflicts "
                "above before starting your day."
            )
        else:
            st.success(
                f"All clear! {len(plan)} tasks fit within "
                f"{owner.time_available} available minutes."
            )

        rows = [
            {
                "Pet": f"{species_icon(p.animal)} {p.name}",
                "Task": task.task_name,
                "Starts": task.time if task.time else "—",
                "Duration (min)": task.duration,
                "Priority": PRIORITY_EMOJI[task.priority],
            }
            for p, task in plan
        ]
        st.table(rows)

st.divider()

# --- Filter Tasks ---
st.subheader("Filter Tasks")

with st.expander("Filter options"):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        pet_options = ["All pets"] + [p.name for p in owner.pets]
        filter_pet = st.selectbox("Pet", pet_options, key="filter_pet")
    with f_col2:
        status_options = {"Any status": None, "Pending only": False, "Completed only": True}
        filter_status_label = st.selectbox("Status", list(status_options.keys()), key="filter_status")

    if st.button("Apply filter"):
        scheduler = Scheduler(owner)
        pet_name = None if filter_pet == "All pets" else filter_pet
        completed = status_options[filter_status_label]
        results = scheduler.filter_tasks(pet_name=pet_name, completed=completed)

        if not results:
            st.info("No tasks match this filter.")
        else:
            rows = [
                {
                    "Pet": f"{species_icon(p.animal)} {p.name}",
                    "Task": task.task_name,
                    "Duration (min)": task.duration,
                    "Priority": PRIORITY_EMOJI[task.priority],
                    "Status": "✅ Done" if task.completed else "⏳ Pending",
                }
                for p, task in results
            ]
            st.success(f"{len(rows)} task(s) found.")
            st.table(rows)
