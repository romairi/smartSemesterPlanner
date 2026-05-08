from data_loader import (
    load_teacher_availability,
    load_student_groups,
    load_courses,
    show_friendly_data,
    show_summary,
    save_clean_teachers,
    save_clean_courses,
    build_time_slots,
    save_clean_time_slots
)


def run_teachers():
    """
    Reads Teachers.xlsx, shows teacher availability,
    shows summary, and saves teachers_clean.xlsx
    """

    availability = load_teacher_availability()

    print("\n--- CLEAN TEACHER AVAILABILITY ---")
    show_friendly_data(availability, rows=50)

    print("\n--- SUMMARY BY TIME SLOT AND DAY ---")
    show_summary(availability)

    save_clean_teachers(availability)

    print("\nTeachers step finished.")

    return availability


def run_student_groups():
    """
    Reads StudentGroups.xlsx Sheet2
    and shows student groups with their courses.
    """

    student_groups = load_student_groups()

    print("\n--- STUDENT GROUPS COURSES ---")
    show_friendly_data(student_groups, rows=150)

    print("\nStudent groups step finished.")

    return student_groups


def run_courses():
    """
    Reads Courses.xlsx,
    creates clean courses table,
    and saves courses_clean.xlsx.
    """

    courses = load_courses()

    print("\n--- CLEAN COURSES ---")
    show_friendly_data(courses, rows=150)

    save_clean_courses(courses)

    print("\nCourses step finished.")

    return courses


def run_time_slots():
    """
    Creates official hourly time slots
    and saves time_slots_clean.xlsx.
    """

    time_slots = build_time_slots()

    print("\n--- TIME SLOTS ---")
    show_friendly_data(time_slots, rows=50)

    save_clean_time_slots(time_slots)

    print("\nTime slots step finished.")

    return time_slots


def run_all():
    """
    Runs all preparation steps.
    """

    print("\n==============================")
    print("STARTING DATA PREPARATION")
    print("==============================")

    availability = run_teachers()
    time_slots = run_time_slots()
    student_groups = run_student_groups()
    courses = run_courses()

    print("\n==============================")
    print("ALL STEPS FINISHED")
    print("==============================")

    return availability, time_slots, student_groups, courses


if __name__ == "__main__":
    # run_all()
    run_time_slots()