# NDPR Compliance Skill

A free, open-source **agent skill** that audits a codebase for compliance with Nigerian data protection law. It works with Claude Code and other coding agents that support `SKILL.md` skills.

Ask your agent something like *"check our app for NDPR compliance"*. The skill then:

1. **Scans the repo** for personal data, trackers, third-party processors, foreign hosting regions, PII in logs, pre-ticked consent, retention jobs and data-subject-rights features. The scanner is bundled and dependency-free.
2. **Builds a personal data inventory**: what is collected, where it's stored, who it's shared with, and whether it leaves Nigeria.
3. **Checks each area** against the law:
   - consent and cookies
   - privacy notices
   - access, export and deletion rights
   - security
   - breach readiness
   - cross-border transfers
   - retention
   - children's data
   - automated decisions and AI
4. **Writes `NDPA-COMPLIANCE-REPORT.md`**. Each finding has `file:line` evidence, a severity, an exact legal citation and a concrete fix.
5. **Offers to fix** the issues, starting with the most severe.

## Which law?

People say **NDPR** (Nigeria Data Protection Regulation 2019), but the governing law is now the **Nigeria Data Protection Act 2023 (NDPA)**. It is implemented through the NDPC's **General Application and Implementation Directive 2025 (GAID)**. NDPR 2019 remains in effect only where it is consistent with the Act (NDPA s.64(2)(f)). This skill reviews against **NDPA + GAID**.

All section and article references in `references/law-map.md` were checked against the official texts. The map also lists commonly mis-cited provisions. For example, breach notification is **s.40**, not s.29, and the DPIA duty is **s.28**, not s.35.

## Install

### Claude Code (plugin)

```
/plugin marketplace add anaivi1960/ndpr-compliance-skill
/plugin install ndpr-compliance@ndpr-compliance-skill
```

### Claude Code (manual)

Copy the skill folder into your personal or project skills directory:

```bash
git clone https://github.com/anaivi1960/ndpr-compliance-skill
cp -r ndpr-compliance-skill/skills/ndpr-compliance ~/.claude/skills/        # all projects
# or
cp -r ndpr-compliance-skill/skills/ndpr-compliance .claude/skills/          # this project only
```

### skills CLI (Claude Code, Cursor, Codex and other agents)

```bash
npx skills add anaivi1960/ndpr-compliance-skill
```

### Any other agent

The skill is plain Markdown plus one Python script. Point your agent at `skills/ndpr-compliance/SKILL.md`.

## Usage

Example prompts:

- "Run an NDPR compliance check on this repo."
- "We're a Lagos fintech launching next month. Are we NDPA compliant?"
- "Is our cookie banner OK under the GAID?"
- "Where do we send BVNs and NINs, and is any of it leaving Nigeria?"
- "Do we need a DPIA for this feature?"

You can also run the scanner on its own:

```bash
python skills/ndpr-compliance/scripts/scan_signals.py path/to/repo           # Markdown
python skills/ndpr-compliance/scripts/scan_signals.py path/to/repo --json    # JSON
```

The scanner reports signals to investigate, not verdicts. It redacts any secrets it encounters.

## Example output

[`examples/sample-loan-app/`](examples/sample-loan-app) is a deliberately non-compliant mini lending app. The [report the skill produced for it](examples/sample-loan-app/NDPA-COMPLIANCE-REPORT.md) contains 17 findings, among them:
- the full user record (including BVN) written to logs
- BVN sent to an LLM abroad
- automated loan rejection with no human review
- pre-ticked marketing consent
- trackers loading before consent
- Hotjar recording the BVN field

## What's covered

| Area | Key provisions |
|---|---|
| Scope, definitions, sensitive data | NDPA s.2, s.65, s.30 |
| Principles, lawful basis | NDPA s.24, s.25; GAID Art.16–26 |
| Consent, cookies, trackers | NDPA s.26, s.35; GAID Art.7(l), 17–19 |
| Privacy notices, apps | NDPA s.27; GAID Art.27, 31 |
| DPIA, privacy by design, AI | NDPA s.28; GAID Art.28, 43 |
| Processors and DPAs | NDPA s.29; GAID Art.34 |
| Data subject rights | NDPA s.34–38; GAID Art.36–40 |
| Security, breach notification (72h) | NDPA s.39, s.40; GAID Art.29, 33 |
| Cross-border transfers | NDPA s.41–43; GAID Art.45 |
| Retention | NDPA s.24(1)(d), s.34(2); GAID Art.49 |
| DCPMI tiers, registration, DPO, CAR | NDPA s.32, s.44; GAID Art.8–14, Sch.7, Sch.10 |
| Enforcement, penalties | NDPA s.47–49 |

## Limitations

- **This is not legal advice.** It is an engineering review aid. Organisational obligations (NDPC registration, DPO designation, DPIA filing, CAR filing, processor agreements) usually can't be verified from code. The report lists them as items to confirm.
- Regulations, fees and NDPC guidance change. Confirm current fees and deadlines at [ndpc.gov.ng](https://ndpc.gov.ng).
- Sector rules (e.g. CBN, NCC, NHIA) and PCI DSS may add requirements beyond the NDPA. The skill flags these but does not audit against them.

## Contributing

Issues and PRs are welcome, especially:
- corrections to citations, with a reference to the official text
- new scanner patterns for Nigerian services and SDKs
- example reports from open-source projects

## License

[MIT](LICENSE)
