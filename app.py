import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
PRIORITY_LABEL = {1: "low", 2: "medium", 3: "high"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Initialize session state ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", time_available=90)
if "editing_task" not in st.session_state:
    st.session_state.editing_task = None

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
    st.success("Owner info updated.")

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
            st.success(f"Added {new_pet_name}!")
            st.rerun()
        else:
            st.warning("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    for i, pet in enumerate(owner.pets):
        p_col1, p_col2, p_col3 = st.columns([3, 3, 1])
        p_col1.write(f"**{pet.name}** ({pet.animal})")
        p_col2.write(f"DOB: {pet.dob}")
        if p_col3.button("Remove", key=f"remove_pet_{i}", use_container_width=True):
            owner.remove_pet(pet)
            st.session_state.editing_task = None
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
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with t_col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with t_col3:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        pet.add_task(Task(task_title, duration=int(duration), priority=PRIORITY_MAP[priority_label]))
        st.success(f"Added '{task_title}' to {pet.name}'s tasks.")

    st.markdown(f"**{pet.name}'s tasks:**")
    if not pet.tasks:
        st.info("No tasks yet.")
    else:
        for i, task in enumerate(pet.tasks):
            t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns([3, 2, 2, 1.2, 1.2])
            t_col1.write(task.task_name)
            t_col2.write(f"{task.duration} min")
            t_col3.write(PRIORITY_LABEL[task.priority])
            if t_col4.button("Edit", key=f"edit_{i}", use_container_width=True):
                st.session_state.editing_task = i
            if t_col5.button("Delete", key=f"delete_{i}", use_container_width=True):
                pet.tasks.pop(i)
                st.session_state.editing_task = None
                st.rerun()

        if st.session_state.editing_task is not None:
            idx = st.session_state.editing_task
            if idx < len(pet.tasks):
                task = pet.tasks[idx]
                st.markdown(f"**Editing:** {task.task_name}")
                e_col1, e_col2, e_col3 = st.columns(3)
                with e_col1:
                    new_name = st.text_input("New title", value=task.task_name, key="e_name")
                with e_col2:
                    new_duration = st.number_input(
                        "New duration", min_value=1, max_value=240, value=task.duration, key="e_dur"
                    )
                with e_col3:
                    current_label = PRIORITY_LABEL[task.priority]
                    new_priority_label = st.selectbox(
                        "New priority", ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(current_label),
                        key="e_pri"
                    )
                if st.button("Save changes"):
                    task.edit(
                        task_name=new_name,
                        duration=int(new_duration),
                        priority=PRIORITY_MAP[new_priority_label]
                    )
                    st.session_state.editing_task = None
                    st.rerun()

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.success(f"Scheduled {len(plan)} tasks within {owner.time_available} available minutes.")
        for i, (p, task) in enumerate(plan, start=1):
            st.markdown(
                f"**{i}. [{p.name}]** {task.task_name} — "
                f"{task.duration} min | priority: {PRIORITY_LABEL[task.priority]}"
            )
    else:
        st.warning("No tasks could be scheduled. Add tasks above or increase available time.")
