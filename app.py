

import streamlit as st
import sqlite3
import time
from datetime import date
from notification_sender import send_notification, load_device_token
# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Student Study Planner",
    page_icon="📚",
    layout="wide"
)

# =====================================
# DATABASE CONNECTION
# =====================================

conn = sqlite3.connect(
    "study_planner.db",
    check_same_thread=False
)

cursor = conn.cursor()

# Subjects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE
)
""")

# Schedules table
cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    subject_name TEXT,
    study_date TEXT,
    study_time TEXT,
    duration TEXT
)
""")

# Tasks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    subject_name TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0
)
""")
# Add reminder_time column if it does not exist
cursor.execute("PRAGMA table_info(tasks)")
task_columns = [column[1] for column in cursor.fetchall()]

if "reminder_time" not in task_columns:
    cursor.execute(
        "ALTER TABLE tasks ADD COLUMN reminder_time TEXT"
    )
# Exams table
cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    exam_date TEXT
)
""")

conn.commit()

# =====================================
# SESSION STATE
# =====================================

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_end" not in st.session_state:
    st.session_state.timer_end = 0.0

if "timer_remaining" not in st.session_state:
    st.session_state.timer_remaining = 1500

if "timer_mode" not in st.session_state:
    st.session_state.timer_mode = "Study"

if "timer_sessions" not in st.session_state:
    st.session_state.timer_sessions = 0

if "sent_notifications" not in st.session_state:
    st.session_state.sent_notifications = set()

today = date.today()

# =====================================
# 🔔 NOTIFICATION SYSTEM
# =====================================

# Task Notifications
cursor.execute("""
SELECT id, task_name, due_date
FROM tasks
WHERE completed = 0
""")

pending_tasks = cursor.fetchall()

for task_id, task_name, due_date in pending_tasks:

    due = date.fromisoformat(due_date)

    if due <= today:

        notification_id = f"task_{task_id}"

        if notification_id not in st.session_state.sent_notifications:

            if due == today:
                st.toast(
                    f"📚 Task due today: {task_name}",
                    icon="🔔"
                )
            else:
                st.toast(
                    f"⚠️ Overdue task: {task_name}",
                    icon="⏰"
                )

            st.session_state.sent_notifications.add(notification_id)


# Exam Notifications
cursor.execute("""
SELECT id, subject_name, exam_date
FROM exams
""")

upcoming_exams = cursor.fetchall()

for exam_id, subject_name, exam_date in upcoming_exams:

    exam_day = date.fromisoformat(exam_date)
    remaining_days = (exam_day - today).days

    if 0 <= remaining_days <= 3:

        notification_id = f"exam_{exam_id}"

        if notification_id not in st.session_state.sent_notifications:

            if remaining_days == 0:
                message = f"🚨 {subject_name} exam is today!"
            else:
                message = (
                    f"📅 {subject_name} exam in "
                    f"{remaining_days} day(s)!"
                )

            st.toast(message, icon="🔔")

            st.session_state.sent_notifications.add(notification_id)


# =====================================
# MAIN HEADING
# =====================================

st.title("📚 Student Study Planner")
st.write("Organize your studies and achieve your goals!")

# =====================================
# SIDEBAR MENU
# =====================================

st.sidebar.title("📌 Menu")

menu = st.sidebar.selectbox(
    "Choose an option",
    [
        "Dashboard",
        "Subjects",
        "Timetable",
        "Tasks",
        "Study Progress Tracker",
        "Pomodoro Timer",
        "Exam Countdown"
    ]
)

# =====================================
# DASHBOARD
# =====================================

