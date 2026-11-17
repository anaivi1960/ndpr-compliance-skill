# Code check catalogue

Each check is phrased as **what to look for in a codebase**, **why it matters** (with the citation from `law-map.md`), and **what a good fix looks like**. Work through the areas that are relevant to the system in front of you. A static marketing site doesn't need the automated-decision checks. A backend-only API doesn't need cookie banner checks.

Severity guide:
- **Critical**: personal data is being exposed or leaked right now, with clear harm potential. Examples:
  - BVN/NIN/card/health data written to logs, error trackers or session replays
  - ID documents in public buckets
  - plaintext passwords
  - unauthenticated endpoints returning other users' data
- **High**: a clear statutory requirement is missing or contradicted. Examples:
  - BVN/NIN/biometrics stored unencrypted at the application level (disk encryption by the host is not enough for these)
  - pre-ticked consent; trackers firing before consent
  - no erasure capability
  - undocumented foreign transfer of sensitive data
  - no breach path at all for a system holding financial or health data
- **Medium**: partial implementation, or a GAID-level expectation is unmet. Examples: a bottom-of-page cookie banner; no retention job; withdrawal harder than opt-in.
- **Low**: hygiene or documentation gaps.
- **Needs confirmation**: code can't show it either way. Ask; don't assume a violation.

---

## A. Data inventory (do this first; everything else depends on it)

Build a table of every personal-data field the system **collects, derives, stores or sends**:

| Field / entity | Category | Sensitive? (s.65) | Source | Where stored (DB, region) | Sent to (third parties) | Purpose | Lawful basis evidence | Retention |

Where to look:
- ORM schemas and migrations: Prisma `schema.prisma`, Django `models.py`, TypeORM/Sequelize entities, SQL migrations, Mongoose schemas, Rails `schema.rb`
- Form components and validation schemas (zod/yup/joi/pydantic)
- API request DTOs
- Mobile permission manifests: `AndroidManifest.xml` permissions, iOS `Info.plist` usage strings for location, contacts, camera, microphone, photos, tracking
- Analytics `identify()`/`track()` payloads
- LLM prompts that interpolate user data

Nigeria-specific identifiers to flag explicitly:
- **BVN** (Bank Verification Number)
- **NIN** (National Identification Number)
- passport, driver's licence and voter's card numbers
- TIN
- account number + bank code
- card PAN

KYC flows typically collect a selfie or liveness check, which is **biometric = sensitive** when used for unique identification. Health, religion, ethnicity/tribe and state-of-origin fields are common in Nigerian forms. State of origin can proxy for ethnicity, so call that out.

**Why:**
- s.24(1)(c) minimisation: every field must be needed.
- s.27 notice must list the data types.
- GAID Art.27(3)(c).

**Flag:**
- fields with no visible use (minimisation)
- sensitive fields collected without a s.30 ground
- free-text fields likely to capture sensitive data, e.g. "notes", "reason", "medical history"

## B. Lawful basis and consent capture

Look for:
- Signup, checkout and onboarding forms: are marketing, data-sharing or research checkboxes **pre-checked** (`defaultChecked`, `checked={true}`, `initialValue: true`, `default=True` on a `marketing_opt_in` column)?
  - Cite **s.26(7)(a)**. Severity: High.
- "By continuing you agree to…" bundling for **non-essential** processing.
  - Cite **s.26(2)**: conditional consent is not freely given.
- Consent stored as a bare boolean with no **timestamp, version of notice, channel, and scope**.
  - Cite **s.26(1)** + **GAID Art.17(6)**: the controller must be able to prove consent. Severity: Medium.
- A withdrawal path that is harder than opt-in, e.g. opt-in is one click but opt-out requires emailing support.
  - Cite **s.35(2)**.
