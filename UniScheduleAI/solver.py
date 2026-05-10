import pandas as pd


def day_allowed_for_group(student_group, day, group_constraints):
    """
    Checks if a student group is allowed to study on this day
    according to group constraints.

    If there is no constraint for this group, all days are allowed.
    """

    constraints = group_constraints[
        group_constraints["student_group"].astype(str).str.strip() == str(student_group).strip()
    ]

    if constraints.empty:
        return True

    for _, row in constraints.iterrows():
        allowed_days = str(row["allowed_days"]).replace(" ", "").split(",")

        if day in allowed_days:
            return True

    return False


def build_simple_schedule(courses_ready, hourly_availability, group_constraints):
    """
    First simple scheduler.

    For each course:
    - finds teacher availability
    - checks student group is free
    - checks teacher is free
    - checks group constraints
    - assigns first possible slot
    """

    schedule = []

    teacher_busy = set()
    group_busy = set()

    for _, course in courses_ready.iterrows():
        course_instance_id = course["course_instance_id"]
        student_group = course["student_group"]
        course_name = course["course_name"]
        section_number = course["section_number"]
        teacher = str(course["teacher"]).strip()
        teacher_name = course["teacher_name"]

        possible_slots = hourly_availability[
            hourly_availability["teacher"].astype(str).str.strip() == teacher
        ].copy()

        possible_slots = possible_slots.sort_values(
            by=["day", "slot_order"]
        )

        assigned = False

        for _, slot in possible_slots.iterrows():
            day = slot["day"]
            slot_id = slot["slot_id"]
            time_slot = slot["time_slot"]
            slot_order = slot["slot_order"]
            slot_type = slot["slot_type"]
            is_mock_availability = slot.get("is_mock_availability", False)

            if not day_allowed_for_group(student_group, day, group_constraints):
                continue

            teacher_key = (teacher, day, slot_id)
            group_key = (student_group, day, slot_id)

            if teacher_key in teacher_busy:
                continue

            if group_key in group_busy:
                continue

            schedule.append({
                "course_instance_id": course_instance_id,
                "student_group": student_group,
                "course_name": course_name,
                "section_number": section_number,
                "teacher": teacher,
                "teacher_name": teacher_name,
                "day": day,
                "slot_id": slot_id,
                "time_slot": time_slot,
                "slot_order": slot_order,
                "slot_type": slot_type,
                "status": "scheduled",
                "is_mock_availability": is_mock_availability
            })

            teacher_busy.add(teacher_key)
            group_busy.add(group_key)

            assigned = True
            break

        if not assigned:
            schedule.append({
                "course_instance_id": course_instance_id,
                "student_group": student_group,
                "course_name": course_name,
                "section_number": section_number,
                "teacher": teacher,
                "teacher_name": teacher_name,
                "day": "",
                "slot_id": "",
                "time_slot": "",
                "slot_order": "",
                "slot_type": "",
                "status": "not_scheduled",
                "is_mock_availability": ""
            })

    return pd.DataFrame(schedule)


def save_generated_schedule(schedule, data_dir):
    """
    Saves generated schedule to Excel.
    """

    output_file = data_dir / "generated_schedule.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        schedule.to_excel(
            writer,
            sheet_name="GeneratedSchedule",
            index=False
        )

    print(f"\nSaved generated schedule to: {output_file}")