import pandas as pd


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


def prepare_courses_for_solver(courses):
    """
    Prepares courses for the first solver version.

    1. Excludes placeholder courses such as:
       קורסי בחירה / בחירה

    2. Adds temporary mock teachers for missing teachers.

    Returns:
    clean courses DataFrame ready for solver
    """

    courses = courses.copy()

    # 1. Exclude placeholder courses
    placeholder_courses = [
        "קורסי בחירה",
        "בחירה"
    ]

    courses["exclude_from_solver"] = courses["course_name"].isin(placeholder_courses)

    # 2. Mock teachers for real courses with missing teachers
    mock_teachers = {
        "CI0025": {
            "teacher": "301289393",
            "teacher_name": "MOCK - עדי מרינוב"
        },
        "CI0056": {
            "teacher": "33869389",
            "teacher_name": "MOCK - יוגב שני"
        },
        "CI0057": {
            "teacher": "33869389",
            "teacher_name": "MOCK - יוגב שני"
        }
    }

    for course_instance_id, mock_data in mock_teachers.items():
        mask = courses["course_instance_id"] == course_instance_id

        courses.loc[mask, "teacher"] = mock_data["teacher"]
        courses.loc[mask, "teacher_name"] = mock_data["teacher_name"]
        courses.loc[mask, "teacher_missing"] = False

    # 3. Keep only courses that should go into solver
    courses_ready = courses[courses["exclude_from_solver"] == False].copy()

    return courses_ready


def save_courses_ready_for_solver(courses_ready, data_dir):
    """
    Saves courses ready for solver.
    """

    output_file = data_dir / "courses_ready_for_solver.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        courses_ready.to_excel(
            writer,
            sheet_name="CoursesReadyForSolver",
            index=False
        )

    print(f"\nSaved courses ready for solver to: {output_file}")



def validate_teacher_availability(courses_ready, availability):
    """
    Checks if every teacher from courses_ready exists in teacher availability.

    Input:
    courses_ready - DataFrame from prepare_courses_for_solver()
    availability - DataFrame from load_teacher_availability()

    Returns:
    DataFrame with courses whose teachers do not have availability
    """

    courses_ready = courses_ready.copy()
    availability = availability.copy()

    courses_ready["teacher"] = courses_ready["teacher"].astype(str).str.strip()
    availability["teacher"] = availability["teacher"].astype(str).str.strip()

    course_teachers = set(courses_ready["teacher"].dropna())
    available_teachers = set(availability["teacher"].dropna())

    missing_teachers = course_teachers - available_teachers

    missing_teachers = {
        teacher for teacher in missing_teachers
        if teacher not in ["", "?", "??", "nan", "None", "NaN"]
    }

    courses_without_availability = courses_ready[
        courses_ready["teacher"].isin(missing_teachers)
    ].copy()

    print("\n--- VALIDATION: TEACHERS WITHOUT AVAILABILITY ---")

    if courses_without_availability.empty:
        print("All course teachers have availability.")
    else:
        print(
            courses_without_availability[
                [
                    "teacher",
                    "teacher_name",
                    "course_instance_id",
                    "student_group",
                    "course_name"
                ]
            ].to_string(index=False)
        )

        print(
            f"\nTotal courses with teachers without availability: "
            f"{len(courses_without_availability)}"
        )

    return courses_without_availability


