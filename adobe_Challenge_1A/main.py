import fitz  # PyMuPDF
import json
import re
import time
from pathlib import Path

# -------- Text & Font Extraction --------
def extract_text_with_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc):
        text_blocks = page.get_text("dict").get("blocks", [])
        for block in text_blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = ""
                sizes = []
                font_names = []
                flags = []
                positions = []
                for span in line["spans"]:
                    span_text = span["text"].strip()
                    if span_text:
                        text += span_text + " "
                        sizes.append(span["size"])
                        font_names.append(span["font"])
                        flags.append(span["flags"])
                        positions.append(span["bbox"])
                if text.strip():
                    blocks.append({
                        "text": text.strip(),
                        "size": round(sum(sizes) / len(sizes), 2) if sizes else 0,
                        "font": font_names[0] if font_names else "",
                        "flags": flags[0] if flags else 0,
                        "bbox": positions[0] if positions else (0, 0, 0, 0),
                        "page": page_num + 1
                    })
    return blocks

# -------- Heuristics for Cleaning --------
def is_noise_heading(text):
    text = text.strip().lower()
    return (
        re.match(r"^page\s+\d+\s+of\s+\d+$", text) or
        re.match(r"^version\s+\d+(\.\d+)*$", text) or
        re.match(r"^\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{4}$", text)
    )

def is_bullet_point(text):
    return bool(re.match(r"^([\u2022\-\*\d+\.]\s+).+", text.strip()))

def is_valid_heading(text):
    text = text.strip()
    if not text or is_bullet_point(text) or is_noise_heading(text):
        return False
    lower = text.lower()
    return (
        2 <= len(text.split()) <= 25 and
        not re.match(r"^[\d\W_]+$", text) and
        not text.endswith((':', ';', ',', '.', '...')) and
        not text.islower() and
        not lower.startswith("from:") and
        not lower.startswith("to:")
    ) or re.match(r"^(unit|chapter|module)\s+[\divx]+", lower)

# -------- Heading Classifier --------
def classify_headings(blocks, pdf_path=""):
    if not blocks:
        return {"title": "", "outline": []}

    sizes = sorted({b["size"] for b in blocks}, reverse=True)
    size_to_level = {}
    for i, size in enumerate(sizes[:4]):
        size_to_level[size] = ["title", "H1", "H2", "H3"][i]

    outline = []
    seen = set()
    title_block = None

    for block in blocks:
        raw_text = block["text"].strip()
        if not raw_text or is_noise_heading(raw_text):
            continue

        size = block["size"]
        font_name = block.get("font", "").lower()
        flags = block.get("flags", 0)
        bbox = block.get("bbox", (0, 0, 0, 0))
        x0 = bbox[0]
        page = block["page"]
        level = size_to_level.get(size, "H3")

        is_bold = flags & 2 != 0
        is_centered = 200 < x0 < 400
        is_styled = is_bold or "bold" in font_name or is_centered

        key = (raw_text.lower(), page)
        if key in seen:
            continue
        seen.add(key)

        # Assign first centered largest block as title
        if not title_block and level == "title" and is_valid_heading(raw_text) and is_styled:
            title_block = raw_text
            continue  # Skip adding title to outline

        # Outline Detection
        if re.match(r"^\d+[\.\)]\s+[A-Z].+", raw_text) and is_bold:
            outline.append({"level": "H3", "text": raw_text, "page": page})
        elif is_centered and is_bold and is_valid_heading(raw_text):
            outline.append({"level": "H1", "text": raw_text, "page": page})
        elif is_bold and raw_text.endswith(":") and len(raw_text.split()) >= 4:
            outline.append({"level": "H2", "text": raw_text, "page": page})
        elif re.match(r"^\d+(\.\d+)*\s+.+", raw_text):
            outline.append({"level": level, "text": raw_text, "page": page})
        elif level in ["H1", "H2"] and is_valid_heading(raw_text) and is_styled:
            outline.append({"level": level, "text": raw_text, "page": page})
        elif re.match(r"^(unit|chapter|module)\s+[\divx]+", raw_text.lower()):
            outline.append({"level": "H2", "text": raw_text, "page": page})

    full_title = title_block or Path(pdf_path).stem
    return {
        "title": full_title.strip(),
        "outline": outline
    }

# -------- PDF Processing --------
def process_pdf(pdf_path, output_path):
    blocks = extract_text_with_fonts(pdf_path)
    data = classify_headings(blocks, pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def batch_process(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        if pdf_file.name.startswith("~$"):
            continue
        output_file = output_dir / f"{pdf_file.stem}.json"
        process_pdf(str(pdf_file), str(output_file))

# -------- Entry --------
if __name__ == "__main__":
    print("Starting PDF processing...")
    start_time = time.time()

    batch_process("input", "output")

    elapsed = time.time() - start_time
    print(f"Processing completed in {elapsed:.2f} seconds.")
    print("✅ Execution complete." if elapsed <= 10 else "⚠️ Execution exceeded 10 seconds.")
