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
