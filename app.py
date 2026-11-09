

import streamlit as st
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Student Study Planner",
    page_icon="📚",
    layout="wide"
)

# Database connection
conn = sqlite3.connect("study_planner.db")
cursor = conn.cursor()

# Create subjects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE
)
""")
# Create subjects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE
)
""")

# Create schedules table
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
conn.commit()

# Main heading
st.title("📚 Student Study Planner")
st.write("Organize your studies and achieve your goals!")

# Sidebar menu
st.sidebar.title("Menu")

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Dashboard", "Subjects", "Timetable", "Tasks"]
)

# Dashboard
if menu == "Dashboard":

    st.header("📊 Dashboard")

    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Subjects", 2)
    col2.metric("Total Tasks", 9)
    col3.metric("Completed Tasks", 4)
    col4.metric("Pending Tasks", 3)

    st.divider()

    st.subheader("🎯 Study Motivation")
    st.success("Small progress every day leads to big results!")

# Subjects page
elif menu == "Subjects":

    st.header("📖 Subject Management")

    st.subheader("Add New Subject")

    subject = st.text_input(
        "Enter Subject Name",
        placeholder="Example: Python Programming"
    )

    if st.button("➕ Add Subject"):

        if subject.strip() == "":
            st.warning("Please enter a subject name.")

        else:
            try:
                cursor.execute(
                    "INSERT INTO subjects (subject_name) VALUES (?)",
                    (subject.strip(),)
                )

                conn.commit()

                st.success("Subject added successfully!")

            except sqlite3.IntegrityError:
                st.warning("This subject already exists.")

    st.divider()

    st.subheader("📚 My Subjects")

    cursor.execute(
        "SELECT id, subject_name FROM subjects ORDER BY id"
    )

    subjects = cursor.fetchall()

    if subjects:

        for subject_id, subject_name in subjects:

            st.write(f"📘 {subject_name}")

        st.divider()

        st.subheader("Delete Subject")

        subject_options = {
            name: subject_id
            for subject_id, name in subjects
        }

        selected_subject = st.selectbox(
            "Select a subject to delete",
            list(subject_options.keys())
        )

        if st.button("🗑️ Delete Subject"):

            cursor.execute(
                "DELETE FROM subjects WHERE id = ?",
                (subject_options[selected_subject],)
            )

            conn.commit()

            st.success("Subject deleted successfully!")

            st.rerun()

    else:
        st.info("No subjects added yet. Add your first subject!")

# Timetable page
elif menu == "Timetable":

    st.header("📅 Study Timetable")
    st.info("Timetable feature will be developed in the next lesson.")

# Tasks page
elif menu == "Tasks":

    st.header("📅 Study Timetable")

st.subheader("Add Your Study Schedule")

day = st.selectbox(
    "Select Day",
    ["Monday", "Tuesday", "Wednesday", "Thursday",
     "Friday", "Saturday", "Sunday"]
)

subject = st.text_input("Enter Subject")

time = st.time_input("Select Study Time")

if st.button("Add to Timetable"):
    if subject:
        st.success(f"{subject} added for {day} at {time}")
    else:
        st.warning("Please enter a subject name.")
# Close database connection
conn.close()
