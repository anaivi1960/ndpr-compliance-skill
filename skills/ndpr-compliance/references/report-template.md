# Report template

Write the report to `NDPA-COMPLIANCE-REPORT.md` in the repo root, unless the user asks for another location or chat-only output. Keep it scannable: a developer should be able to turn each finding into a ticket.

```markdown
# NDPA 2023 compliance review: <project name>

_Reviewed <date> against the Nigeria Data Protection Act 2023 and the NDPC General Application and Implementation Directive (GAID) 2025. This is an engineering review of the codebase, not legal advice._

## Summary
- **Applies?** <Yes/Likely/Unclear>, because <one line: e.g. "serves users in Nigeria (s.2(2)(c))">
- **Role:** <controller / processor / both>
- **Likely DCPMI tier:** <UHL / EHL / OHL / not major importance / unclear>, because <reason: sector + volume (GAID Sch.7)>. This affects penalties (s.48) and filing duties.
- **Findings:** <n> critical · <n> high · <n> medium · <n> low · <n> need confirmation
- **Top 3 fixes:** <one line each>

## Personal data inventory
| Data | Sensitive? | Where collected | Where stored (region) | Shared with | Purpose | Retention |
|---|---|---|---|---|---|---|

## Findings

### [CRITICAL] <short title>
- **Where:** `path/to/file.ts:42` (+ any others)
- **What:** <what the code does, quoting the line(s) briefly>
- **Why it matters:** <plain-language risk>, <NDPA s.X / GAID Art.Y>
- **Fix:** <concrete change; include a code sketch when it's short>

(repeat, ordered by severity)

## Needs confirmation (not visible in code)
- [ ] NDPC registration as a DCPMI (s.44) and tier
- [ ] DPO designated (s.32), if DCPMI
- [ ] DPIA done/filed (s.28; GAID Art.28(3) triggers: <which apply>)
- [ ] Data processing agreements with: <list processors found> (s.29(2); GAID Art.34)
- [ ] Transfer basis recorded for: <list foreign recipients> (s.41(2))
- [ ] CAR filing (GAID Art.10): <deadline if determinable>
- [ ] Breach response plan and breach register (s.40(8))

## What's already good
<Brief. Credit real controls (hashing, encryption, consent gating, deletion jobs) so the team knows what not to break.>

## Suggested order of work
1. <critical items>
2. <high items>
3. <medium items / documentation>
```

## Writing guidance

- **One finding = one problem.** If the same issue appears in 12 files, make one finding and list the locations. Don't pad the count.
- **Quote evidence.** Every code finding needs evidence:
  - **Something present**, such as a tracker or a log line: give its `file:line`.
  - **A missing capability**, such as no deletion, export or retention job: it is still a code finding. Set **Where:** to `Not found: searched <what/where>` (e.g. "no purge job in workers/, no TTL indexes, no bucket lifecycle rules") and point to the closest relevant code, e.g. the soft-delete column.
  - **Organisational matters** that code can't show either way (registration, DPO, DPIA filing, DPAs) go under "Needs confirmation".
- **Cite precisely, from `law-map.md` only.** Prefer the specific subsection, e.g. "s.26(7)(a)" rather than "s.26".
- **Explain the risk in plain words** before the citation. The reader is usually an engineer, not a lawyer.
- **Make fixes concrete.** Name the file to change and what to change, and give a short code sketch when it helps.
- **Don't inflate.** Use "Medium" for GAID-level expectations that are good practice but where reasonable people differ, such as exact banner placement. Use "Critical" only where real people could be harmed now.