- Consent required but missing for:
  - marketing emails/SMS/push (**GAID Art.18(1)(a)**, **s.36(3)**)
  - sensitive data (**Art.18(1)(b)**)
  - children (**Art.18(1)(d)**, **s.31**)
  - non-adequate transfers (**Art.18(1)(e)**)
  - solely-automated significant decisions (**Art.18(1)(f)**)
- Marketing sends that don't check an opt-out or suppression list.

**Good fix:** a `consents` table with `(subject_id, purpose, granted bool, notice_version, method, ip/user_agent, granted_at, withdrawn_at)`. Unchecked defaults. A one-click withdraw in settings and in every marketing message.

## C. Cookies, pixels and trackers (web)

Look for:
- Analytics/ads scripts loaded unconditionally in `<head>`, `_document`, `layout.tsx`, `index.html` or a tag manager: GA/gtag, GTM, Meta Pixel (`fbq`), TikTok pixel, Hotjar, Microsoft Clarity, Mixpanel, Segment, Amplitude, PostHog, FullStory, LogRocket.
  - Do they fire **before** consent?
  - Cite **GAID Art.19(2),(6)**. Severity: High.
- Session-replay tools (Hotjar, Clarity, FullStory, LogRocket, PostHog recordings) without input masking.
  - These capture keystrokes, possibly including BVN or card numbers.
  - Severity: High/Critical, depending on the pages covered.
- Cookie banner:
  - Exists at all? **GAID Art.7(l)**.
  - Has an equal-weight **Reject** button? **Art.19(6)**, **Art.17(9)**.
  - Positioned at the bottom as a thin bar? **Art.7(l)** says that is a lack of transparency. It should be conspicuous and visible without scrolling (**Art.19(7)(a)**). Severity: Medium.
  - Names the responsible organisation, the purposes, and how to withdraw? **Art.19(7)(b)–(e)**.
  - Provides a way to re-open preferences later (withdrawal)?
- `document.cookie`, `localStorage` or device-fingerprinting code used for tracking counts the same as cookies (**Art.19(8)**).

**Good fix:**
- Gate every non-necessary script behind a consent state: load on accept, never on reject.
- Use Google Consent Mode defaults set to `denied`.
- Render the banner as a centred or side modal with Accept/Reject/Customise.
- Persist the choice and expose "Cookie settings" in the footer.

## D. Privacy notice and in-app disclosures

Look for:
- A privacy policy page and route. Check it is linked from signup, checkout and the footer, and inside mobile apps (**GAID Art.31(2)(d)**).
- **Spot-check its content against the actual data inventory.** Mismatches are findings:
  - data collected but not disclosed
  - third parties used but not named
  - retention not stated (**s.27(1)(e)**)
  - no mention of the NDPC complaint right (**s.27(1)(f)**)
  - automated decisions undisclosed (**s.27(1)(g)**)
- Mobile apps need a **pre-installation privacy statement** (store listing / first-run screen) with the GAID Art.31(2)(e) items, including:
  - a support link
  - a self-service disable/uninstall link
  - a complaint link
- Just-in-time notices at the point of collection for sensitive data, e.g. the KYC selfie screen.

## E. Data subject rights (DSAR) capability

Check whether the system can actually do each of these. Note what's self-service versus manual.

| Capability | What to look for | Cite |
|---|---|---|
| Access / export | An export endpoint or admin tool that gathers **all** of a user's data across tables and third parties, in JSON/CSV | s.34(1)(b), s.38 |
| Rectification | Profile edit for all user-supplied fields; audit log of changes; no fee for correcting the controller's errors | s.34(1)(c), GAID Art.36 |
| Erasure | Delete account → hard delete or irreversible anonymisation across all tables, caches, search indexes, object storage (avatars, KYC images), analytics profiles and processors (the Mixpanel/Segment/CRM deletion APIs) | s.34(1)(d), GAID Art.38(3) |
| Restriction | A flag that freezes processing while a dispute is open | s.34(1)(e) |
| Objection / marketing opt-out | Suppression list checked by every marketing sender | s.36(3)–(4) |
| Automated decisions | For credit scoring, auto-KYC rejection, fraud auto-blocks, or AI-driven approvals: is there a human-review/appeal path, and is the subject told? | s.37(3) |
| Complaint / grievance intake | A contact route, a ticket with timestamps, and a 30-day SLA | GAID Art.40, Sch.9 |

