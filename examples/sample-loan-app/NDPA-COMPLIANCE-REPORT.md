# NDPA 2023 compliance review: fixture-loanapp (lending app)

_Reviewed 2026-11-17 against the Nigeria Data Protection Act 2023 and the NDPC General Application and Implementation Directive (GAID) 2025. This is an engineering review of the codebase, not legal advice._

> A note on "NDPR": the 2019 NDPR still exists, but only where it is consistent with the Nigeria Data Protection Act 2023 (s.64(2)(f)). The Act and GAID 2025 are what the NDPC enforces now, so this review checks against them.

## Summary
- **Applies?** Yes. The app collects BVN and NIN and serves borrowers in Nigeria (s.2(2); GAID Art.8(2)).
- **Role:** Controller for borrower data. Dojah, OpenAI, Vercel and the analytics vendors act as processors or recipients.
- **Likely DCPMI tier:** UHL. The app is a fintech in the financial sector (GAID Sch.7). This affects penalties (s.48) and filing duties. The penalty cap for a DCPMI is the greater of ₦10m or 2% of annual gross revenue (s.48(3)(a)).
- **Findings:** 1 critical · 9 high · 5 medium · 2 low · 9 need confirmation
- **Top 3 fixes:**
  1. Stop logging the full user object.
  2. Remove the BVN and email from the OpenAI prompt, and add a human-review path for automated loan rejections.
  3. Gate GA, Meta Pixel and Hotjar behind a consent banner, and un-tick the marketing checkbox.

Scope assumptions: the repo is small (5 files). The database host, privacy policy, selfie capture flow and admin tooling are not in it, so the related items are marked "Needs confirmation" rather than treated as violations.

## Personal data inventory
| Data | Sensitive? | Where collected | Where stored (region) | Shared with | Purpose | Retention |
|---|---|---|---|---|---|---|
| Email | No | `signup.tsx:2` | `User.email`; DB region unknown, functions in `iad1` (US) | OpenAI (prompt), logs | Account, risk check | None defined |
| Phone number | No | Not in visible form | `User.phoneNumber` | Logs | Contact (assumed) | None defined |
| BVN | High-risk identifier | `signup.tsx:2` | `User.bvn`, plaintext | Dojah (URL query), OpenAI (prompt), logs | KYC, risk | None defined |
| NIN | High-risk identifier | Not in visible form | `User.nin`, plaintext | Logs | KYC (assumed) | None defined |
| Date of birth | No (age check relevance) | Not in visible form | `User.dateOfBirth` | Logs | Eligibility (assumed) | None defined |
| State of origin | Proxy for ethnicity (s.65) | Not in visible form | `User.stateOfOrigin` | Logs | Unclear | None defined |
| KYC selfie | **Yes**, biometric (s.65) | Not in repo | `User.selfieUrl` (storage location unknown) | Logs (URL) | Identity verification (assumed) | None defined |
| Marketing opt-in | No | `signup.tsx:3` | `User.marketingOptIn`, default `true` | n/a | Marketing | None defined |
| Credit score / auto-reject | Derived, significant effect | `kyc.ts:6-7` | `LoanApplication` | OpenAI (inputs) | Loan decision | None defined |
| Browsing behaviour, session recordings | No (can capture typed BVN) | `layout.tsx:3-5` | Google, Meta, Hotjar (abroad) | Google, Meta, Hotjar | Analytics, ads | Vendor default |

## Findings

### [CRITICAL] Full user record, including BVN, NIN and selfie URL, written to logs
- **Where:** `src/lib/kyc.ts:4`
- **What:** `console.log("KYC request", user);` logs the whole user object. On Vercel this goes to the platform's log drain (US) and to any log integrations, and it includes BVN, NIN, date of birth, state of origin and the selfie URL.
- **Why it matters:** Logs are widely readable, rarely access-controlled, and kept outside your retention controls. A leak of BVN and NIN enables identity fraud. This breaks the security principle and the duty to apply proportionate technical measures: s.24(1)(f), s.39(1).
- **Fix:** Log an identifier only: `console.log("KYC request", { userId: user.id });`. Add a logger with a redaction list (`bvn`, `nin`, `selfieUrl`, `email`, `phoneNumber`, `dateOfBirth`). Purge existing log entries that contain BVNs.

