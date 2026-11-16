import streamlit as st
import sqlite3

from datetime import date

# Page configuration
st.set_page_config(
    page_title="Student Study Planner",
    page_icon="📚",
    layout="wide"
)

# Database connection
conn = sqlite3.connect(
    "study_planner.db",
    check_same_thread=False
)
cursor = conn.cursor()

# Create database tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE
)
""")

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    subject_name TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0
)
""")

conn.commit()

# Main heading
st.title("📚 Student Study Planner")
st.write("Organize your studies and achieve your goals!")

# Sidebar
st.sidebar.title("📌 Menu")

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Dashboard", "Subjects", "Timetable", "Tasks"]
)

# DASHBOARD
if menu == "Dashboard":

    st.header("📊 Dashboard")

    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM schedules")
    total_schedules = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE completed = 1"
    )
    completed_tasks = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Subjects", total_subjects)
    col2.metric("Study Schedules", total_schedules)
    col3.metric("Total Tasks", total_tasks)
    col4.metric("Completed Tasks", completed_tasks)

    st.divider()

    st.subheader("🎯 Study Motivation")
    st.success(
        "Small progress every day leads to big results!"
    )

# SUBJECTS
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

    cursor.execute(
        "SELECT id, subject_name FROM subjects ORDER BY id"
    )

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

# TIMETABLE
elif menu == "Timetable":

    st.header("📅 Study Timetable")

    cursor.execute(
        "SELECT subject_name FROM subjects ORDER BY subject_name"
    )

    subject_list = [
        row[0] for row in cursor.fetchall()
    ]

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
                value=date.today()
            )

            study_time = st.time_input("Select Study Time")

            duration = st.selectbox(
                "Study Duration",
                ["30 minutes", "1 hour", "1.5 hours",
                 "2 hours", "3 hours"]
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

        st.divider()

        st.subheader("📋 My Study Schedule")

        cursor.execute("""
            SELECT id, subject_name, study_date,
                   study_time, duration
            FROM schedules
            ORDER BY study_date, study_time
        """)

        schedules = cursor.fetchall()

        for row in schedules:

            st.write(
                f"📘 **{row[1]}** | "
                f"📅 {row[2]} | "
                f"⏰ {row[3]} | "
                f"⌛ {row[4]}"
            )

            if st.button("Delete Schedule", key=f"sch_{row[0]}"):

                cursor.execute(
                    "DELETE FROM schedules WHERE id = ?",
                    (row[0],)
                )

                conn.commit()
                st.rerun()

    else:
        st.info("Please add subjects before creating a timetable.")

# TASKS
elif menu == "Tasks":

    st.header("✅ Study Tasks")

    cursor.execute(
        "SELECT subject_name FROM subjects ORDER BY subject_name"
    )

    subject_list = [
        row[0] for row in cursor.fetchall()
    ]

    if subject_list:

        with st.form("task_form"):

            task_name = st.text_input("Enter Task Name")

            subject = st.selectbox(
                "Select Subject",
                subject_list
            )

            due_date = st.date_input(
                "Task Due Date",
                value=date.today()
            )

            submit = st.form_submit_button("Add Task")

            if submit:

                if task_name.strip():

                    cursor.execute("""
                        INSERT INTO tasks
                        (task_name, subject_name, due_date)
                        VALUES (?, ?, ?)
                    """, (
                        task_name.strip(),
                        subject,
                        str(due_date)
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
                   due_date, completed
            FROM tasks
            ORDER BY due_date
        """)

        tasks = cursor.fetchall()

        for task in tasks:

            task_id, name, subject, due, completed = task

            checked = st.checkbox(
                f"{name} - {subject} - Due: {due}",
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

            if st.button("Delete Task", key=f"del_{task_id}"):

                cursor.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    (task_id,)
                )

                conn.commit()
                st.rerun()

    else:
        st.info("Please add subjects before creating tasks.")

conn.close()