**Common gaps:**
- `deletedAt` soft delete with no purge job, so data lives forever.
- Deletion that misses foreign-key children, S3 objects or third-party copies.
- Export that only covers the `users` table.

Legal-hold exceptions (**GAID Art.38(2)**, **Art.49(4)**), such as AML/KYC record-keeping by financial institutions, are legitimate reasons to retain specific records after an erasure request. When code retains data for this reason, check it is scoped and documented rather than flagging it as a violation.

## F. Security controls (s.39, GAID Art.29)

Look for:
- **Secrets & keys:** hard-coded API keys, DB URLs or JWT secrets in code; committed `.env` files.
- **Encryption at rest:**
  - BVN, NIN, card data, health data and KYC images stored in plaintext columns or public buckets.
  - Public S3/GCS/Supabase/Cloudinary buckets holding ID documents.
  - Card PAN storage at all (PCI DSS issue as well).
- **Encryption in transit:** `http://` endpoints for APIs; disabled TLS verification (`rejectUnauthorized: false`, `verify=False`).
- **Passwords:** bcrypt/argon2/scrypt is fine; MD5/SHA1/unsalted SHA256 or plaintext is Critical.
- **PII in logs:** `console.log(user)`, `logger.info(req.body)`, logging full webhook payloads from payment/KYC providers, Sentry without `beforeSend` scrubbing or with `sendDefaultPii: true`.
  - Cite **s.24(1)(f)** + **s.39**.
- **Access control:**
  - IDOR on user resources: `/users/:id` without an ownership check.
  - Admin panels exposing full PII without role checks.
  - No audit log of staff access to customer data.
- **Masking:** BVN/NIN/phone/account numbers shown in full where masking would do (e.g. `****1234`).
- **Backups:** existence, encryption, restore testing, expiry (**s.39(2)(d)**).
- **Dependency hygiene:** obviously outdated, vulnerable auth/crypto libs (**GAID Art.29(2)(c)**).

## G. Breach detection and response (s.40, GAID Art.33)

Code rarely contains a full incident process, but you can check whether the system **could** meet a 72-hour clock:
- Security-relevant logging and alerting: auth failures, mass exports, admin access, unusual query volumes.
- An incident or breach record: a table, runbook, or `docs/incident-response.md`.
  - **s.40(8)** requires a record of *all* breaches.
- The ability to answer "which users and which data were affected?": access logs with user IDs and timestamps.
- A mechanism to notify affected users quickly: bulk email/SMS capability.
- Processor contracts or webhooks: if the system is a processor, is there a way to notify the controller (**s.40(1)**)?

**Missing everything above:**
- High for systems with financial, health or identity data.
- Medium otherwise.
- The fix is a runbook plus a breach register plus alerting. Provide a skeleton.

## H. Third parties and cross-border transfers (ss.29, 41–43; GAID Art.34, 45)

Enumerate every external service that receives personal data:
- **Where to find them:** SDK imports, `package.json`/`requirements.txt`/`go.mod`, env var names (`*_API_KEY`), outbound HTTP clients, webhook targets.
- **Typical services:**
  - email/SMS: SendGrid, Mailgun, Resend, Twilio, Termii
  - payments: Paystack, Flutterwave, Stripe
  - KYC: Smile ID, Dojah, Prembly, YouVerify, QoreID
  - open banking: Mono, Okra
  - CRM: HubSpot, Intercom
  - analytics and error tracking
  - LLM APIs: OpenAI, Anthropic, Google
  - cloud storage
  - CDN/image services

