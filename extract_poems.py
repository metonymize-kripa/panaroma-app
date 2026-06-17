#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["pdfplumber"]
# ///
"""
Extract poems from PANORAMA.pdf preserving indentation and stanza breaks.

Usage:
    uv run extract_poems.py --update-json          # update poems.json in place (main use)
    uv run extract_poems.py --pages 11 12 13       # preview specific pages as text
    uv run extract_poems.py --output all.txt       # dump all pages to a single file
    uv run extract_poems.py --pdf other.pdf ...    # different PDF
"""

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import pdfplumber

PDF_PATH  = "PANORAMA.pdf"
JSON_PATH = "poems.json"


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_page(page) -> str:
    """
    Reconstruct text from raw character positions.
    Groups chars by y (top) coordinate → one entry per visual line.
    Inserts exactly one blank line where the vertical gap exceeds 1.6×
    median line spacing (stanza break). No synthetic blanks elsewhere.
    Strips trailing whitespace; preserves leading spaces (indentation).
    """
    chars = page.chars
    if not chars:
        return ""

    buckets: dict[int, list] = defaultdict(list)
    for c in chars:
        buckets[round(c["top"])].append(c)

    sorted_ys = sorted(buckets)
    spacings = [sorted_ys[i + 1] - sorted_ys[i] for i in range(len(sorted_ys) - 1)]
    median_sp = statistics.median(spacings) if spacings else 18
    stanza_threshold = median_sp * 1.6

    lines: list[str] = []
    for i, y in enumerate(sorted_ys):
        if i > 0 and (y - sorted_ys[i - 1]) > stanza_threshold:
            lines.append("")
        text = "".join(c["text"] for c in sorted(buckets[y], key=lambda c: c["x0"])).rstrip()
        if text:
            lines.append(text)

    return "\n".join(lines)


def poem_body(raw: str) -> str:
    """
    Strip the title and 'by Author' header that appears on every page,
    returning only the poem text.
    Page layout is always:  <title>  \\n\\n  by <author>  \\n\\n  <poem body...>
    """
    paras = raw.split("\n\n")
    body_paras = [p for p in paras[2:] if p.strip()]
    return "\n\n".join(body_paras)


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def update_json(pdf_path: str, json_path: str) -> None:
    """Re-extract every poem page and update the 'text' field in poems.json."""
    poems = json.loads(Path(json_path).read_text(encoding="utf-8"))

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        updated = 0
        for idx, poem in enumerate(poems):
            page_start = poem["page"]
            page_end   = poem.get("page_end", page_start)
            if not 1 <= page_start <= total:
                print(f"  skip: page {page_start} out of range (1–{total})")
                continue

            if page_start == page_end:
                raw  = extract_page(pdf.pages[page_start - 1])
                body = poem_body(raw)
            else:
                # First page: strip title/author header
                raw  = extract_page(pdf.pages[page_start - 1])
                body = poem_body(raw)
                # Continuation pages: use raw text directly (no header to strip)
                for pn in range(page_start + 1, page_end + 1):
                    if not 1 <= pn <= total:
                        print(f"  warn: continuation page {pn} out of range")
                        break
                    cont = extract_page(pdf.pages[pn - 1])
                    if cont:
                        body = body + "\n\n" + cont if body else cont

            if not body:
                print(f"  warn: page {page_start} — no body text extracted")
                continue
            poems[idx]["text"] = body
            updated += 1

    Path(json_path).write_text(
        json.dumps(poems, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Updated {updated}/{len(poems)} poems in {json_path}")


def preview(pdf_path: str, page_numbers: list[int] | None,
            output: str | None, output_dir: str) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        pages = page_numbers or list(range(1, total + 1))

        if output:
            out = Path(output)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                for p in pages:
                    if not 1 <= p <= total:
                        print(f"skip: page {p} out of range")
                        continue
                    text = extract_page(pdf.pages[p - 1])
                    if text:
                        f.write(f"{'=' * 60}\nPage {p}\n{'=' * 60}\n\n{text}\n\n")
            print(f"wrote {out}")
        else:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            written = 0
            for p in pages:
                if not 1 <= p <= total:
                    print(f"skip: page {p} out of range")
                    continue
                text = extract_page(pdf.pages[p - 1])
                if text:
                    (out_dir / f"page_{p:04d}.txt").write_text(text, encoding="utf-8")
                    written += 1
            print(f"wrote {written} files → {out_dir}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf",         default=PDF_PATH)
    parser.add_argument("--update-json", action="store_true",
                        help="update poems.json in place (main use)")
    parser.add_argument("--json",        default=JSON_PATH,
                        help="path to poems.json (with --update-json)")
    parser.add_argument("--pages",       nargs="+", type=int,
                        help="1-indexed page numbers to preview")
    parser.add_argument("--output",      type=str,
                        help="single output file for preview mode")
    parser.add_argument("--output-dir",  default="poems",
                        help="output directory for per-page preview files")
    args = parser.parse_args()

    if args.update_json:
        update_json(args.pdf, args.json)
    else:
        preview(args.pdf, args.pages, args.output, args.output_dir)
