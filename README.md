# SafetyAudit 🦺
![CI](https://github.com/realMNohgee/safetyaudit/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**OSHA-compliant jobsite safety checklist generator & tracker.** Zero dependencies, pure Python stdlib.

Generate safety checklists for 5 construction job types, log completed audits, track recurring violations, and analyze trends across your entire audit history.

> Part of the **Construction AI Toolkit** — four zero-dependency tools for the job site.

## One tool, many domains

| Domain | What SafetyAudit does for you |
|---|---|
| 🦺 **Safety Checklists** | Generate OSHA 1926 checklists for 5 job types with PPE requirements |
| 📋 **Audit Logging** | Record completed audits with issues found, crew size, and notes |
| 📈 **Trend Analysis** | Analyze violation trends — top 5 recurring issues, pattern detection (3+) |
| ⚠️ **Recurrence Alerts** | Auto-flag issues appearing in 2+ of the last 5 audits |
| 📊 **CSV Export** | Export checklists, reports, and trends to CSV for spreadsheets |

## Built-in Checklists

| Job Type | PPE Items | Hazard Categories |
|---|---|---|
| `residential_framing` | hard hat, glasses, boots, gloves, hi-vis | Fall Protection, Material Handling, Electrical |
| `commercial_roofing` | hard hat, glasses, boots, gloves, knee pads, harness | Fall Protection, Heat Safety, Material Handling |
| `electrical_rough_in` | hard hat, glasses, boots, voltage-rated gloves | Electrical Safety, Confined Space |
| `concrete_foundation` | hard hat, glasses, boots, rubber boots, chem gloves, hi-vis, face shield | Excavation & Trenching, Concrete Placement, Rebar & Formwork |
| `excavation_trenching` | hard hat, glasses, boots, hi-vis, gloves, hearing protection | Trench Safety, Underground Utilities, Heavy Equipment |

## Install
```bash
git clone git@github.com:realMNohgee/safetyaudit.git
cd safetyaudit
python3 safetyaudit.py --help
```

## Quick start
```bash
# Generate a checklist
python3 safetyaudit.py check --type excavation_trenching --crew 5
python3 safetyaudit.py check --type concrete_foundation --crew 3 --format csv

# Log completed audits
python3 safetyaudit.py log --type residential_framing --crew 4 \
  --issues "guardrail missing,hole cover unsecured"

# View audit history
python3 safetyaudit.py report
python3 safetyaudit.py report --format csv

# Analyze violation trends
python3 safetyaudit.py trends
python3 safetyaudit.py trends --format json
```

## Subcommands

| Command | Description |
|---|---|
| `check` | Generate a safety checklist for a job type |
| `log` | Record a completed audit with issues found |
| `report` | View audit history (last 20 entries) |
| `trends` | Analyze violation trends — top 5, patterns, audits by type |

All subcommands support `--format text|json|csv`.

## License
MIT — see [LICENSE](LICENSE).

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
