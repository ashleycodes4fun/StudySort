import streamlit as st
import pandas as pd
import base64
from datetime import date

st.set_page_config(
    page_title="StudySort",
    page_icon="📚",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "assignments" not in st.session_state:
    st.session_state.assignments = []

if "brain_dump" not in st.session_state:
    st.session_state.brain_dump = ""


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("📚 StudySort")

st.caption(
    "A study planner designed to reduce overwhelm "
    "and help you focus on what to do next."
)


# -------------------------------------------------
# BRAIN DUMP
# -------------------------------------------------

with st.expander("🧠 Brain Dump"):

    st.write(
        "Write down anything on your mind. "
        "It does not need to be organized."
    )

    st.session_state.brain_dump = st.text_area(
        "What's on your mind?",
        value=st.session_state.brain_dump,
        height=120,
        placeholder=(
            "Example: Physics homework, email professor, "
            "study for CS quiz..."
        )
    )


# -------------------------------------------------
# ADD ASSIGNMENT
# -------------------------------------------------

st.subheader("➕ Add an Assignment")

col1, col2 = st.columns(2)

with col1:

    course = st.text_input(
        "Course",
        placeholder="Example: CS 106B"
    )

    assignment = st.text_input(
        "Assignment",
        placeholder="Example: Coding Project 1"
    )

    due_date = st.date_input(
        "Due Date",
        min_value=date.today()
    )

with col2:

    hours = st.number_input(
        "Estimated Hours",
        min_value=1,
        max_value=50,
        value=2
    )

    difficulty = st.selectbox(
        "How difficult does this feel?",
        ["Easy", "Medium", "Hard"]
    )

    energy = st.selectbox(
        "Energy needed",
        ["Low", "Medium", "High"]
    )

steps_text = st.text_area(
    "Break it into smaller steps",
    placeholder=(
        "Example:\n"
        "Read instructions\n"
        "Write pseudocode\n"
        "Code first function\n"
        "Test program"
    )
)

if st.button(
    "Add Assignment",
    use_container_width=True
):

    if course and assignment:

        days_left = (due_date - date.today()).days

        if days_left <= 2:
            priority = "🔴 High"
            priority_score = 1

        elif days_left <= 5:
            priority = "🟡 Medium"
            priority_score = 2

        else:
            priority = "🟢 Low"
            priority_score = 3

        steps = [
            step.strip()
            for step in steps_text.split("\n")
            if step.strip()
        ]

        st.session_state.assignments.append({
            "Course": course,
            "Assignment": assignment,
            "Due Date": due_date,
            "Days Left": days_left,
            "Hours": hours,
            "Difficulty": difficulty,
            "Energy": energy,
            "Priority": priority,
            "Priority Score": priority_score,
            "Completed": False,
            "Steps": steps,
            "Completed Steps": []
        })

        st.success("Assignment added.")

    else:
        st.warning(
            "Please enter a course and assignment."
        )


st.divider()


# -------------------------------------------------
# MAIN PLANNER
# -------------------------------------------------

if st.session_state.assignments:

    active = [
        task
        for task in st.session_state.assignments
        if not task["Completed"]
    ]

    completed = [
        task
        for task in st.session_state.assignments
        if task["Completed"]
    ]


    # -------------------------------------------------
    # PROGRESS
    # -------------------------------------------------

    st.subheader("📈 Progress")

    total = len(st.session_state.assignments)
    completed_count = len(completed)

    progress = completed_count / total if total > 0 else 0

    st.progress(progress)

    st.write(
        f"**{completed_count} of {total} assignments completed**"
    )


    # -------------------------------------------------
    # SORT OPTION
    # -------------------------------------------------

    sort_method = st.selectbox(
        "Organize my tasks by",
        [
            "What should I do first?",
            "Due date",
            "Difficulty",
            "Energy needed"
        ]
    )


    def difficulty_score(value):
        scores = {
            "Hard": 1,
            "Medium": 2,
            "Easy": 3
        }
        return scores[value]


    def energy_score(value):
        scores = {
            "Low": 1,
            "Medium": 2,
            "High": 3
        }
        return scores[value]


    if sort_method == "Due date":

        active = sorted(
            active,
            key=lambda x: x["Days Left"]
        )

    elif sort_method == "Difficulty":

        active = sorted(
            active,
            key=lambda x: difficulty_score(
                x["Difficulty"]
            )
        )

    elif sort_method == "Energy needed":

        active = sorted(
            active,
            key=lambda x: energy_score(
                x["Energy"]
            )
        )

    else:

        active = sorted(
            active,
            key=lambda x: (
                x["Priority Score"],
                x["Days Left"],
                -x["Hours"]
            )
        )


    # -------------------------------------------------
    # START HERE
    # -------------------------------------------------

    if active:

        first = active[0]

        st.subheader("🎯 Start Here")

        st.info(
            f"""
**{first["Assignment"]}**

📘 {first["Course"]}

📅 Due in **{first["Days Left"]} days**

⏱ Estimated time: **{first["Hours"]} hours**

🧠 Difficulty: **{first["Difficulty"]}**

⚡ Energy needed: **{first["Energy"]}**

{first["Priority"]}
"""
        )

        if first["Steps"]:

            st.write("**Start with just this:**")

            st.success(
                first["Steps"][0]
            )

        elif first["Hours"] >= 4:

            st.success(
                "Start with a short focus session. "
                "You do not need to finish the entire assignment."
            )

        elif first["Hours"] >= 2:

            st.success(
                "Try one focused work session to get started."
            )

        else:

            st.success(
                "This may be a good quick-win task."
            )


    # -------------------------------------------------
    # TODAY VIEW
    # -------------------------------------------------

    st.divider()

    st.subheader("☀️ Today")

    st.caption(
        "Showing only a few tasks at a time "
        "to make your workload easier to manage."
    )

    today_tasks = active[:3]

    if today_tasks:

        for number, task in enumerate(
            today_tasks,
            start=1
        ):

            st.write(
                f"**{number}. {task['Assignment']}**"
            )

            st.caption(
                f"{task['Course']} • "
                f"{task['Priority']} • "
                f"{task['Hours']} hrs"
            )

    else:

        st.success(
            "Nothing left to do. 🎉"
        )


    # -------------------------------------------------
    # FOCUS TIMER
    # -------------------------------------------------

    st.divider()

    st.subheader("⏱ Focus Session")

    st.caption(
        "Choose how many minutes you want to focus."
    )

    # Load your local MP3 file
    try:
        with open("chime.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode()

        st.components.v1.html(
            f"""
            <div style="
                font-family: Arial, sans-serif;
                padding-top: 5px;
            ">

                <label style="
                    font-size: 16px;
                    font-weight: 600;
                ">
                    Focus time in minutes
                </label>

                <br><br>

                <input
                    id="minutes"
                    type="number"
                    min="1"
                    max="180"
                    value="25"
                    style="
                        width: 140px;
                        padding: 10px;
                        font-size: 16px;
                        border-radius: 8px;
                        border: 1px solid #ccc;
                    "
                >

                <br><br>

                <button
                    onclick="startTimer()"
                    style="
                        padding: 10px 18px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 8px;
                    "
                >
                    ▶ Start Focus
                </button>

                <button
                    onclick="resetTimer()"
                    style="
                        padding: 10px 18px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 8px;
                        margin-left: 8px;
                    "
                >
                    Reset
                </button>

                <br><br>

                <div
                    id="timer"
                    style="
                        font-size: 42px;
                        font-weight: bold;
                        margin-top: 10px;
                    "
                >
                    Timer is ready.
                </div>

                <div
                    id="complete"
                    style="
                        margin-top: 12px;
                        font-size: 20px;
                        font-weight: bold;
                    "
                ></div>

                <audio id="alarm">
                    <source
                        src="data:audio/mp3;base64,{audio_base64}"
                        type="audio/mpeg"
                    >
                </audio>

            </div>

            <script>

            let interval = null;
            let secondsRemaining = 0;

            const alarm = document.getElementById("alarm");


            function startTimer() {{

                if (interval) {{
                    clearInterval(interval);
                }}

                const minutes =
                    parseInt(
                        document.getElementById(
                            "minutes"
                        ).value
                    );

                secondsRemaining = minutes * 60;

                document.getElementById(
                    "complete"
                ).innerHTML = "";

                /*
                Unlock audio using the user's click.
                */
                alarm.volume = 0;

                alarm.play().then(() => {{

                    alarm.pause();
                    alarm.currentTime = 0;
                    alarm.volume = 1;

                }}).catch(() => {{

                    alarm.volume = 1;

                }});

                updateDisplay();

                interval = setInterval(() => {{

                    secondsRemaining--;

                    updateDisplay();

                    if (secondsRemaining <= 0) {{

                        clearInterval(interval);
                        interval = null;

                        document.getElementById(
                            "timer"
                        ).innerHTML = "00:00";

                        document.getElementById(
                            "complete"
                        ).innerHTML =
                            "🎉 Focus session complete!";

                        alarm.currentTime = 0;
                        alarm.volume = 1;

                        alarm.play().catch(
                            error => {{
                                console.log(
                                    "Audio blocked:",
                                    error
                                );
                            }}
                        );
                    }}

                }}, 1000);
            }}


            function updateDisplay() {{

                const minutes =
                    Math.floor(
                        secondsRemaining / 60
                    );

                const seconds =
                    secondsRemaining % 60;

                document.getElementById(
                    "timer"
                ).innerHTML =
                    String(minutes).padStart(
                        2,
                        "0"
                    )
                    + ":"
                    + String(seconds).padStart(
                        2,
                        "0"
                    );
            }}


            function resetTimer() {{

                if (interval) {{
                    clearInterval(interval);
                }}

                interval = null;

                alarm.pause();
                alarm.currentTime = 0;

                document.getElementById(
                    "timer"
                ).innerHTML =
                    "Timer is ready.";

                document.getElementById(
                    "complete"
                ).innerHTML = "";
            }}

            </script>
            """,
            height=330
        )

    except FileNotFoundError:

        st.error(
            "chime.mp3 was not found. "
            "Make sure it is in the same StudySort folder as app.py."
        )


    # -------------------------------------------------
    # ALL TASKS
    # -------------------------------------------------

    st.divider()

    st.subheader("📝 All Tasks")

    if active:

        for task in active:

            index = (
                st.session_state.assignments
                .index(task)
            )

            with st.container(border=True):

                checked = st.checkbox(
                    f"{task['Priority']} "
                    f"{task['Course']} — "
                    f"{task['Assignment']}",
                    value=False,
                    key=f"assignment_{index}"
                )

                st.caption(
                    f"Due {task['Due Date']} • "
                    f"{task['Days Left']} days left • "
                    f"{task['Hours']} hrs • "
                    f"{task['Difficulty']} • "
                    f"{task['Energy']} energy"
                )


                # SMALL STEPS
                if task["Steps"]:

                    st.write(
                        "**Small steps:**"
                    )

                    for step_number, step in enumerate(
                        task["Steps"]
                    ):

                        step_key = (
                            f"step_{index}_{step_number}"
                        )

                        done = st.checkbox(
                            step,
                            value=(
                                step
                                in task[
                                    "Completed Steps"
                                ]
                            ),
                            key=step_key
                        )

                        if (
                            done
                            and step
                            not in task[
                                "Completed Steps"
                            ]
                        ):

                            task[
                                "Completed Steps"
                            ].append(step)

                        elif (
                            not done
                            and step
                            in task[
                                "Completed Steps"
                            ]
                        ):

                            task[
                                "Completed Steps"
                            ].remove(step)


                # COMPLETE ASSIGNMENT
                if checked:

                    st.session_state.assignments[
                        index
                    ]["Completed"] = True

                    st.rerun()


                # DELETE ASSIGNMENT
                if st.button(
                    "Delete",
                    key=f"delete_{index}"
                ):

                    st.session_state.assignments.pop(
                        index
                    )

                    st.rerun()

    else:

        st.success(
            "🎉 You've completed everything!"
        )


    # -------------------------------------------------
    # COMPLETED SECTION
    # -------------------------------------------------

    st.divider()

    with st.expander(
        f"✅ Completed ({len(completed)})"
    ):

        if completed:

            for task in completed:

                index = (
                    st.session_state.assignments
                    .index(task)
                )

                checked = st.checkbox(
                    f"✅ {task['Course']} — "
                    f"{task['Assignment']}",
                    value=True,
                    key=f"completed_{index}"
                )

                if not checked:

                    st.session_state.assignments[
                        index
                    ]["Completed"] = False

                    st.rerun()

        else:

            st.write(
                "No completed assignments yet."
            )


    # -------------------------------------------------
    # QUICK OVERVIEW
    # -------------------------------------------------

    st.divider()

    st.subheader("📊 Quick Overview")

    if active:

        active_df = pd.DataFrame(active)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Assignments Left",
            len(active)
        )

        col2.metric(
            "Study Hours Left",
            active_df["Hours"].sum()
        )

        urgent = len(
            active_df[
                active_df[
                    "Priority"
                ] == "🔴 High"
            ]
        )

        col3.metric(
            "High Priority",
            urgent
        )


    # -------------------------------------------------
    # CLEAR PLANNER
    # -------------------------------------------------

    st.divider()

    if st.button(
        "Clear Entire Planner"
    ):

        st.session_state.assignments = []

        st.rerun()


# -------------------------------------------------
# EMPTY PLANNER
# -------------------------------------------------

else:

    st.subheader("🌱 Your planner is empty")

    st.write(
        "Start by adding one assignment above. "
        "You do not need to organize everything at once."
    )