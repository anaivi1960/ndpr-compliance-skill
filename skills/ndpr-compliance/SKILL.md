---
name: ndpr-compliance
description: Audit a codebase for compliance with Nigerian data protection law (NDPA 2023, NDPC GAID 2025, and the older NDPR 2019) and help fix the gaps. Finds how personal data is collected, stored, logged, shared and transferred abroad. Checks consent and cookie banners, data subject rights (export, delete, correct), retention, security, breach readiness, automated decisions and children's data. Produces a findings report with exact section citations and concrete code fixes. Use this whenever the user mentions NDPR, NDPA, GAID, NDPC, "Nigeria Data Protection", Nigerian privacy compliance, or a DPIA/CAR/DPO in a Nigerian context. Also use it when they ask for a privacy or data-protection review of an app that serves users in Nigeria (fintech, lending, KYC with BVN/NIN, healthtech, edtech, e-commerce), even if they don't name the law.
license: MIT
---

# NDPR / NDPA compliance review for codebases

You are reviewing software for compliance with Nigeria's data protection regime. People still say "NDPR" (the 2019 Regulation), but the governing law is the **Nigeria Data Protection Act 2023 (NDPA)**. The NDPC's **General Application and Implementation Directive 2025 (GAID)** implements it. NDPR 2019 survives only where it is consistent with the Act (s.64(2)(f)). Review against NDPA + GAID. If the user said "NDPR", mention this once in a sentence and move on.

The goal is a review an engineering team can act on:
- real findings tied to real lines of code
- the correct legal citation
- a concrete fix

A short report of accurate findings beats a long one padded with generic privacy advice.

## Bundled resources

- `references/law-map.md` (long; use its table of contents and read the sections you need) holds the verified section and article map: what each provision requires, and the citation mistakes to avoid. **Cite only from this file.** Section numbers are easy to get wrong (breach is s.40, not s.29; DPIA is s.28, not s.35). Wrong citations destroy the credibility of an otherwise good review. If you need a provision that isn't in the map, describe the requirement and say "verify the exact provision" rather than inventing a number.
- `references/code-checks.md` is the catalogue of what to look for in code, area by area (A–L), with severity guidance and good fixes.
- `references/report-template.md` is the output format.
- `scripts/scan_signals.py` is a fast, dependency-free first-pass scanner (Python 3.8+). It surfaces likely locations of personal data, trackers, third-party processors, foreign hosting regions, PII in logs, pre-ticked consent, retention jobs and rights features. It redacts any secrets it sees.

## Workflow

### 1. Establish scope (briefly)

Work out, from the code, README and docs, or by asking if it's genuinely unclear:
- **Does the Act apply?** It does if the organisation operates in Nigeria, processes in Nigeria, or processes data of people in Nigeria, which includes targeting them (s.2(2), GAID Art.8(2)). Signs in code: NGN currency, +234 phone validation, BVN/NIN, Paystack/Flutterwave, Nigerian states lists.
- **Controller or processor?** A SaaS that processes its customers' end-user data is often a processor for that data and a controller for its own account data.
- **Sector and scale**, for the likely DCPMI tier (law-map §12). Fintechs and payment gateways are UHL by default.

Don't stall on this. State your assumptions in the report and continue.

### 2. Run the signal scan

```bash
python <skill-dir>/scripts/scan_signals.py <repo-root> > /tmp/ndpa-signals.md
```

Read the output. It is a map of where to look, **not** a list of findings. Most matches will be benign: a `phone` field is normal, and a `cron` may be unrelated. The "No matches" section matters too. Having no deletion, retention, consent-banner or export signals is often the most important result.

If Python isn't available, do the equivalent with grep/ripgrep, using the areas in `code-checks.md`.

### 3. Build the personal data inventory

Read the schemas, models, forms, API handlers, third-party integrations and infra config the scan pointed to. Fill in the inventory table (code-checks §A). Everything else hangs off it: you can't judge minimisation, notices, transfers or retention without knowing what data exists and where it goes.

Pay special attention to:
- **Sensitive data (s.65, s.30):** biometrics such as KYC selfies and liveness checks, health, religion, ethnicity (state of origin can proxy for it), political views, sex life, trade union membership.
- **High-risk identifiers:** BVN, NIN, card and account numbers.
- **Every place data leaves the system:** third-party SDKs and APIs, LLM prompts, analytics payloads, webhooks, and the hosting region itself.

### 4. Check each relevant area

Go through `references/code-checks.md` sections B–L, skipping areas that don't apply (no web UI → skip cookies; no ML/scoring → skip automated decisions). For each candidate issue:
1. **Open the file and confirm it.** Don't report a scanner hit you haven't read.
2. Decide whether it's a real gap, partially handled elsewhere, or fine. Check for mitigations before flagging. A tracker may be gated by a consent hook defined in another file. A soft-delete may have a purge job in a worker.
3. Assign a severity using the guide in code-checks.md.
4. Find the right citation in law-map.md.

Separate **code findings** (provable from the repo) from **organisational items** (registration, DPO, DPIA filing, DPAs, CAR, training). The latter go under "Needs confirmation", not as violations. A missing DPIA file in the repo doesn't mean no DPIA exists.

### 5. Write the report

Use `references/report-template.md`. Default to writing `NDPA-COMPLIANCE-REPORT.md` at the repo root. If the user asked a narrower question, such as "is our cookie banner compliant?" or "where do we send BVNs?", answer that directly in chat with the same rigour (evidence + citation + fix) instead of producing a full report.

### 6. Offer to fix

After the report, offer to implement fixes, highest severity first. When implementing:
- Prefer small, reviewable changes that match the codebase's existing patterns.
- Common fixes:
  - un-pre-tick consent defaults
  - gate trackers behind consent
  - add a consent record (purpose, notice version, timestamp, withdrawal)
  - scrub PII from logs and error trackers
  - mask BVN/NIN in UI and API responses
  - add an export endpoint and a real deletion path that also clears object storage and processors
  - add retention/purge jobs
  - add a breach register and runbook skeleton
  - add a human-review path for automated rejections
- Don't change legal text such as privacy policies or terms as if it were final. Draft it, mark it as a draft for legal review, and keep it consistent with what the code actually does.

## Judgement notes

- **Be precise about what the law says versus good practice.** For example, the Act sets no fixed DSAR deadline; it says "without undue delay". A 30-day SLA is a sensible recommendation, so present it as one. In contrast, the 72-hour NDPC breach notification (s.40(2)) and the GAID Art.49(3) 6-month default retention ceiling are real rules.
- **Financial services have extra layers.** BVN/NIN handling, CBN data-localisation expectations and PCI DSS may apply on top of the NDPA. Flag these as "also check sector regulation" rather than citing them as NDPA requirements.
- **Penalties give context, not scare tactics.** Mention the s.48 caps once in the summary if useful: the greater of ₦10m or 2% of annual gross revenue for DCPMIs, and the greater of ₦2m or 2% for others. Don't repeat them in every finding.
- **Credit what's done well.** Teams fix things faster when the review recognises existing good controls, and it stops them from accidentally removing those controls.
- **You're not giving legal advice.** Say so once in the report header. Don't hedge every sentence.