if menu == "Dashboard":

    st.header("📊 Dashboard")

    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM schedules")
    total_schedules = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM tasks
    WHERE completed = 1
    """)
    completed_tasks = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Subjects", total_subjects)
    col2.metric("Study Schedules", total_schedules)
    col3.metric("Total Tasks", total_tasks)
    col4.metric("Completed Tasks", completed_tasks)

    st.divider()

    st.subheader("🔔 Notifications")

    cursor.execute("""
    SELECT COUNT(*) FROM tasks
    WHERE completed = 0 AND due_date <= ?
    """, (str(today),))

    due_tasks = cursor.fetchone()[0]

    if due_tasks > 0:
        st.warning(f"You have {due_tasks} task(s) due or overdue!")
    else:
        st.success("No tasks are due today. Keep going!")

    st.subheader("🎯 Study Motivation")

    st.success(
        "Small progress every day leads to big results!"
    )

# =====================================
# SUBJECT MANAGEMENT
# =====================================

elif menu == "Subjects":

    st.header("📖 Subject Management")

    subject = st.text_input("Enter Subject Name")

    if st.button("➕ Add Subject"):

        if subject.strip():

            try:
                cursor.execute(
                    "INSERT INTO subjects (subject_name) VALUES (?)",
                    (subject.strip(),)
                )

                conn.commit()

                st.success("Subject added successfully!")
                st.rerun()

            except sqlite3.IntegrityError:
                st.warning("This subject already exists.")

        else:
            st.warning("Please enter a subject name.")

    st.divider()

    st.subheader("📚 My Subjects")

    cursor.execute("""
    SELECT id, subject_name
    FROM subjects
    ORDER BY id
    """)

    subjects = cursor.fetchall()

    if subjects:

        for subject_id, subject_name in subjects:

            col1, col2 = st.columns([4, 1])

            col1.write(f"📘 {subject_name}")

            if col2.button("Delete", key=f"sub_{subject_id}"):

                cursor.execute(
                    "DELETE FROM subjects WHERE id = ?",
                    (subject_id,)
                )

                conn.commit()
                st.rerun()

    else:
        st.info("No subjects added yet.")

# =====================================
# TIMETABLE
# =====================================

elif menu == "Timetable":

    st.header("📅 Study Timetable")

    cursor.execute("""
    SELECT subject_name FROM subjects
    ORDER BY subject_name
    """)

    subject_list = [row[0] for row in cursor.fetchall()]

    if subject_list:

        with st.form("schedule_form"):

            st.subheader("Add Your Study Schedule")

            student = st.text_input("Student Name")

            subject = st.selectbox(
                "Select Subject",
                subject_list
            )

            study_date = st.date_input(
                "Select Date",
                value=today
            )

            study_time = st.time_input("Select Study Time")

            duration = st.selectbox(
                "Study Duration",
                [
                    "30 minutes",
                    "1 hour",
                    "1.5 hours",
                    "2 hours",
                    "3 hours"
                ]
            )

            submit = st.form_submit_button(
                "➕ Add to Timetable"
            )

            if submit:

                cursor.execute("""
                INSERT INTO schedules
                (student_name, subject_name,
                 study_date, study_time, duration)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    student,
                    subject,
                    str(study_date),
                    str(study_time),
                    duration
                ))

                conn.commit()

                st.success("Study schedule added!")
                st.rerun()

        st.divider()

        st.subheader("📋 My Study Schedule")

        cursor.execute("""
        SELECT id, subject_name, study_date,
               study_time, duration
        FROM schedules
        ORDER BY study_date, study_time
        """)

        schedules = cursor.fetchall()

        if schedules:

            for row in schedules:

                st.write(
                    f"📘 **{row[1]}** | "
                    f"📅 {row[2]} | "
                    f"⏰ {row[3]} | "
                    f"⌛ {row[4]}"
                )

                if st.button(
                    "Delete Schedule",
                    key=f"sch_{row[0]}"
                ):

                    cursor.execute(
                        "DELETE FROM schedules WHERE id = ?",
                        (row[0],)
                    )

                    conn.commit()
                    st.rerun()

        else:
            st.info("No schedules added yet.")

    else:
        st.info("Please add subjects before creating a timetable.")

# =====================================
# STUDY TASKS
# =====================================

