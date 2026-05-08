from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
TEACHERS_FILE = DATA_DIR / "Teachers.xlsx"


def load_teacher_availability():
    raw = pd.read_excel(
        TEACHERS_FILE,
        sheet_name="לפי שעות",
        header=None
    )

    header_rows = raw[raw.iloc[:, 0] == "שעות אקדמיות"]

    if header_rows.empty:
        raise ValueError("Could not find header row with 'שעות אקדמיות'")

    header_row_index = header_rows.index[0]

    day_columns = raw.iloc[header_row_index, 1:7].tolist()

    df = raw.iloc[header_row_index + 1:, 0:8].copy()

    df.columns = ["time_slot"] + day_columns + ["notes"]

    df["time_slot"] = df["time_slot"].ffill()

    df = df.dropna(subset=day_columns, how="all")

    availability = df.melt(
        id_vars=["time_slot", "notes"],
        value_vars=day_columns,
        var_name="day",
        value_name="teacher"
    )

    availability = availability.dropna(subset=["teacher"])

    availability["teacher"] = (
        availability["teacher"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    availability = availability[availability["teacher"] != ""]

    availability["time_slot"] = availability["time_slot"].astype(str).str.strip()
    availability["day"] = availability["day"].astype(str).str.strip()

    availability = availability[["time_slot", "day", "teacher", "notes"]]

    availability = availability.sort_values(
        by=["time_slot", "day", "teacher"]
    ).reset_index(drop=True)

    return availability


def show_friendly_data(df, rows=100):
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 80)

    print(df.head(rows).to_string(index=False))


def show_summary(availability):
    summary = availability.pivot_table(
        index="time_slot",
        columns="day",
        values="teacher",
        aggfunc="count",
        fill_value=0
    )

    print(summary.to_string())


def save_clean_teachers(availability):
    output_file = DATA_DIR / "teachers_clean.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        availability.to_excel(
            writer,
            sheet_name="TeacherAvailability",
            index=False
        )

    print(f"\nSaved clean file to: {output_file}")



#########################################################################################


def load_student_groups():
    """
    Reads only Sheet2 from StudentGroups.xlsx.

    Converts this structure:

    group name
        course
        course
    group name
        course
        course

    into clean table:

    student_group | course_name
    """

    student_groups_file = DATA_DIR / "StudentGroups.xlsx"

    raw = pd.read_excel(
        student_groups_file,
        sheet_name="Sheet2",
        header=None
    )

    records = []
    current_group = None

    for _, row in raw.iterrows():
        first_col = row.iloc[0]
        second_col = row.iloc[1]

        # If first column has text, it is probably a student group
        if pd.notna(first_col):
            value = str(first_col).strip()

            # Skip title row
            if value and "קורסים" not in value:
                current_group = value

        # If second column has text, it is a course
        if pd.notna(second_col):
            course_name = str(second_col).strip()

            # Skip header row
            if course_name and course_name != "קורס" and current_group is not None:
                records.append({
                    "student_group": current_group,
                    "course_name": course_name
                })

    df = pd.DataFrame(records)

    # Clean spaces
    df["student_group"] = df["student_group"].astype(str).str.strip()
    df["course_name"] = df["course_name"].astype(str).str.strip()

    # Remove empty rows
    df = df[
        (df["student_group"] != "") &
        (df["course_name"] != "")
    ]

    # Add simple group_id
    df["group_id"] = df["student_group"].factorize()[0] + 1
    df["group_id"] = "G" + df["group_id"].astype(str).str.zfill(3)

    # Add simple course_id
    df["course_id"] = df["course_name"].factorize()[0] + 1
    df["course_id"] = "C" + df["course_id"].astype(str).str.zfill(3)

    # Better column order
    df = df[
        [
            "group_id",
            "student_group",
            "course_id",
            "course_name"
        ]
    ]

    return df

##############################################################################################################


