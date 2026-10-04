#!/usr/bin/env python3
"""Apply the OOOD caption glossary to an SRT or VTT file.

  fix    IN --out OUT [--report REPORT.md]   write a corrected copy (never overwrites anything)
  check  IN [--report REPORT.md]             report what would change, write nothing else
  prompt                                     print a vocabulary prompt for Whisper-style ASR

Timing and cue numbers are never touched; only cue text changes. Every change and every
review flag is listed in the report so a person can audit it both ways.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLOSSARY = HERE / "glossary.json"
MAX_LINE = 42  # house caption width
TIME = re.compile(r"^\s*\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s+-->\s+")


def ws(p):
    """' ?' in a pattern = optional whitespace; ' ' = any whitespace, including a line break."""
    return p.replace(" ?", r"\s*").replace(" ", r"\s+")


def load():
    g = json.loads(GLOSSARY.read_text())
    fixes = []
    for rule in g["fix"]:
        for p in rule["patterns"]:
            fixes.append((re.compile(ws(p), re.I), rule["term"]))
    reviews = [(re.compile(ws(r["pattern"])), r["why"]) for r in g["review"]]
    return g, fixes, reviews


def blocks(text):
    """Yield (header_lines, text_lines) per cue; header = index + timing lines."""
    for raw in re.split(r"\n\s*\n", text.strip("\n")):
        lines = raw.split("\n")
        i = next((k for k, l in enumerate(lines) if TIME.match(l)), None)
        if i is None:
            yield lines, []
        else:
            yield lines[: i + 1], lines[i + 1:]


def fix_text(lines, fixes):
    text = "\n".join(lines)
    changes = []
    for rx, term in fixes:
        def repl(m, term=term):
            found = m.group(0)
            if " ".join(found.split()) == term:  # already right; don't move a line break
                return found
            new = term
            gaps = re.findall(r"\s+", found)
            if "\n" in found and " " in term:  # keep the caption line break in the same gap
                words = term.split(" ")
                k = min(next(i for i, g in enumerate(gaps) if "\n" in g), len(words) - 2)
                new = " ".join(words[: k + 1]) + "\n" + " ".join(words[k + 1:])
            if found != new:
                changes.append((found.replace("\n", " "), term))
            return new
        text = rx.sub(repl, text)
    return text.split("\n"), changes


def run(path, fixes, reviews):
    src = path.read_text(encoding="utf-8")
    header = ""
    if src.startswith("WEBVTT"):
        header, _, src = src.partition("\n\n")
        header += "\n\n"
    out, report, flags = [], [], []
    for head, body in blocks(src):
        new_body, changes = fix_text(body, fixes)
        stamp = next((l.split("-->")[0].strip() for l in head if "-->" in l), "?")
        line = " ".join(new_body)
        for found, term in changes:
            report.append((stamp, found, term, line))
        for rx, why in reviews:
            if rx.search(line):
                flags.append((stamp, rx.pattern, why, line))
        if changes and any(len(l) > MAX_LINE for l in new_body) and not any(len(l) > MAX_LINE for l in body):
            flags.append((stamp, "width", f"a fix made this caption line longer than {MAX_LINE} characters; rewrap it", line))
        out.append("\n".join(head + new_body))
    return header + "\n\n".join(out) + "\n", report, flags


def write_report(dest, src, report, flags):
    md = [f"# Caption glossary report: `{src.name}`", "",
          f"{len(report)} automatic fixes, {len(flags)} lines flagged for a listen.", ""]
    md += ["## Automatic fixes", "", "| Time | Heard | Written | Line |", "|---|---|---|---|"]
    md += [f"| {t} | {a} | {b} | {l} |" for t, a, b, l in report] or ["| | none | | |"]
    md += ["", "## Check these against the audio", "", "| Time | Why | Line |", "|---|---|---|"]
    md += [f"| {t} | {w} | {l} |" for t, _, w, l in flags] or ["| | none | |"]
    Path(dest).write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fix"); f.add_argument("src"); f.add_argument("--out", required=True); f.add_argument("--report")
    c = sub.add_parser("check"); c.add_argument("src"); c.add_argument("--report")
    sub.add_parser("prompt")
    a = ap.parse_args()
    g, fixes, reviews = load()

    if a.cmd == "prompt":
        terms = []
        for r in g["fix"]:
            if r["term"] not in terms:
                terms.append(r["term"])
        print("Out of Our Depth, a podcast with Josh and Mary Eiland. Mary calls Josh J. "
              "Terms: " + ", ".join(t for t in terms if t not in ("J", "Eiland")) + ".")
        return

    src = Path(a.src)
    text, report, flags = run(src, fixes, reviews)
    for dest in [getattr(a, "out", None), a.report]:
        if dest and Path(dest).exists():
            sys.exit(f"refusing to overwrite {dest}; pick a new name")
    if a.cmd == "fix":
        Path(a.out).write_text(text, encoding="utf-8")
    if a.report:
        write_report(a.report, src, report, flags)
    print(f"{src.name}: {len(report)} fixes, {len(flags)} flagged"
          + (f" -> {a.out}" if a.cmd == "fix" else ""))
    for t, found, term, _ in report:
        print(f"  fix  {t}  {found!r} -> {term!r}")
    for t, _, why, line in flags:
        print(f"  flag {t}  {line[:70]!r}  ({why})")


if __name__ == "__main__":
    main()