def prepare_availability_for_solver(courses_ready, availability):
    """
    Prepares teacher availability for the first solver version.

    If a teacher exists in courses_ready but does not exist in availability,
    we add MOCK availability for all days and all official teacher time blocks.

    This allows us to continue developing the solver,
    but later these mock rows should be replaced with real teacher constraints.
    """

    courses_ready = courses_ready.copy()
    availability = availability.copy()

    courses_ready["teacher"] = courses_ready["teacher"].astype(str).str.strip()
    availability["teacher"] = availability["teacher"].astype(str).str.strip()

    course_teachers = set(courses_ready["teacher"].dropna())
    available_teachers = set(availability["teacher"].dropna())

    missing_teachers = course_teachers - available_teachers

    missing_teachers = {
        teacher for teacher in missing_teachers
        if teacher not in ["", "?", "??", "nan", "None", "NaN"]
    }

    # Add marker to real availability
    availability["is_mock_availability"] = False

    if not missing_teachers:
        print("\nNo mock availability needed.")
        return availability

    # Get teacher names from courses_ready
    teacher_names = (
        courses_ready[["teacher", "teacher_name"]]
        .drop_duplicates()
        .set_index("teacher")["teacher_name"]
        .to_dict()
    )

    # Use existing days and time blocks from real availability
    days = sorted(availability["day"].dropna().unique().tolist())
    time_slots = sorted(availability["time_slot"].dropna().unique().tolist())

    mock_records = []

    for teacher in sorted(missing_teachers):
        teacher_name = teacher_names.get(teacher, "")

        for day in days:
            for time_slot in time_slots:
                mock_records.append({
                    "time_slot": time_slot,
                    "day": day,
                    "teacher": teacher,
                    "notes": f"MOCK availability for {teacher_name}",
                    "is_mock_availability": True
                })

    mock_availability = pd.DataFrame(mock_records)

    availability_ready = pd.concat(
        [availability, mock_availability],
        ignore_index=True
    )

    print("\n--- MOCK AVAILABILITY ADDED ---")
    print(f"Teachers with mock availability: {len(missing_teachers)}")
    print(f"Mock availability rows added: {len(mock_availability)}")

    return availability_ready


def save_availability_ready_for_solver(availability_ready, data_dir):
    """
    Saves availability ready for solver.
    """

    output_file = data_dir / "availability_ready_for_solver.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        availability_ready.to_excel(
            writer,
            sheet_name="AvailabilityReadyForSolver",
            index=False
        )

    print(f"\nSaved availability ready for solver to: {output_file}")



def expand_availability_to_hourly_slots(availability_ready, time_slots):
    """
    Converts teacher availability from large time blocks
    into official hourly time slots.

    Example:
    10:00-12:00
    becomes:
    10:00-11:00
    11:00-12:00

    It only keeps slots that exist in time_slots_clean.
    """

    availability_ready = availability_ready.copy()
    time_slots = time_slots.copy()

    records = []

    for _, row in availability_ready.iterrows():
        teacher = str(row["teacher"]).strip()
        day = str(row["day"]).strip()
        block = str(row["time_slot"]).strip()
        notes = row.get("notes", "")
        is_mock_availability = row.get("is_mock_availability", False)

        if "-" not in block:
            continue

        block_start, block_end = block.split("-")
        block_start = block_start.strip()
        block_end = block_end.strip()

        for _, slot in time_slots.iterrows():
            slot_id = slot["slot_id"]
            slot_time = slot["time_slot"]
            slot_start = slot["start_time"]
            slot_end = slot["end_time"]
            slot_order = slot["slot_order"]
            slot_type = slot["slot_type"]

            # Keep only hourly slots inside the teacher availability block
            if slot_start >= block_start and slot_end <= block_end:
                records.append({
                    "teacher": teacher,
                    "day": day,
                    "slot_id": slot_id,
                    "time_slot": slot_time,
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "slot_order": slot_order,
                    "slot_type": slot_type,
                    "notes": notes,
                    "is_mock_availability": is_mock_availability
                })

    hourly_availability = pd.DataFrame(records)

    hourly_availability = hourly_availability.drop_duplicates(
        subset=["teacher", "day", "slot_id"]
    ).reset_index(drop=True)

    return hourly_availability


def save_hourly_availability_for_solver(hourly_availability, data_dir):
    """
    Saves hourly teacher availability for solver.
    """

    output_file = data_dir / "availability_hourly_for_solver.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        hourly_availability.to_excel(
            writer,
            sheet_name="AvailabilityHourly",
            index=False
        )

    print(f"\nSaved hourly availability for solver to: {output_file}")