elif menu == "Tasks":

    st.header("✅ Study Tasks")

    cursor.execute("""
    SELECT subject_name FROM subjects
    ORDER BY subject_name
    """)

    subject_list = [row[0] for row in cursor.fetchall()]

    if subject_list:

        with st.form("task_form"):

            task_name = st.text_input("Enter Task Name")

            subject = st.selectbox(
                "Select Subject",
                subject_list
            )

            due_date = st.date_input(
                "Task Due Date",
                value=today
            )

            reminder_time = st.time_input(
    "⏰ Reminder Time"
)
            submit = st.form_submit_button("Add Task")

            if submit:

                if task_name.strip():

                    cursor.execute("""
    INSERT INTO tasks
    (task_name, subject_name, due_date, reminder_time)
    VALUES (?, ?, ?, ?)
    """, (
        task_name.strip(),
        subject,
        str(due_date),
        str(reminder_time)
    ))

                    conn.commit()

                    st.success("Task added successfully!")
                    st.rerun()

                else:
                    st.warning("Please enter a task name.")

        st.divider()

        st.subheader("📝 My Tasks")

        cursor.execute("""
        SELECT id, task_name, subject_name,
               due_date, completed, reminder_time
        FROM tasks
        ORDER BY due_date
        """)

        tasks = cursor.fetchall()

        if tasks:

            for task in tasks:

                task_id, name, subject, due, completed, reminder_time = task

                checked = st.checkbox(
                    f"{name} - {subject} - Due: {due} - Reminder: {reminder_time}",
                    value=bool(completed),
                    key=f"task_{task_id}"
                )

                if checked != bool(completed):

                    cursor.execute(
                        "UPDATE tasks SET completed = ? WHERE id = ?",
                        (int(checked), task_id)
                    )

                    conn.commit()
                    st.rerun()

                if not completed and date.fromisoformat(due) < today:
                    st.warning(f"⚠️ {name} is overdue!")

                if st.button(
                    "Delete Task",
                    key=f"del_{task_id}"
                ):

                    cursor.execute(
                        "DELETE FROM tasks WHERE id = ?",
                        (task_id,)
                    )

                    conn.commit()
                    st.rerun()

        else:
            st.info("No tasks added yet.")

    else:
        st.info("Please add subjects before creating tasks.")

# =====================================
# STUDY PROGRESS TRACKER
# =====================================

