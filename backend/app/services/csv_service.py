import csv
import io

def rows_to_csv(rows):
    out = io.StringIO()
    writer = csv.writer(out)
    headers = ["Student"] + [f"Date {i}" for i in range(1, 13)] + ["Present", "Absent", "Leave", "Scheduled", "Attendance %"]
    writer.writerow(headers)
    for r in rows:
        statuses = list(r.get("date_statuses") or r.get("statuses") or [])
        statuses = (statuses + [""] * 12)[:12]
        total = int(r.get("total", 0) or 0)
        present = int(r.get("present", 0) or 0)
        absent = int(r.get("absent", 0) or 0)
        leave = int(r.get("leave", 0) or 0)
        pct = round((present / total) * 100, 1) if total else 0
        writer.writerow([r.get("student", ""), *statuses, present, absent, leave, total, pct])
    return out.getvalue()
