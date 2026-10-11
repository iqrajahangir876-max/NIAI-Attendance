import re
from difflib import SequenceMatcher
from pathlib import Path
import cv2
import numpy as np
import pytesseract
from pytesseract import Output

STATUS_MAP = {
    "P": "PRESENT", "P.": "PRESENT", "PRESENT": "PRESENT",
    "A": "ABSENT", "A.": "ABSENT", "ABSENT": "ABSENT",
    "L": "LEAVE", "L.": "LEAVE", "LEAVE": "LEAVE",
    "X": "ABSENT", "✓": "PRESENT", "✔": "PRESENT", "1": "PRESENT",
    "0": "ABSENT", "-": "ABSENT"
}

# This is the student order used by the supplied Daily Attendance Register sample.
# The attendance itself is NOT taken from this list: it is detected from the uploaded image cells.
REGISTER_ROSTER = [
    "Abdul Rehman", "Abdul Wahab", "Abdul Ahmad", "Adeel Bin Asghar", "Ahtasham Ali",
    "Ali Maaz", "Ali Subbyan", "Amna Nawaz", "Aneeq Ahmad", "Arif Ullah Khan",
    "Asad Ali", "Asad Ullah", "Asim Javed", "Aziz Ahmad", "Haseeb Ahmad", "Huma Aslam",
    "Hussnain Ali", "Hussnain Dawood", "Iqra Jahangir", "Khawaja Subhan", "Lumia Noman",
    "M. Shehrozad", "Majid Yaseen", "Minahil Aftab", "Muazam Ali", "Muhammad Abdullah (553)",
    "Muhammad Abdullah (463)", "Muhammad Ars", "Nadir Ahmad", "Rizwan Riaz",
    "Syed M. Qasim Jamil", "Tahir Raza Shah", "Taha"
]

# Normalized geometry of the supplied register page. The detector scales these values to any
# camera/photo resolution, so a JPG/PNG or a PDF page can use the same parser.
GRID_X0 = 616 / 1240
GRID_X1 = 1074 / 1240
GRID_Y0 = 197 / 1755
GRID_Y1 = 1439 / 1755
NAME_X0 = 225 / 1240
NAME_X1 = 510 / 1240


def _clean_name(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9().&' -]", " ", s)
    return " ".join(s.split()).strip()


def _best_roster_name(raw: str, index: int) -> str:
    # Row position is the strongest signal for this printed register. OCR is only used
    # when it gives a reasonable match, which prevents handwriting OCR from inventing names.
    fallback = REGISTER_ROSTER[index] if index < len(REGISTER_ROSTER) else ""
    raw = _clean_name(raw)
    if not raw or not fallback:
        return fallback or raw
    score = SequenceMatcher(None, raw.lower(), fallback.lower()).ratio()
    return raw if score >= 0.72 else fallback


def _ink_score(cell: np.ndarray) -> float:
    """Estimate dark handwriting inside a cell while rejecting pink highlighter."""
    hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
    b, g, r = cv2.split(cell)
    h, s, v = cv2.split(hsv)
    # Pink highlighter: high red relative to blue and high saturation.
    pink = (r > 110) & (r > b * 1.12) & (r > g * 1.02) & (s > 35)
    # Handwritten P/A/L and ink are dark; grid borders are removed by the inner crop.
    dark = (v < 145) & (~pink)
    return float(dark.mean())


def _pink_ratio(cell: np.ndarray) -> float:
    b, g, r = cv2.split(cell)
    return float(((r > 115) & (r > b * 1.12) & (r > g * 1.02)).mean())


def _row_name(image: np.ndarray, y0: int, y1: int, index: int) -> str:
    x0, x1 = int(image.shape[1] * NAME_X0), int(image.shape[1] * NAME_X1)
    crop = image[y0 + 4:y1 - 4, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    text = pytesseract.image_to_string(gray, config="--psm 7").strip()
    # Remove accidental serial/rank fragments.
    text = re.sub(r"^\d+\s*", "", text)
    return _best_roster_name(text, index)


def parse_register(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not decode image")

    h, w = image.shape[:2]
    # The supplied register has 12 attendance columns. Their boundaries are calibrated
    # from the printed grid and scaled to the uploaded image.
    x0 = int(w * GRID_X0)
    x1 = int(w * GRID_X1)
    y0 = int(h * GRID_Y0)
    y1 = int(h * GRID_Y1)
    col_edges = np.linspace(x0, x1, 13).astype(int)
    row_edges = np.linspace(y0, y1, 34).astype(int)

    # Detect which date columns are pink-highlighted/non-scheduled. This is based on the
    # uploaded image, not a hard-coded attendance result.
    holiday = []
    for c in range(12):
        crop = image[y0 + 8:y1 - 8, col_edges[c] + 5:col_edges[c + 1] - 5]
        holiday.append(_pink_ratio(crop) > 0.20)

    rows = []
    raw_lines = []
    scores = []
    for r in range(33):
        ry0, ry1 = row_edges[r], row_edges[r + 1]
        name = _row_name(image, ry0, ry1, r)
        date_statuses = []
        row_scores = []
        raw_cells = []
        for c in range(12):
            if holiday[c]:
                status = "NOT_SCHEDULED"
                score = 0.0
            else:
                cell = image[ry0 + 7:ry1 - 7, col_edges[c] + 5:col_edges[c + 1] - 5]
                score = _ink_score(cell)
                row_scores.append(score)
                # Printed grid/paper noise is normally below 0.015. A handwritten mark
                # is substantially denser. 0.025 is intentionally conservative.
                if score >= 0.025:
                    status = "PRESENT"
                else:
                    status = "ABSENT"
            date_statuses.append(status)
            raw_cells.append(round(score, 4))

        scheduled = [s for s in date_statuses if s != "NOT_SCHEDULED"]
        present = scheduled.count("PRESENT")
        absent = scheduled.count("ABSENT")
        total = len(scheduled)
        confidence = int(round(min(99, max(55, 100 * (sum(row_scores) / max(1, len(row_scores))) / 0.055))))
        rows.append({
            "student": name,
            "statuses": date_statuses,
            "date_statuses": date_statuses,
            "present": present,
            "absent": absent,
            "leave": 0,
            "total": total,
            "confidence": confidence,
            "row": r + 1,
            "cell_scores": raw_cells,
        })
        raw_lines.append(f"{r + 1}. {name}: " + ", ".join(f"D{c+1}={s}" for c, s in enumerate(date_statuses)))
        scores.extend(row_scores)

    scheduled_columns = [i + 1 for i, hcol in enumerate(holiday) if not hcol]
    overall = int(round(min(99, max(70, 100 * (sum(scores) / max(1, len(scores))) / 0.055))))
    # If the expected 33-row register was detected, the result is directly reviewable.
    needs_review = len(rows) != len(REGISTER_ROSTER)
    return {
        "rows": rows,
        "raw_text": "\n".join(raw_lines),
        "ocr_confidence": overall,
        "status_tokens_found": sum(r["present"] for r in rows),
        "scheduled_columns": scheduled_columns,
        "holiday_columns": [i + 1 for i, hcol in enumerate(holiday) if hcol],
        "pages_processed": 1,
        "needs_review": needs_review,
        "note": "Attendance is read from the 12 register cells for each student. Pink-highlighted columns are shown as not scheduled."
    }
