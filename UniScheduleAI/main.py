from data_loader import (
    load_teacher_availability,
    load_student_groups,
    load_courses,
    build_time_slots,
    load_group_constraints,
    show_friendly_data,
    show_summary,
    save_clean_teachers,
    save_clean_student_groups,
    save_clean_courses,
    save_clean_time_slots,
    save_clean_group_constraints
)

from validation import validate_missing_teachers

def run_teachers():
    availability = load_teacher_availability()

    print("\n--- CLEAN TEACHER AVAILABILITY ---")
    show_friendly_data(availability, rows=50)

    print("\n--- SUMMARY BY TIME SLOT AND DAY ---")
    show_summary(availability)

    save_clean_teachers(availability)

    print("\nTeachers step finished.")

    return availability


def run_time_slots():
    time_slots = build_time_slots()

    print("\n--- TIME SLOTS ---")
    show_friendly_data(time_slots, rows=50)

    save_clean_time_slots(time_slots)

    print("\nTime slots step finished.")

    return time_slots


def run_group_constraints():
    group_constraints = load_group_constraints()

    print("\n--- GROUP CONSTRAINTS ---")
    show_friendly_data(group_constraints, rows=50)

    save_clean_group_constraints(group_constraints)

    print("\nGroup constraints step finished.")

    return group_constraints


def run_student_groups():
    student_groups = load_student_groups()

    print("\n--- STUDENT GROUPS COURSES ---")
    show_friendly_data(student_groups, rows=150)

    save_clean_student_groups(student_groups)

    print("\nStudent groups step finished.")

    return student_groups


def run_courses():
    courses = load_courses()

    print("\n--- CLEAN COURSES ---")
    show_friendly_data(courses, rows=150)

    save_clean_courses(courses)

    print("\nCourses step finished.")

    return courses


def run_all():
    print("\n==============================")
    print("STARTING DATA PREPARATION")
    print("==============================")

    availability = run_teachers()
    time_slots = run_time_slots()
    group_constraints = run_group_constraints()
    student_groups = run_student_groups()
    courses = run_courses()

    print("\n==============================")
    print("ALL STEPS FINISHED")
    print("==============================")

    return availability, time_slots, group_constraints, student_groups, courses


def run_validations():
    """
    Runs data validation checks.
    """

    courses = load_courses()

    print("\n==============================")
    print("STARTING DATA VALIDATION")
    print("==============================")

    missing_teachers = validate_missing_teachers(courses)

    print("\n==============================")
    print("DATA VALIDATION FINISHED")
    print("==============================")

    return missing_teachers

if __name__ == "__main__":
    # run_all()
    run_validations()






