def clean_value(value):
    """
    Cleans Excel cell value.
    Converts NaN to empty string and removes spaces.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace("\u200f", "")
    value = value.replace("\u200e", "")

    if value.endswith(".0"):
        value = value[:-2]

    return value


def load_teacher_names_from_courses_file():
    """
    Reads the first sheet:
    'שמות + תעודות זהות'

    Creates a table:
    teacher | teacher_name
    """

    courses_file = DATA_DIR / "Courses.xlsx"

    raw = pd.read_excel(
        courses_file,
        sheet_name=" שמות +תעודות זהות",
        header=None
    )

    records = []

    for _, row in raw.iterrows():
        teacher_name = clean_value(row.iloc[0])
        teacher_id = clean_value(row.iloc[1])

        if teacher_name in ["", "שם מלא"]:
            continue

        if teacher_id in ["", "תעודת זהות"]:
            continue

        records.append({
            "teacher": teacher_id,
            "teacher_name": teacher_name
        })

    return pd.DataFrame(records)


def clean_group_name(sheet_name):
    """
    Converts sheet name into a clean student group name.
    """

    group_name = sheet_name.strip()

    group_name = group_name.replace("-קורסים + תעודות זהות", "")
    group_name = group_name.replace("קורסים + תעודות זהות", "")
    group_name = group_name.replace("- קורסים + תז", "")
    group_name = group_name.replace("- קורסים + תעודות זהות", "")
    group_name = group_name.replace("קורסים + תז", "")

    group_name = group_name.strip()

    return group_name


def load_courses():
    """
    Reads all group sheets from Courses.xlsx.

    Skips:
    - שמות + תעודות זהות
    - מרצים + ש״ס

    Output:
    student_group | course_name | teacher | teacher_name | section_number
    """

    courses_file = DATA_DIR / "Courses.xlsx"

    excel_file = pd.ExcelFile(courses_file)

    skip_sheets = [
        "שמות",
        "מרצים"
    ]

    teacher_names = load_teacher_names_from_courses_file()

    records = []

    for sheet_name in excel_file.sheet_names:
        clean_sheet_name = sheet_name.strip()

        # Skip non-group sheets
        if any(skip_word in clean_sheet_name for skip_word in skip_sheets):
            continue

        student_group = clean_group_name(clean_sheet_name)

        raw = pd.read_excel(
            courses_file,
            sheet_name=sheet_name,
            header=None
        )

        for _, row in raw.iterrows():
            course_name = clean_value(row.iloc[0])
            teacher = clean_value(row.iloc[1]) if len(row) > 1 else ""
            extra_note = clean_value(row.iloc[2]) if len(row) > 2 else ""

            # Skip header row
            if course_name in ["", "קורס"]:
                continue

            if teacher in ["מרצה", "מרצה "]:
                continue

            records.append({
                "student_group": student_group,
                "course_name": course_name,
                "teacher": teacher,
                "extra_note": extra_note,
                "source_sheet": sheet_name
            })

    courses = pd.DataFrame(records)

    # Mark missing teacher
    courses["teacher_missing"] = courses["teacher"].isin(["", "?", "nan"])

    # Add teacher names when possible
    courses = courses.merge(
        teacher_names,
        on="teacher",
        how="left"
    )

    courses["teacher_name"] = courses["teacher_name"].fillna("")

    # Add section number for duplicated courses inside same student group
    courses["section_number"] = (
        courses
        .groupby(["student_group", "course_name"])
        .cumcount() + 1
    )

    # Technical unique id for every course section
    courses["course_instance_id"] = (
        "CI" + (courses.index + 1).astype(str).str.zfill(4)
    )

    courses = courses[
        [
            "course_instance_id",
            "student_group",
            "course_name",
            "section_number",
            "teacher",
            "teacher_name",
            "teacher_missing",
            "extra_note",
            "source_sheet"
        ]
    ]

    return courses


def save_clean_courses(courses):
    """
    Saves clean courses table.
    """

    output_file = DATA_DIR / "courses_clean.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        courses.to_excel(
            writer,
            sheet_name="CoursesClean",
            index=False
        )

    print(f"\nSaved clean courses file to: {output_file}")


###############################################################################

def get_slot_type_by_hour(hour):
    """
    Defines slot type by start hour.
    """

    if hour < 12:
        return "morning"

    if hour < 14:
        return "noon"

    if hour < 18:
        return "afternoon"

    return "evening"


def build_time_slots():
    """
    Builds official hourly time slots based on the real schedule format.

    Output:
    slot_id | time_slot | start_time | end_time | slot_order | slot_type
    """

    records = []

    start_hour = 9
    end_hour = 22

    slot_order = 1

    for hour in range(start_hour, end_hour):
        start_time = f"{hour:02d}:00"
        end_time = f"{hour + 1:02d}:00"
        time_slot = f"{start_time}-{end_time}"

        records.append({
            "slot_id": f"S{slot_order:03d}",
            "time_slot": time_slot,
            "start_time": start_time,
            "end_time": end_time,
            "slot_order": slot_order,
            "slot_type": get_slot_type_by_hour(hour)
        })

        slot_order += 1

    return pd.DataFrame(records)


def save_clean_time_slots(time_slots):
    """
    Saves clean time slots table.
    """

    output_file = DATA_DIR / "time_slots_clean.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        time_slots.to_excel(
            writer,
            sheet_name="TimeSlotsClean",
            index=False
        )

    print(f"\nSaved clean time slots file to: {output_file}")



