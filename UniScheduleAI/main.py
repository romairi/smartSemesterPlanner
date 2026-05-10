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

from validation import (
    validate_missing_teachers,
    prepare_courses_for_solver,
    save_courses_ready_for_solver,
    validate_teacher_availability, prepare_availability_for_solver, save_availability_ready_for_solver,
    expand_availability_to_hourly_slots, save_hourly_availability_for_solver
)

from data_loader import DATA_DIR

from solver import build_simple_schedule, save_generated_schedule


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
    Runs data validation checks and prepares files for the first solver.
    """

    courses = load_courses()
    availability = load_teacher_availability()
    time_slots = build_time_slots()

    print("\n==============================")
    print("STARTING DATA VALIDATION")
    print("==============================")

    missing_teachers = validate_missing_teachers(courses)

    courses_ready = prepare_courses_for_solver(courses)

    print("\n--- COURSES READY FOR SOLVER ---")
    show_friendly_data(courses_ready, rows=150)

    save_courses_ready_for_solver(courses_ready, DATA_DIR)

    teachers_without_availability = validate_teacher_availability(
        courses_ready,
        availability
    )

    availability_ready = prepare_availability_for_solver(
        courses_ready,
        availability
    )

    print("\n--- AVAILABILITY READY FOR SOLVER ---")
    show_friendly_data(availability_ready, rows=150)

    save_availability_ready_for_solver(availability_ready, DATA_DIR)

    hourly_availability = expand_availability_to_hourly_slots(
        availability_ready,
        time_slots
    )

    print("\n--- HOURLY AVAILABILITY FOR SOLVER ---")
    show_friendly_data(hourly_availability, rows=150)

    save_hourly_availability_for_solver(hourly_availability, DATA_DIR)

    print("\n==============================")
    print("DATA VALIDATION FINISHED")
    print("==============================")

    return (
        missing_teachers,
        courses_ready,
        teachers_without_availability,
        availability_ready,
        hourly_availability
    )


def run_solver():
    """
    Runs first simple schedule solver.
    """

    courses = load_courses()
    availability = load_teacher_availability()
    time_slots = build_time_slots()
    group_constraints = load_group_constraints()

    # Prepare courses for solver
    courses_ready = prepare_courses_for_solver(courses)

    # Prepare availability with mocks
    availability_ready = prepare_availability_for_solver(
        courses_ready,
        availability
    )

    # Convert availability to hourly slots
    hourly_availability = expand_availability_to_hourly_slots(
        availability_ready,
        time_slots
    )

    # Build schedule
    schedule = build_simple_schedule(
        courses_ready,
        hourly_availability,
        group_constraints
    )

    print("\n--- GENERATED SCHEDULE ---")
    show_friendly_data(schedule, rows=200)

    save_generated_schedule(schedule, DATA_DIR)

    print("\nSolver step finished.")

    return schedule



if __name__ == "__main__":
    # run_all()
    # run_validations()
    run_solver()