#!/usr/bin/env python3
"""
SafetyAudit — OSHA-compliant jobsite safety checklist generator & tracker.

Input a job type, phase, and crew size. Get back a comprehensive safety
checklist with hazard categories, required PPE, and inspection points.
Tracks completed audits over time, flags recurring violations, and
analyzes violation trends across the audit log.

Built-in OSHA 1926 knowledge base (illustrative — editable JSON).
Pure Python standard library. Zero dependencies.

Domains: construction safety · compliance tracking · OSHA inspection prep ·
AI-assisted safety management.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter
from datetime import datetime

CHECKLISTS = {
    "residential_framing": {
        "ppe": ["hard hat", "safety glasses", "steel-toe boots", "gloves", "hi-vis vest"],
        "hazards": [
            {"cat": "Fall Protection", "items": [
                "guardrails at openings >6ft", "PFAS harness inspected",
                "ladder tied off and 3ft above landing", "hole covers secured"
            ]},
            {"cat": "Material Handling", "items": [
                "lumber stacked flat, max 16ft high", "nails removed from scrap",
                "pneumatic hoses secured, whip checks on", "nail gun safety engaged when not firing"
            ]},
            {"cat": "Electrical", "items": [
                "GFCI protection on temp power", "cords not across walkways",
                "panel covers in place", "extension cords 12ga minimum"
            ]},
        ],
        "criteria": 4,
    },
    "commercial_roofing": {
        "ppe": ["hard hat", "safety glasses", "steel-toe boots", "gloves", "knee pads", "harness"],
        "hazards": [
            {"cat": "Fall Protection", "items": [
                "warning line at 6ft from edge", "PFAS anchor points rated 5000lb",
                "skylight covers installed", "ladder tied off at top and bottom"
            ]},
            {"cat": "Heat Safety", "items": [
                "water station on roof", "shade tent available",
                "heat index monitored", "buddy system active"
            ]},
            {"cat": "Material Handling", "items": [
                "kettle placed on non-combustible surface", "fire extinguisher within 25ft",
                "material hoisted, not carried up ladder"
            ]},
        ],
        "criteria": 3,
    },
    "electrical_rough_in": {
        "ppe": ["hard hat", "safety glasses", "steel-toe boots", "voltage-rated gloves"],
        "hazards": [
            {"cat": "Electrical Safety", "items": [
                "LOTO verified on all circuits", "panel dead-front confirmed",
                "voltage tester working, checked on known live", "NRTL-listed tools only"
            ]},
            {"cat": "Confined Space", "items": [
                "atmosphere tested before entry", "attendant present at entrance",
                "retrieval tripod setup", "ventilation running for 5min prior"
            ]},
        ],
        "criteria": 5,
    },
    "concrete_foundation": {
        "ppe": ["hard hat", "safety glasses", "steel-toe boots", "rubber boots",
                "chemical-resistant gloves", "hi-vis vest", "face shield (pouring)"],
        "hazards": [
            {"cat": "Excavation & Trenching", "items": [
                "shoring/trench box in place if >5ft deep", "spoil pile at least 2ft from edge",
                "ladder every 25ft in trench", "competent person inspected before shift"
            ]},
            {"cat": "Concrete Placement", "items": [
                "pump truck outriggers fully extended on pads", "washout area designated and lined",
                "vibrator cords GFCI-protected", "wet concrete splash PPE in use"
            ]},
            {"cat": "Rebar & Formwork", "items": [
                "rebar caps on all protruding bars", "form ties rated for pour pressure",
                "bracing checked after each truck load", "impalement hazards capped or guarded"
            ]},
        ],
        "criteria": 4,
    },
    "excavation_trenching": {
        "ppe": ["hard hat", "safety glasses", "steel-toe boots", "hi-vis vest",
                "gloves", "hearing protection (near equipment)"],
        "hazards": [
            {"cat": "Trench Safety", "items": [
                "protective system for trench >5ft (slope/shield/shore)",
                "competent person classified soil type (A/B/C)",
                "daily inspection documented before entry",
                "no water accumulation in trench",
                "ladder within 25ft of all workers"
            ]},
            {"cat": "Underground Utilities", "items": [
                "811 called and utilities marked", "hand-dig within 2ft of marked lines",
                "overhead power lines de-energized or flagged", "gas line shut-off valve identified"
            ]},
            {"cat": "Heavy Equipment", "items": [
                "swing radius barricaded", "spotter assigned for backing",
                "equipment inspections current (daily checklist)",
                "no workers under suspended loads"
            ]},
        ],
        "criteria": 5,
    },
}


def cmd_check(args):
    if args.type not in CHECKLISTS:
        print(f"unknown job type '{args.type}'. Available: {', '.join(sorted(CHECKLISTS))}",
              file=sys.stderr)
        return 2
    cl = CHECKLISTS[args.type]
    now = datetime.now().isoformat()
    report = {
        "job_type": args.type,
        "crew_size": args.crew,
        "phase": args.phase,
        "generated": now,
        "ppe_required": cl["ppe"],
        "checklist": [],
    }
    for cat in cl["hazards"]:
        c = {"category": cat["cat"], "items": []}
        for i, item in enumerate(cat["items"]):
            critical = i < cl.get("criteria", 3) or "critical" in item.lower()
            c["items"].append({"check": item, "critical": critical})
        report["checklist"].append(c)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif args.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["category", "item", "critical"])
        for cat in report["checklist"]:
            for item in cat["items"]:
                writer.writerow([cat["category"], item["check"],
                                 "YES" if item["critical"] else ""])
        sys.stdout.write(buf.getvalue())
    else:
        print(f"SAFETY AUDIT — {args.type} | crew: {args.crew} | phase: {args.phase}")
        print(f"PPE: {', '.join(cl['ppe'])}\n")
        for cat in report["checklist"]:
            print(f"[{cat['category']}]")
            for item in cat["items"]:
                crit = " ⚠ CRITICAL" if item["critical"] else ""
                print(f"  [ ] {item['check']}{crit}")
            print()
    return 0


def _read_log(log_path: str) -> list:
    """Read audit log as JSON array."""
    try:
        return json.load(open(log_path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def cmd_log(args):
    log = _read_log(args.log)
    ts = datetime.now().isoformat()
    entry = {"timestamp": ts, "job_type": args.type, "crew_size": args.crew,
             "phase": args.phase, "issues_found": args.issues, "notes": args.notes or ""}
    log.append(entry)
    open(args.log, "w", encoding="utf-8").write(json.dumps(log, indent=2) + "\n")
    print(f"logged audit #{len(log)} — {args.type} ({ts[:10]})")
    # Flag recurring issues (same issue in 2+ of last 5 audits)
    if len(log) >= 2:
        recent = log[-5:]
        issues_seen = {}
        for e in recent:
            for iss in e.get("issues_found", "").split(","):
                iss = iss.strip().lower()
                if iss:
                    issues_seen[iss] = issues_seen.get(iss, 0) + 1
        recurring = [k for k, v in issues_seen.items() if v >= 2]
        if recurring:
            print(f"  ⚠ RECURRING ISSUE: {', '.join(recurring)}")
    return 0


def cmd_report(args):
    log = _read_log(args.log)
    if not log:
        print("no audit log found")
        return 1

    if args.format == "json":
        print(json.dumps(log, indent=2))
    elif args.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["date", "job_type", "crew", "phase", "issues", "notes"])
        for e in log:
            writer.writerow([
                e["timestamp"][:10], e["job_type"], e["crew_size"],
                e.get("phase", ""), e.get("issues_found", ""),
                e.get("notes", ""),
            ])
        sys.stdout.write(buf.getvalue())
    else:
        print(f"SAFETY AUDIT REPORT — {len(log)} audits logged\n")
        for e in log[-20:]:
            issues = e.get("issues_found", "") or "none"
            print(f"  {e['timestamp'][:10]}  {e['job_type']:<22} crew:{e['crew_size']}  issues: {issues}")
    return 0


def cmd_trends(args):
    """Analyze violation trends from audit log."""
    log = _read_log(args.log)
    if not log:
        print("no audit log found")
        return 1

    # Collect all issues across all audits
    counter: Counter = Counter()
    job_counts: Counter = Counter()
    for entry in log:
        job_counts[entry["job_type"]] += 1
        for iss in entry.get("issues_found", "").split(","):
            iss = iss.strip()
            if iss:
                counter[iss] += 1

    if not counter:
        print("no violations found in audit log")
        return 0

    top5 = counter.most_common(5)
    patterns = [(k, v) for k, v in top5 if v >= 3]

    if args.format == "json":
        out = {
            "total_audits": len(log),
            "total_violations": sum(counter.values()),
            "unique_violations": len(counter),
            "top_5": [{"violation": k, "count": v} for k, v in top5],
            "patterns": [{"violation": k, "count": v} for k, v in patterns],
            "audits_by_type": dict(job_counts.most_common()),
        }
        print(json.dumps(out, indent=2))
    elif args.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["violation", "count", "pattern"])
        for k, v in counter.most_common():
            is_pattern = "YES" if v >= 3 else ""
            writer.writerow([k, v, is_pattern])
        sys.stdout.write(buf.getvalue())
    else:
        print(f"\n  VIOLATION TRENDS — {len(log)} audits, {sum(counter.values())} total violations\n")
        print(f"  Top recurring violations:")
        for i, (violation, count) in enumerate(top5, 1):
            flag = " ⚠ PATTERN (3+ occurrences)" if count >= 3 else ""
            bar = "█" * min(count, 30) if count <= 30 else "█" * 30 + f"+{count-30}"
            print(f"  {i}. {violation:<35} {count:>3}x  {bar}{flag}")
        print()

        if patterns:
            print(f"  ⚠ {len(patterns)} violation(s) flagged as patterns (3+ occurrences)")
            for k, v in patterns:
                print(f"    • {k} — {v}x")
            print()

        print(f"  Audits by type:")
        for job_type, count in job_counts.most_common():
            print(f"    {job_type:<25} {count}x")
        print()

    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="safetyaudit", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["text", "json", "csv"], default="text")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", parents=[common], help="generate safety checklist")
    s.add_argument("--type", required=True,
                   help=f"job type: {', '.join(sorted(CHECKLISTS))}")
    s.add_argument("--crew", type=int, default=1)
    s.add_argument("--phase", default="active")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("log", parents=[common], help="record completed audit")
    s.add_argument("--type", required=True)
    s.add_argument("--crew", type=int, default=1)
    s.add_argument("--phase", default="active")
    s.add_argument("--issues", default="")
    s.add_argument("--notes")
    s.add_argument("--log", default="safety_audit.json")
    s.set_defaults(func=cmd_log)

    s = sub.add_parser("report", parents=[common], help="view audit history")
    s.add_argument("--log", default="safety_audit.json")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("trends", parents=[common], help="analyze violation trends")
    s.add_argument("--log", default="safety_audit.json")
    s.set_defaults(func=cmd_trends)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
