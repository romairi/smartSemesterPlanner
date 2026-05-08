def validate_missing_teachers(courses):
    """
    Checks courses that do not have a valid teacher.

    Input:
    courses DataFrame from load_courses()

    Returns:
    DataFrame with problematic courses
    """

    missing_values = ["", "?", "??", "nan", "None", "NaN"]

    missing_teachers = courses[
        (courses["teacher"].astype(str).str.strip().isin(missing_values)) |
        (courses["teacher_missing"] == True)
    ].copy()

    print("\n--- VALIDATION: COURSES WITH MISSING TEACHERS ---")

    if missing_teachers.empty:
        print("No courses with missing teachers found.")
    else:
        print(
            missing_teachers[
                [
                    "course_instance_id",
                    "student_group",
                    "course_name",
                    "section_number",
                    "teacher",
                    "teacher_name",
                    "source_sheet"
                ]
            ].to_string(index=False)
        )

        print(f"\nTotal courses with missing teachers: {len(missing_teachers)}")

    return missing_teachers