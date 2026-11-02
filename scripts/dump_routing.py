"""
Routing dump — runs build.py's routers over real rows and writes the result.

Used for the PLL-mapping zero-diff gate: dump before a routing change, dump
after, diff. Never builds the board and never writes board-data.json.

  python scripts/dump_routing.py OUT.json --input INPUT.json

INPUT.json holds the Enrollment Database (course, program, technology) triples.
If it does not exist, they are fetched live (needs SMARTSHEET_API_TOKEN in the
environment) and saved there, so a second run routes the identical rows.
OE/SS rows come from the newest data/ files, chosen the way build.py chooses.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402  (a missing/invalid mapping file exits here)


def label_weekly(course):
    key, flagged = build.route_pll(course)
    return "VENDOR" if key == "__vendor__" else "UNMATCHED" if flagged else key


def label_lookahead(course, program, tech):
    key, flagged = build.route_lookahead_internal(course, program, tech)
    return "EXCLUDED" if key == "__excluded__" else "UNMATCHED" if flagged else key


def label_customer(tech, name):
    key, flagged = build.route_customer(tech, name)
    return "UNMATCHED" if flagged else key


def enrollment_triples(input_path):
    p = Path(input_path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    client = build.smartsheet_client()
    headers, rows, _ = build.fetch_sheet_table(client, "enrollment",
                                               "Enrollment Database")
    ci = build.find_col(headers, "course name", "class name", "course")
    pi = build.find_col(headers, "program")
    ti = build.find_col(headers, "technology")

    def cell(row, i):
        return str(row[i] or "").strip() if i is not None and i < len(row) else ""

    triples = [[cell(r, ci), cell(r, pi), cell(r, ti)] for r in rows if cell(r, ci)]
    p.write_text(json.dumps(triples, ensure_ascii=False), encoding="utf-8")
    return triples


def customer_pairs():
    files, missing, _ = build.discover_files(build.get_week(None)[0])
    if missing:
        sys.exit(f"missing source files: {missing}")
    pairs = []
    for bucket, key in (("OE", "demand"), ("SS", "classlist")):
        headers, rows = build.load_sheet(files[key])
        ni = build.find_col(headers, "class name")
        ci = build.find_col(headers, "course title")
        ti = build.find_col(headers, "technology")
        for r in rows:
            def g(i):
                return str(r[i] or "").strip() if i is not None and i < len(r) else ""
            name = g(ni) or g(ci)
            if name:
                pairs.append([bucket, g(ti), name])
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    out = []
    triples = enrollment_triples(args.input)
    for (course, program, tech), n in sorted(Counter(map(tuple, triples)).items()):
        out.append({"router": "internal_weekly", "course": course, "rows": n,
                    "result": label_weekly(course)})
        out.append({"router": "internal_lookahead", "course": course,
                    "program": program, "technology": tech, "rows": n,
                    "result": label_lookahead(course, program, tech)})
    pairs = customer_pairs()
    for (bucket, tech, name), n in sorted(Counter(map(tuple, pairs)).items()):
        out.append({"router": "customer", "bucket": bucket, "technology": tech,
                    "course": name, "rows": n,
                    "result": label_customer(tech, name)})

    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False),
                              encoding="utf-8")
    print(f"routing dump: {len(triples)} enrollment rows, {len(pairs)} OE/SS rows, "
          f"{len(out)} routed entries -> {args.out}")


if __name__ == "__main__":
    main()
