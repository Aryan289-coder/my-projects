"""
STEP 4 — View Attendance Reports
===================================
Reads all CSV files from attendance_records/ and
generates a full summary report.

Usage:
    python 04_view_report.py

Options shown in interactive menu:
    1. Full attendance table (all lectures)
    2. Per-student summary (total lectures attended)
    3. Per-lecture summary (who was present)
    4. Absentees for a specific lecture
    5. Export summary to Excel
"""

import os
import sys
import glob

try:
    import pandas as pd
except ImportError:
    print("❌ pandas not installed. Run: pip install pandas openpyxl")
    sys.exit(1)


ATTENDANCE_FOLDER = "attendance_records"


def load_all_records():
    """Load all CSV attendance files into a single DataFrame."""
    pattern = os.path.join(ATTENDANCE_FOLDER, "*.csv")
    files = glob.glob(pattern)

    if not files:
        print(f"❌ No attendance records found in '{ATTENDANCE_FOLDER}/'")
        print("   Run 03_take_attendance.py first to create records.")
        sys.exit(1)

    dfs = []
    for filepath in sorted(files):
        try:
            df = pd.read_csv(filepath)
            # Extract lecture and date from filename
            basename = os.path.basename(filepath).replace(".csv", "")
            parts = basename.rsplit("_", 1)
            lecture_id = parts[0] if len(parts) >= 1 else basename
            date = parts[1] if len(parts) == 2 else "Unknown"
            df["Lecture"] = lecture_id.replace("_", " ")
            df["Date"] = date
            df["File"] = basename
            dfs.append(df)
        except Exception as e:
            print(f"   ⚠ Skipping {filepath}: {e}")

    if not dfs:
        print("❌ No valid CSV files found.")
        sys.exit(1)

    combined = pd.concat(dfs, ignore_index=True)
    combined.columns = combined.columns.str.strip()
    return combined, files


def print_separator(char="─", width=60):
    print(char * width)


def show_full_table(df):
    """Show all attendance records."""
    print_separator()
    print("  📋 FULL ATTENDANCE TABLE")
    print_separator()
    display = df[["Student Name", "Lecture", "Date", "Time Detected", "Status"]].copy()
    display = display.sort_values(["Date", "Lecture", "Student Name"])
    print(display.to_string(index=False))
    print_separator()
    print(f"  Total records: {len(df)}")


def show_student_summary(df):
    """Show per-student attendance count and percentage."""
    print_separator()
    print("  👤 STUDENT ATTENDANCE SUMMARY")
    print_separator()

    total_lectures = df["File"].nunique()
    summary = df.groupby("Student Name")["File"].nunique().reset_index()
    summary.columns = ["Student Name", "Lectures Attended"]
    summary["Total Lectures"] = total_lectures
    summary["Attendance %"] = (summary["Lectures Attended"] / total_lectures * 100).round(1)
    summary = summary.sort_values("Attendance %", ascending=False)

    # Add visual bar
    def bar(pct):
        filled = int(pct / 10)
        return "█" * filled + "░" * (10 - filled)

    summary["Progress"] = summary["Attendance %"].apply(bar)

    print(f"\n  Total lectures held: {total_lectures}\n")
    for _, row in summary.iterrows():
        status = "✅" if row["Attendance %"] >= 75 else "⚠️ " if row["Attendance %"] >= 50 else "❌"
        print(f"  {status}  {row['Student Name']:<25} {row['Lectures Attended']}/{row['Total Lectures']}  "
              f"{row['Progress']}  {row['Attendance %']}%")

    print_separator()
    print(f"  ✅ = 75%+ attendance  |  ⚠️  = 50-75%  |  ❌ = below 50%")