For each, note:
1. **What data goes there** (from the call sites).
2. **Where it is processed.** Hosting regions in infra config:
   - Terraform `region`, `vercel.json` `regions`, Supabase/Neon/PlanetScale host strings
   - AWS `us-east-1`, `eu-west-1`, `af-south-1` (Cape Town is still **outside Nigeria**)
   - GCP `us-central1`, `europe-west*`

   Anything outside Nigeria is a cross-border transfer.
3. **Transfer basis recorded?** Look for a ROPA, transfer register or DPA reference in docs/. Absence → finding citing **s.41(2)**: the basis must be recorded.
4. **Is sensitive or identity data (BVN, NIN, biometrics, health) sent abroad?** That's High unless a documented basis exists. Also flag possible sector localisation rules (e.g. CBN for financial institutions) as "check sector regulator".
5. **LLM/AI usage:**
   - Is user PII sent in prompts? Is it necessary? Is redaction possible?
   - Is the provider's retention/training setting configured?
   - Is it disclosed in the privacy notice?
   - Cite **GAID Art.43** for emerging tech and the DPIA.

**Good fix:**
- A `docs/data-transfers.md` / ROPA listing each recipient, data categories, country, transfer basis (adequacy instrument or s.43 ground) and DPA status.
- PII minimisation or redaction before sending to third parties.
- Region selection where available.

## I. Retention and deletion (s.24(1)(d), GAID Art.49)

Look for:
- Scheduled jobs (cron, queues, DB TTL indexes, S3 lifecycle rules, log retention settings) that delete or anonymise data.
- **No retention mechanism at all** → Medium finding. Cite s.24(1)(d) and GAID Art.49(3): a 6-month default after the purpose ends, absent a legal requirement.
- Unbounded retention of high-risk artefacts:
  - KYC images after verification
  - OTPs
  - raw webhook payloads
  - session recordings
  - server logs with IPs or emails
- Inactive account handling.

**Good fix:**
- A retention schedule (data category → period → legal reason → mechanism).
- Purge jobs with tests.
- Lifecycle policies on buckets and logs.

## J. Children (s.31)

Look for:
- Products likely to have under-18 users: edtech, gaming, social, schools.
- Age gates, DOB collection, and parental consent flows.
- Whether age is **verified** (s.31(2)) or just self-declared. Self-declaration alone is weak for child-directed services. s.31(3) says government ID is an appropriate mechanism.
- Behavioural ads/trackers on child-facing pages (consent required, **GAID Art.18(1)(d)**).

## K. Automated decisions, profiling and AI (s.37, GAID Art.28(3), Art.43)

Look for:
- Credit scoring, loan approval, fraud scoring that auto-blocks, auto-reject KYC, dynamic pricing per user, and ML recommendation systems with significant effects.
- **Check:**
  - Is the decision **solely** automated?
  - Is there a human-review path and an appeal UI (**s.37(3)**)?
  - Is the logic disclosed (**s.27(1)(g)**)?
  - Is a DPIA referenced (**GAID Art.28(3)(a)–(b)**)?
- For AI features: training on user data without a disclosed basis; no opt-out; disparate-outcome testing absent (**GAID Art.43(4)**).

## L. DPIA and governance artefacts (look in docs/ and the repo root)

Code audits can note whether these exist in the repo, but their absence in a repo is **not** proof they don't exist:
- DPIA (**s.28**; mandatory triggers in **GAID Art.28(3)**: fintech, health, e-commerce, edtech, cross-border, communications software, CCTV)
- ROPA / data inventory
- Retention schedule
- Breach response plan + breach register
- DPAs with processors (**s.29(2)**, **GAID Art.34**)
- Transfer register (**s.41(2)**)
- Legitimate Interest Assessment if relying on legitimate interests (**GAID Sch.8**)

Report these as "Needs confirmation" unless the code itself proves otherwise. For example, a privacy notice in the code that claims a DPIA exists while none is referenced would still only be a "confirm" item.
