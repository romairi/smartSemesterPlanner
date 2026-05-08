from data_loader import (
    load_teacher_availability,
    show_friendly_data,
    show_summary,
    save_clean_teachers
)

availability = load_teacher_availability()

print("\n--- CLEAN TEACHER AVAILABILITY ---")
show_friendly_data(availability, rows=100)

print("\n--- SUMMARY BY TIME SLOT AND DAY ---")
show_summary(availability)

save_clean_teachers(availability)

print("\nDone!")