### [HIGH] BVN and email sent to OpenAI in a prompt (foreign transfer, no recorded basis)
- **Where:** `src/lib/kyc.ts:6`
- **What:** `` content:`Assess risk for ${user.email} BVN ${user.bvn}` `` sends a direct identifier and the BVN to OpenAI in the US. The model cannot meaningfully assess risk from a BVN string, so it is not needed for the purpose.
- **Why it matters:** This is a cross-border transfer of identity data. It needs an adequacy basis or a s.43 ground, and the basis must be recorded (s.41(1), s.41(2)). Where the recipient country has no adequacy decision, GAID requires consent (GAID Art.18(1)(e)). Sending data the task doesn't need breaks minimisation (s.24(1)(c)). AI processing also triggers GAID Art.43 (DPIA with disparate-outcome assessment).
- **Fix:** Remove PII from the prompt entirely and pass only the non-identifying features the model actually uses. If an LLM stays in the loop, use a pseudonymous ID, confirm zero-retention and no-training settings with the provider, sign a DPA, record the transfer basis in a transfer register, and disclose OpenAI in the privacy notice. Also check sector rules: CBN data-localisation expectations may apply to BVN data.

### [HIGH] Loan applications rejected by a solely automated score with no human review
- **Where:** `src/lib/kyc.ts:7`, `prisma/schema.prisma:16-17`
- **What:** `if (score(r) < 500) return { autoRejected: true };`. The LLM output decides the rejection, with no review queue, appeal route or explanation.
- **Why it matters:** Refusing credit has a legal or similarly significant effect. A solely automated decision of this kind is only allowed under contract, law or consent, and then the borrower must be able to get human intervention, give their view and contest the decision (s.37). Consent is mandatory for such decisions (GAID Art.18(1)(f)). The logic must be disclosed (s.27(1)(g)), and scoring triggers a mandatory filed DPIA (GAID Art.28(3)).
- **Fix:** Change `autoRejected` to a `pendingReview` state, or let the score only recommend. Add a `LoanDecisionReview` model (`applicationId`, `reviewerId`, `outcome`, `reason`, `decidedAt`). Tell the applicant the decision was automated and give them a "request human review" button. Store the main reasons so you can explain the decision.

### [HIGH] Marketing consent is pre-ticked in the form and defaults to true in the database
- **Where:** `src/app/signup.tsx:3`, `prisma/schema.prisma:10`
- **What:** `<input type="checkbox" name="marketing" defaultChecked />` and `marketingOptIn Boolean @default(true)`.
- **Why it matters:** Consent must be affirmative, not pre-selected (s.26(7)). Silence or inaction is not consent (s.26(3)). Consent is mandatory for direct marketing (GAID Art.18(1)(a)).
- **Fix:** Remove `defaultChecked`, change the default to `@default(false)`, and treat existing `true` values as unconsented until users re-confirm.

### [HIGH] Data sharing with "partners" bundled into acceptance of terms
- **Where:** `src/app/signup.tsx:4`
- **What:** "By continuing you agree to our terms and to sharing your data with partners."
- **Why it matters:** Consent is not freely given when the service depends on agreeing to processing it doesn't need (s.26(2)). Consent requests also need an explicit accept or decline option (GAID Art.17(9)). Recipients must be identified in the notice (s.27(1)(c)), and "partners" names no one.
- **Fix:** Split this into (a) a link to the terms and privacy notice and (b) a separate, unticked opt-in for each named partner sharing purpose. If the sharing is needed for the loan (for example, credit bureaux), rely on contract or legal obligation (s.25(1)(b)) and name the recipients in the notice instead of asking for consent.

### [HIGH] Google Analytics, Meta Pixel and Hotjar load on every page before any consent; no cookie banner
- **Where:** `src/app/layout.tsx:3-5`
- **What:** All three scripts sit unconditionally in the root `<head>`. The repo has no consent banner or consent-management library.
- **Why it matters:** Non-necessary cookies and similar trackers need an explicit accept/reject choice before they run (GAID Art.19(2), (6), (8)). A cookie notice with accept/decline is expected on the homepage (GAID Art.7(l)). These vendors also process data abroad.
- **Fix:** Add a centred or side consent modal with equal-weight Accept, Reject and Customise buttons, which can be reopened from the footer ("Cookie settings"). Load each script only after the matching category is accepted. Set Google Consent Mode defaults to `denied`.

### [HIGH] Hotjar session replay runs on the signup page where the BVN is typed
- **Where:** `src/app/layout.tsx:5` (root layout, so it covers `src/app/signup.tsx:2`)
- **What:** Hotjar is loaded globally, and nothing in the repo excludes the BVN field from recordings (`data-hj-suppress` / `data-hj-allow` or similar).
- **Why it matters:** Session replay can capture keystrokes in identity fields and send them to a foreign vendor. That is a security failure (s.24(1)(f), s.39) and an unrecorded transfer (s.41(2)).
- **Fix:** Exclude Hotjar from the signup, KYC and loan routes entirely, or at minimum add `data-hj-suppress` to all identity and financial inputs and confirm that Hotjar's suppression settings are on. Gate it behind consent as described above.