elif menu == "Study Progress Tracker":

    st.header("📊 Study Progress Tracker")

    st.write("Track your study tasks and monitor your progress.")

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM tasks
    WHERE completed = 1
    """)

    completed = cursor.fetchone()[0]

    pending = total - completed

    percentage = (
        (completed / total) * 100 if total > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tasks", total)
    col2.metric("Completed Tasks", completed)
    col3.metric("Pending Tasks", pending)

    st.divider()

    st.subheader("🎯 Overall Progress")

    st.progress(int(percentage))

    st.success(
        f"Your study completion is {percentage:.1f}%"
    )

    st.subheader("📈 Task Performance")

    st.bar_chart({
        "Number of Tasks": {
            "Completed": completed,
            "Pending": pending
        }
    })

    st.divider()

    st.subheader("📚 Subject-wise Progress")

    cursor.execute("""
    SELECT subject_name,
           COUNT(*),
           SUM(completed)
    FROM tasks
    GROUP BY subject_name
    """)

    subject_progress = cursor.fetchall()

    if subject_progress:

        for subject, total_tasks, done in subject_progress:

            done = done or 0
            percent = done / total_tasks

            st.write(f"**{subject}**")

            st.progress(percent)

            st.caption(
                f"{done} out of {total_tasks} tasks completed"
            )

    else:
        st.info("Add some study tasks to see your progress.")

# =====================================
# POMODORO TIMER
# =====================================

elif menu == "Pomodoro Timer":

    st.header("⏱️ Pomodoro Study Timer")

    st.write("Stay focused with study sessions and short breaks.")

    mode = st.radio(
        "Choose Timer",
        ["Study (25 Minutes)", "Short Break (5 Minutes)"],
        horizontal=True
    )

    selected_mode = (
        "Study" if mode.startswith("Study") else "Break"
    )

    duration = 1500 if selected_mode == "Study" else 300

    # Reset when timer type changes
    if st.session_state.timer_mode != selected_mode:

        st.session_state.timer_running = False
        st.session_state.timer_remaining = duration
        st.session_state.timer_mode = selected_mode

    @st.fragment(run_every="1s")
    def timer_display():

        if st.session_state.timer_running:

            remaining = max(
                0,
                int(st.session_state.timer_end - time.time())
            )

            st.session_state.timer_remaining = remaining

            if remaining == 0:

                st.session_state.timer_running = False

                if st.session_state.timer_mode == "Study":
                    st.session_state.timer_sessions += 1

                st.toast(
                    "🎉 Your timer is completed!",
                    icon="🔔"
                )

                st.success("🎉 Timer completed!")

        else:
            remaining = st.session_state.timer_remaining

        minutes = remaining // 60
        seconds = remaining % 60

        st.subheader(
            f"📖 {st.session_state.timer_mode} Session"
        )

        st.markdown(
            f"<h1 style='text-align:center;font-size:65px;'>"
            f"{minutes:02d}:{seconds:02d}</h1>",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "▶️ Start",
                disabled=st.session_state.timer_running
            ):

                st.session_state.timer_end = time.time() + remaining
                st.session_state.timer_running = True
                st.rerun(scope="fragment")

        with col2:

            if st.button(
                "⏸️ Pause",
                disabled=not st.session_state.timer_running
            ):

                st.session_state.timer_remaining = max(
                    0,
                    int(st.session_state.timer_end - time.time())
                )

                st.session_state.timer_running = False
                st.rerun(scope="fragment")

        with col3:

            if st.button("🔄 Reset"):

                st.session_state.timer_running = False
                st.session_state.timer_remaining = duration
                st.rerun(scope="fragment")

        st.divider()

        st.metric(
            "Completed Study Sessions",
            st.session_state.timer_sessions
        )

    timer_display()

# =====================================
# EXAM COUNTDOWN
# =====================================

elif menu == "Exam Countdown":

    st.header("📅 Exam Countdown")

    st.write(
        "Plan your examinations and keep track of remaining days."
    )

    cursor.execute("""
    SELECT subject_name FROM subjects
    ORDER BY subject_name
    """)

    subject_list = [row[0] for row in cursor.fetchall()]

    if subject_list:

        with st.form("exam_form"):

            st.subheader("➕ Add Upcoming Exam")

            exam_subject = st.selectbox(
                "Select Exam Subject",
                subject_list
            )

            exam_date = st.date_input(
                "Select Exam Date",
                min_value=today
            )

            submit_exam = st.form_submit_button("Add Exam")

            if submit_exam:

                cursor.execute("""
                INSERT INTO exams (subject_name, exam_date)
                VALUES (?, ?)
                """, (
                    exam_subject,
                    str(exam_date)
                ))

                conn.commit()

                st.success("Exam added successfully!")
                st.rerun()

    else:
        st.info("Please add subjects before adding exams.")

    st.divider()

    st.subheader("📝 Upcoming Examinations")

    cursor.execute("""
    SELECT id, subject_name, exam_date
    FROM exams
    ORDER BY exam_date
    """)

    exams = cursor.fetchall()

    if exams:

        for exam_id, subject, exam_day in exams:

            exam_day = date.fromisoformat(exam_day)

            remaining_days = (exam_day - today).days

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                col1.write(f"📘 **{subject}**")
                col1.write(f"📅 Exam Date: {exam_day}")

                if remaining_days > 0:
                    col2.metric("Days Left", remaining_days)

                elif remaining_days == 0:
                    col2.warning("Exam is today!")

                else:
                    col2.info("Exam date has passed.")

                if st.button(
                    "Delete Exam",
                    key=f"exam_{exam_id}"
                ):

                    cursor.execute(
                        "DELETE FROM exams WHERE id = ?",
                        (exam_id,)
                    )

                    conn.commit()
                    st.rerun()

    else:
        st.info("No examinations added yet.")

# =====================================
# CLOSE DATABASE
# =====================================

conn.close()
st.divider()
st.subheader("🔔 Test Firebase Notification")

if st.button("Send Test Notification"):
    device_token = load_device_token()

    if device_token:
        result = send_notification(
            device_token,
            "Study Planner",
            "Your Firebase notifications are working!"
        )

        if result:
            st.success("Test notification sent successfully!")
    else:
        st.error("Device token not found. Please check device_token.txt.")
