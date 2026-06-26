# SafetyAudit 🦺

**OSHA-compliant jobsite safety checklist generator & tracker.** Zero dependencies, pure Python stdlib.

Generate safety checklists by job type, log completed audits, and get flagged when the same violation keeps recurring across inspections.

> Part of the **Construction AI Toolkit** — four zero-dependency tools for the job site.

## Install
```bash
git clone git@github.com:realMNohgee/safetyaudit.git
cd safetyaudit
python3 safetyaudit.py --help
```

## Quick start
```bash
python3 safetyaudit.py check --type residential_framing --crew 4
python3 safetyaudit.py log --type residential_framing --crew 4 --issues "guardrail missing"
python3 safetyaudit.py report   # see audit history + recurring issues
```

## License
MIT — see [LICENSE](LICENSE).

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