### [HIGH] All processing hosted in the US with no recorded transfer basis
- **Where:** `vercel.json:1` (`{"regions":["iad1"]}`)
- **What:** Server functions, which handle BVN, NIN and biometric references, run in Washington, D.C. (US East).
- **Why it matters:** Processing outside Nigeria is a cross-border transfer and needs an adequacy basis or a s.43 ground (s.41(1)), recorded with the adequacy assessment (s.41(2)). A missing NDPC determination does not mean adequacy (s.42(6)).
- **Fix:** Create `docs/data-transfers.md` listing Vercel, the database host, OpenAI, Google, Meta and Hotjar, with data categories, country, transfer basis and DPA status. Consider a region closer to Nigeria for functions and the database. Check CBN localisation expectations for financial and BVN data with your sector counsel.

### [HIGH] No way to erase a user; soft delete with no purge
- **Where:** `prisma/schema.prisma:11` (`deletedAt DateTime?`); no delete or purge code anywhere in the repo
- **What:** Users can only be soft-deleted, so BVN, NIN, selfie and other data stay in the database indefinitely. Nothing removes the selfie object or the copies held by processors.
- **Why it matters:** Data subjects have a right to erasure without undue delay, including copies at third parties you shared with (s.34(1)(d), s.34(2); GAID Art.38(3)).
- **Fix:** Add a deletion flow that hard-deletes or anonymises the `User` row and its `LoanApplication` rows, deletes the selfie object, and calls processor deletion APIs where available. Keep only the records AML/KYC law requires, with a documented, time-limited legal-hold flag (GAID Art.38(2), Art.49(4)).

### [HIGH] BVN and NIN stored as plaintext columns
- **Where:** `prisma/schema.prisma:5-6`
- **What:** `bvn String` and `nin String?` have no field-level encryption, hashing or tokenisation. The repo has no encryption helpers.
- **Why it matters:** These identifiers enable fraud if the database or a backup leaks. Measures must be proportionate to sensitivity, and encryption is named among them (s.39(1)-(2)). Disk-level encryption from the database host doesn't protect against application-level or SQL-level access.
- **Fix:** Encrypt these fields at the application layer (for example AES-GCM with a KMS-managed key), store a keyed hash for lookups, and return only masked values (`*******1234`) from APIs and the UI.

### [MEDIUM] Biometric selfie and state of origin stored with no visible consent or purpose
- **Where:** `prisma/schema.prisma:8-9`
- **What:** `selfieUrl` (biometric, used for unique identification) and `stateOfOrigin` (a proxy for ethnicity) are required fields. No consent capture or just-in-time notice for them is in the repo, and nothing uses `stateOfOrigin`.
- **Why it matters:** Both count as sensitive personal data (s.65), and consent is mandatory for processing sensitive data (GAID Art.18(1)(b)). Collecting a field with no use breaks minimisation (s.24(1)(c)).
- **Fix:** Drop `stateOfOrigin` unless a specific legal requirement needs it. Add an explicit, unticked consent and a just-in-time notice on the selfie capture screen, recorded in a consent table. Delete the selfie after verification, or within a defined period.

### [MEDIUM] No retention or purge mechanism for any data
- **Where:** Repo-wide; no scheduler, TTL or lifecycle configuration. Affects all `User` and `LoanApplication` fields.
- **What:** Nothing ever deletes data, including selfies, rejected applications and soft-deleted users.
- **Why it matters:** Storage limitation applies (s.24(1)(d)). Where no other law sets a period, data must go within 6 months after the purpose is accomplished (GAID Art.49(3)).
- **Fix:** Write a retention schedule (data category, period, legal reason, mechanism) and add a scheduled purge job (for example a Vercel Cron route) with tests. Add lifecycle rules on the selfie bucket.

### [MEDIUM] Consent stored as a bare boolean with no proof or easy withdrawal
- **Where:** `prisma/schema.prisma:10`
- **What:** `marketingOptIn` records no timestamp, notice version or method. There is no unsubscribe or settings path in the repo.
- **Why it matters:** The controller must be able to prove consent (s.26(1); GAID Art.17(6)). Withdrawal must be as easy as giving consent (s.35(2)), and objection to direct marketing is absolute (s.36(3)-(4)).
- **Fix:** Add a `Consent` model (`userId`, `purpose`, `granted`, `noticeVersion`, `method`, `ipOrUserAgent`, `grantedAt`, `withdrawnAt`). Add a one-click toggle in settings and an unsubscribe link in every marketing message, checked by every sender.

