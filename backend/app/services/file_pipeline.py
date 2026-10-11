from pathlib import Path
import fitz
from .register_parser import parse_register


def pdf_pages_to_images(pdf_path: str, out_dir: str):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    paths = []
    try:
        if len(doc) == 0:
            raise ValueError("PDF has no pages")
        for idx, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2), alpha=False)
            page_path = out / f"{Path(pdf_path).stem}_page_{idx+1}.png"
            pix.save(str(page_path))
            paths.append(str(page_path))
    finally:
        doc.close()
    return paths


def process_file(path: str, work_dir: str):
    p = Path(path)
    if p.suffix.lower() != ".pdf":
        return parse_register(path)

    page_paths = pdf_pages_to_images(str(p), work_dir)
    all_rows = []
    raw_parts = []
    confidence = []
    status_hits = 0
    review = False
    for page_no, page_path in enumerate(page_paths, start=1):
        result = parse_register(page_path)
        confidence.append(result.get("ocr_confidence", 0))
        status_hits += result.get("status_tokens_found", 0)
        review = review or result.get("needs_review", False)
        raw_parts.append(f"--- PAGE {page_no} ---\n{result.get('raw_text','')}")
        for row in result.get("rows", []):
            row = dict(row)
            row["page"] = page_no
            all_rows.append(row)

    # Keep page-level rows visible while also merging repeated student names.
    merged = {}
    for row in all_rows:
        key = " ".join(str(row.get("student", "")).lower().split())
        if not key:
            continue
        if key not in merged:
            merged[key] = dict(row)
            merged[key]["statuses"] = list(row.get("statuses", []))
        else:
            cur = merged[key]
            cur["statuses"] = list(cur.get("statuses", [])) + list(row.get("statuses", []))
            cur["present"] = cur.get("present", 0) + row.get("present", 0)
            cur["absent"] = cur.get("absent", 0) + row.get("absent", 0)
            cur["leave"] = cur.get("leave", 0) + row.get("leave", 0)
            cur["total"] = cur.get("total", 0) + row.get("total", 0)
            cur["confidence"] = round((cur.get("confidence", 0) + row.get("confidence", 0)) / 2)

    rows = list(merged.values())
    overall = round(sum(confidence) / max(1, len(confidence)))
    return {
        "rows": rows,
        "raw_text": "\n".join(raw_parts),
        "ocr_confidence": max(0, min(100, overall)),
        "status_tokens_found": status_hits,
        "pages_processed": len(page_paths),
        "needs_review": review or len(rows) == 0 or overall < 70,
        "note": "PDF pages are processed individually with OpenCV + Tesseract. Handwritten registers may require review/calibration."
    }