def show_lecture_summary(df):
    """Show per-lecture attendance count."""
    print_separator()
    print("  📅 LECTURE-WISE ATTENDANCE")
    print_separator()

    summary = df.groupby(["Lecture", "Date"])["Student Name"].count().reset_index()
    summary.columns = ["Lecture", "Date", "Students Present"]
    summary = summary.sort_values(["Date", "Lecture"])

    print(summary.to_string(index=False))
    print_separator()


def show_absentees(df):
    """Show who was absent for a chosen lecture."""
    print_separator()
    print("  ❌ CHECK ABSENTEES FOR A LECTURE")
    print_separator()

    lectures = df["File"].unique()
    print("\n  Available lectures:")
    for i, lec in enumerate(sorted(lectures), 1):
        print(f"    {i}. {lec}")

    try:
        choice = int(input("\n  Enter lecture number: ").strip()) - 1
        chosen = sorted(lectures)[choice]
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return

    # All registered students (ever seen in any lecture)
    all_students = set(df["Student Name"].unique())

    # Students present in chosen lecture
    present = set(df[df["File"] == chosen]["Student Name"].unique())

    absent = all_students - present

    print(f"\n  Lecture: {chosen}")
    print(f"  Present : {len(present)}  |  Absent: {len(absent)}\n")

    if present:
        print("  ✅ PRESENT:")
        for s in sorted(present):
            print(f"     - {s}")

    if absent:
        print("\n  ❌ ABSENT:")
        for s in sorted(absent):
            print(f"     - {s}")
    else:
        print("\n  🎉 All students were present!")

    print_separator()


def export_to_excel(df):
    """Export full report to Excel with multiple sheets."""
    try:
        import openpyxl
    except ImportError:
        print("❌ openpyxl not installed. Run: pip install openpyxl")
        return

    output_file = "attendance_report.xlsx"

    total_lectures = df["File"].nunique()
    summary = df.groupby("Student Name")["File"].nunique().reset_index()
    summary.columns = ["Student Name", "Lectures Attended"]
    summary["Total Lectures"] = total_lectures
    summary["Attendance %"] = (summary["Lectures Attended"] / total_lectures * 100).round(1)
    summary["Status"] = summary["Attendance %"].apply(
        lambda x: "✅ Good" if x >= 75 else ("⚠️ Warning" if x >= 50 else "❌ Low")
    )

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Sheet 1: All records
        df[["Student Name", "Lecture", "Date", "Time Detected", "Status"]].to_excel(
            writer, sheet_name="All Records", index=False
        )
        # Sheet 2: Student summary
        summary.to_excel(writer, sheet_name="Student Summary", index=False)

        # Sheet 3: Lecture pivot
        pivot = df.pivot_table(
            index="Student Name",
            columns="Lecture",
            values="Status",
            aggfunc=lambda x: "Present",
            fill_value="Absent"
        )
        pivot.to_excel(writer, sheet_name="Attendance Matrix")

    print(f"\n  ✅ Exported to: {output_file}")
    print(f"     Sheets: 'All Records', 'Student Summary', 'Attendance Matrix'")


def main():
    print("\n" + "=" * 60)
    print("   📊 ATTENDANCE REPORT VIEWER")
    print("=" * 60)

    df, files = load_all_records()
    print(f"\n✅ Loaded {len(files)} lecture file(s) — {len(df)} total records")

    while True:
        print("\n  What would you like to see?")
        print("  1. Full attendance table")
        print("  2. Per-student summary (with attendance %)")
        print("  3. Per-lecture summary")
        print("  4. Absentees for a specific lecture")
        print("  5. Export full report to Excel")
        print("  0. Exit")

        choice = input("\n  Enter choice: ").strip()

        if choice == "1":
            show_full_table(df)
        elif choice == "2":
            show_student_summary(df)
        elif choice == "3":
            show_lecture_summary(df)
        elif choice == "4":
            show_absentees(df)
        elif choice == "5":
            export_to_excel(df)
        elif choice == "0":
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("  ❌ Invalid choice. Please enter 0-5.")


if __name__ == "__main__":
    main()