### [MEDIUM] No data export or access capability
- **Where:** Repo-wide; no export endpoint or admin tool
- **What:** A borrower cannot get a copy of their data, and nothing gathers it across `User`, `LoanApplication` and processors.
- **Why it matters:** Data subjects have rights of access and to a copy in a common electronic format (s.34(1)(a)-(b)), plus portability (s.38).
- **Fix:** Add an authenticated `GET /api/me/export` that returns JSON for all of the user's rows, with BVN and NIN masked or included only after re-authentication. Track requests with a 30-day internal SLA (good practice, not a statutory deadline).

### [MEDIUM] No privacy notice at the point of collection
- **Where:** `src/app/signup.tsx:1-5`; no privacy policy route or link in the repo
- **What:** The signup form collects email and BVN with no link to a privacy notice.
- **Why it matters:** Before collecting data, you must give the controller's identity, the lawful basis, recipients, rights, retention, the right to complain to the NDPC, and any automated decision-making (s.27(1)(a)-(g)), in an accessible privacy policy (s.27(3)).
- **Fix:** Link a privacy notice from the signup form and the footer. Make it match this inventory: Dojah, OpenAI, Google, Meta, Hotjar and US hosting, automated credit decisions, retention periods and the NDPC complaint route. Mark the draft for legal review.

### [LOW] BVN sent to Dojah in a URL query string
- **Where:** `src/lib/kyc.ts:5`
- **What:** `fetch("https://api.dojah.io/api/v1/kyc/bvn?bvn="+user.bvn)`. Query strings often end up in proxy, APM and access logs.
- **Why it matters:** Avoidable exposure of an identifier (s.39(1)). This may be how the provider's API is designed, so it is rated Low.
- **Fix:** Use a POST or body-based endpoint if Dojah offers one. Make sure outbound URLs are excluded from APM and tracing. Confirm a DPA with Dojah.

### [LOW] Date of birth collected but no age check
- **Where:** `prisma/schema.prisma:7`
- **What:** `dateOfBirth` is stored, but nothing rejects applicants under 18.
- **Why it matters:** Processing children's data needs parental consent and verification (s.31(1)-(3)). A lending product should simply block minors.
- **Fix:** Reject signups under 18 on the server, using the date of birth returned by the BVN or NIN lookup rather than a self-declared value.

## Needs confirmation (not visible in code)
- [ ] NDPC registration as a DCPMI, likely UHL (s.44)
- [ ] DPO designated (s.32; GAID Art.11-14)
- [ ] DPIA done and filed before launch (s.28). GAID Art.28(3) triggers that apply: profiling/scoring, automated decisions with legal effect, sensitive data (biometrics), digital financial services, cross-border transfer, and AI/emerging tech (Art.43).
- [ ] Data processing agreements with Dojah, OpenAI, Vercel, the database host, Google, Meta and Hotjar (s.29(2); GAID Art.34)
- [ ] Transfer basis recorded for Vercel (US), OpenAI (US), Google, Meta, Hotjar and the database host if it is outside Nigeria (s.41(2))
- [ ] CAR filing through a licensed DPCO (GAID Art.10, Art.10(14)): due within 15 months of establishment if you were established after 12 June 2023, then annually (Art.10(8))
- [ ] Breach response plan, breach register (s.40(8)), and the ability to notify the NDPC within 72 hours (s.40(2)). The repo has no audit logging or incident artefacts, so you couldn't currently scope which users were affected by a breach.
- [ ] Where the selfie images are stored, and whether that bucket is private and encrypted
- [ ] Sector rules: CBN guidance on BVN handling and data localisation (outside the NDPA, but likely relevant)

## What's already good
- `nin` is optional, so it isn't forced where it isn't needed.
- Using a specialist KYC provider (Dojah) for BVN verification is better than building your own.
- `email` is unique, which helps target DSAR and erasure requests at the right record.

## Suggested order of work
1. **Critical:** remove PII from logs (`kyc.ts:4`) and purge existing logs.
2. **High, before launch:**
   - strip PII from the OpenAI prompt and add human review for rejections
   - un-tick marketing consent and unbundle partner sharing
   - add a consent banner and gate GA, Meta and Hotjar behind it, and keep Hotjar off the identity pages
   - encrypt and mask BVN and NIN
   - build an erasure flow
   - record transfer bases for US hosting
3. **Medium:**
   - sensitive-data consent and drop `stateOfOrigin`
   - retention schedule and purge job
   - consent records and withdrawal
   - data export
   - privacy notice
4. **Organisational:** DPIA, NDPC registration, DPO, DPAs, breach plan, CAR schedule.
