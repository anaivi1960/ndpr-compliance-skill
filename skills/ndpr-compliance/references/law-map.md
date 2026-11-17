# Nigerian data protection law map (for code audits)

Source texts: **Nigeria Data Protection Act 2023** ("NDPA", "the Act") and the **NDP Act General Application and Implementation Directive 2025** ("GAID", issued by the NDPC on 20 March 2025). Section and Article numbers below were checked against the official texts. Cite **only** from this map. If you need a provision that isn't here, say "verify against the official text" instead of guessing a number.

## Contents
1. How the instruments fit together
2. Scope and key definitions
3. Principles and lawful basis
4. Consent, cookies, children
5. Transparency (privacy notice)
6. DPIA and privacy by design
7. Processors and data processing agreements
8. Data subject rights
9. Security and breach notification
10. Cross-border transfer
11. Retention
12. Organisational duties (DCPMI, DPO, CAR)
13. Enforcement and penalties
14. Citation mistakes to avoid

---

## 1. How the instruments fit together

- **NDPA 2023** is the primary law. Where another law conflicts on personal data, the Act prevails (s.63).
- **NDPR 2019** (Nigeria Data Protection Regulation, issued by NITDA) **remains in effect** under s.64(2)(f), but only until it is repealed or replaced and only where it is consistent with the Act. Treat it as secondary. Users often say "NDPR" when they mean "Nigerian data protection law" generally. Answer for NDPA + GAID, and explain this gently once.
- **GAID 2025** is the NDPC's implementing directive (Articles 1–52, Schedules 1–10). It turns the Act's general duties into concrete requirements, such as cookie banner placement, DPIA triggers and CAR filing.
- **NDPC** is the Nigeria Data Protection Commission, the regulator (s.4).

## 2. Scope and key definitions

| Topic | Rule | Cite |
|---|---|---|
| Territorial scope | The Act applies if the controller or processor is domiciled, resident or **operating in Nigeria**; or processing occurs in Nigeria; or a foreign controller or processor **processes data of a data subject in Nigeria**. | NDPA s.2(2) |
| "Operating in Nigeria" | Includes **targeting** data subjects in Nigeria, even without a Nigerian presence. | GAID Art.8(2) |
| Household exemption | Purely personal or household processing is outside the Act. | NDPA s.3(1) |
| Personal data | Any information relating to an identified or identifiable individual, e.g. name, ID number, location data, online identifier. | NDPA s.65 |
| Sensitive personal data | Genetic & biometric data (for unique identification); race/ethnic origin; religious or similar beliefs; **health status**; sex life; political opinions/affiliations; trade union membership; plus anything NDPC prescribes. Financial data is **not** on the statutory list. GAID treats it as high-risk (Art.19(5), Sch.7). | NDPA s.65, s.30 |
| Processing sensitive data | Prohibited unless one of the s.30(1) grounds applies: (a) consent; (b) employment/social security obligations; (c) vital interests where the subject can't consent; (d) members of non-profits; (e) legal claims; (f) substantial public interest under a law; (g) medical care under a duty of confidentiality; (h) public health; (i) archiving/research under a law. For a commercial app the realistic ground is usually **(a) consent**, which GAID Art.18(1)(b) also requires. | NDPA s.30(1) |
| Child | As defined in the Child's Rights Act 2003, i.e. **under 18**. | NDPA s.65, s.31 |
| Processing | Any operation on personal data. It **excludes mere transit** of data originating outside Nigeria. | NDPA s.65 |
| Personal data breach | A security breach leading to accidental or unlawful destruction, loss, alteration, or unauthorised disclosure of or access to personal data. | NDPA s.65 |

## 3. Principles and lawful basis

**Principles: NDPA s.24(1)**
- (a) fair, lawful, transparent
- (b) purpose limitation (s.24(4) covers compatible further processing)
- (c) data minimisation: "adequate, relevant, and limited to the minimum necessary"
- (d) storage limitation
- (e) accuracy
- (f) security

s.24(2) requires appropriate technical and organisational measures (TOMs) for confidentiality, integrity and availability. s.24(3) imposes a **duty of care** and **accountability** on controllers and processors.

**Lawful bases: NDPA s.25(1)**
- (a) consent
- (b)(i) contract
- (b)(ii) legal obligation
- (b)(iii) vital interest
- (b)(iv) public interest/official authority
- (b)(v) legitimate interests

Legitimate interests fail if they override the subject's rights, are incompatible with the other bases, or the subject wouldn't reasonably expect the processing (s.25(2)). GAID Art.16–26 elaborate each basis; Schedule 8 is the **Legitimate Interest Assessment** template.

**Consent is mandatory (GAID Art.18(1)) for:**
- direct marketing
- sensitive personal data
- incompatible further processing
- children's data
- transfers to a country without an NDPC adequacy decision
- solely-automated decisions with legal or similarly significant effects

## 4. Consent, cookies, children

| Rule | Cite |
|---|---|
| Controller bears the burden of proving consent → **must keep consent records** | NDPA s.26(1); GAID Art.17(6) |
| Consent is not freely given if a service is conditional on consent to unnecessary processing | NDPA s.26(2) |
| **Silence or inactivity is not consent** | NDPA s.26(3) |
| Must tell the subject about the right to withdraw **before** consent is given | NDPA s.26(4) |
| Clear, simple language; accessible format | NDPA s.26(6) |
| Consent must be **affirmative, not pre-selected** | NDPA s.26(7)(a) |
| Consent may be written, oral or electronic | NDPA s.26(7)(b) |
| Withdrawal must be **as easy as giving** consent | NDPA s.35(2); GAID Art.17(7)(b) |
| Refusing consent must not be detrimental to the subject | GAID Art.17(7)(c) |
| Where consent is required, give a clear and explicit **accept or decline** option | GAID Art.17(9) |
| Cookies and similar trackers need consent, except "necessary" cookies (security, network stability, accessibility) that don't process sensitive, financial or privately stored data | GAID Art.19(2),(5),(6) |
| All non-necessary cookies need an explicit **yes/no (accept/reject)** choice | GAID Art.19(6) |
| Cookie banner must be **conspicuous, with no scrolling needed to see it**. Trackers must be disclosed in the first-visible section. Say who is responsible, the purpose, and how to withdraw. | GAID Art.19(7) |
| Privacy & cookie notice on the homepage. The cookie notice must let the subject accept or decline, and should obstruct the middle/left/right of the page. **A bottom-of-page banner = lack of transparency.** | GAID Art.7(l) |
| Pixels, SDKs, fingerprinting and other "tracking tools similar to cookies" follow cookie rules | GAID Art.19(8) |
| Children: get **parent or guardian consent**; apply age and consent **verification** mechanisms (government ID counts) | NDPA s.31(1)–(3) |

## 5. Transparency (privacy notice)

Before collecting directly from the subject, tell them (NDPA s.27(1)):
- (a) the controller's identity and contact details
- (b) the **specific lawful basis** and purposes
- (c) recipients
- (d) their rights
- (e) **retention period**
- (f) the right to complain to the NDPC
- (g) any automated decision-making or profiling, its consequences, and the right to object

Put this in a clear, accessible privacy policy (s.27(3)). GAID Art.27(3) adds: the types of data collected, the means of processing, third-party access and its purpose, and an internal remediation contact. A privacy notice is **not** a request for consent (GAID Art.27(4)).

**Software and apps (GAID Art.31).** Applies when deploying software that tracks data subjects or opens a communication link with them, such as a mobile app, OS, firmware or driver. It requires:
- a DPIA **before deployment**
- privacy by design and by default
- compliance with app-store security guidance
- a privacy policy **inside the software**
- a **pre-installation privacy statement** covering:
  - data types and the lawful purpose
  - the TOMs used (e.g. name the encryption)
  - that a DPIA was done
  - a privacy support link
  - a self-service disable or uninstall link
  - a complaints link

## 6. DPIA and privacy by design

- **DPIA is required before high-risk processing** (NDPA s.28(1)). If residual risk stays high, **consult the NDPC before processing** (s.28(2)). Required contents are in s.28(4); the template is GAID Schedule 4.
- **GAID Art.28(3) makes a DPIA mandatory and filed with the NDPC** for:
  - profiling or scoring
  - automated decisions with legal effect
  - systematic monitoring
  - sensitive or highly personal data
  - vulnerable subjects
  - innovative technology
  - **software for communicating with data subjects**
  - **digital financial services**
  - **health care**
  - **e-commerce**
  - public-facing CCTV
  - education records
  - hospitality
  - **cross-border transfer**

  In practice, almost every Nigerian fintech, healthtech, edtech or e-commerce product needs one.
- A DPIA must be done before processing starts (Art.28(9)), vetted and signed by an NDPC-accredited DPO (Art.28(4),(12)), and include privacy-by-design-and-default measures (Art.28(11)).
- **Emerging tech (AI, IoT, blockchain), GAID Art.43:**
  - Run a DPIA that assesses **disparate outcomes** and the vulnerability index in Schedule 6.
  - Consider anonymisation at collection.
  - Test in low-risk environments.
  - Monitor continuously.
  - Account for the right to be forgotten, e.g. with synthetic data or tokenisation.

## 7. Processors and data processing agreements

- When engaging a processor or sub-processor, ensure it meets the Act, helps with data subject rights, implements security, gives compliance information, and notifies new sub-processors (NDPA s.29(1)). A **written agreement** is required (s.29(2)).
- **The DPA must include** (GAID Art.34(2)):
  - parties and purpose
  - **location of processing**
  - scope and lawful basis
  - TOMs and the DPIA outcome
  - risks
  - evidence of NDPC registration
  - confidentiality, tenure, restrictions, indemnity, insurance, force majeure and disputes

  The controller is accountable for its third parties (Art.34(3)).

## 8. Data subject rights

| Right | Cite | What code should support |
|---|---|---|
| Access & confirmation: purposes, categories, recipients (esp. foreign), retention, source, automated decisions | NDPA s.34(1)(a) | DSAR intake + response |
| Copy in a **commonly used electronic format** | s.34(1)(b) | Export |
| Rectification of inaccurate data | s.34(1)(c); GAID Art.36 | Self-service edit. GAID Art.36(4): don't charge for fixing the controller's own input error. Art.36(5): keep an audit trail of the error source. |
| Erasure without undue delay | s.34(1)(d), s.34(2); GAID Art.38 | Delete or anonymise, **including at third parties you shared with** (Art.38(3)) |
| Restriction pending a dispute | s.34(1)(e) | Processing-restricted flag |
| Withdraw consent anytime, as easily as giving it | s.35 | Unsubscribe / revoke toggles |
| Object; **absolute right against direct marketing** | s.36(3)–(4) | Marketing opt-out honoured everywhere |
| No solely-automated decisions with legal or similarly significant effect, unless contract, law or consent applies; then provide **human intervention, a way to express a view, and a way to contest** | s.37 | Human review path for automated credit, KYC or fraud decisions |
| Portability: structured, machine-readable, direct transmission where feasible. Applies to consent- and contract-based data. | s.38; GAID Art.37 | JSON/CSV export |
| Complain to the NDPC | s.46; GAID Art.39 | Mention in the privacy notice and in-app |
| SNAG (Standard Notice to Address Grievance): the subject may demand a fix; respond **within 30 days or sooner if specified** | GAID Art.40, Schedule 9 | Grievance intake with tracking |

GAID Art.7(s)–(u) expect systems that make access, correction and portability "seamless". The Act sets no fixed DSAR deadline beyond "without undue delay". GAID Art.49(2) says to act promptly, so a 30-day internal SLA is a reasonable recommendation (present it as practice, not law).

## 9. Security and breach notification

- **TOMs (NDPA s.39(1)–(2))** must be proportionate to the volume and sensitivity of the data. Examples given:
  - pseudonymisation/de-identification
  - **encryption**
  - resilience
  - **restore/backup**
  - periodic risk assessment, including of data in transit
  - regular testing
  - updates
- **GAID Art.29** requires a monitoring and maintenance schedule covering:
  - training
  - certifications
  - software updates
  - **database vulnerability tests**
  - **authentication checks**
  - **encryption reviews**
  - QA

  An information security officer must certify the schedule.
- **Processor → controller:** notify on becoming aware of a breach (NDPA s.40(1)).
- **Controller → NDPC:** within **72 hours** of becoming aware, if the breach is likely to risk individuals' rights (NDPA s.40(2); GAID Art.33(1)). Information may be given in phases (s.40(9)).
- **Controller → data subjects:** **immediately** if the risk is high (NDPA s.40(3); GAID Art.33(3)). "High risk" includes possible fraud, identity theft, or exposure of sensitive data (Art.33(2)). Use public communication if direct contact isn't feasible.
- **Notification contents:** NDPA s.40(4) and GAID Art.33(5) cover circumstances, timing, data involved, risk assessment, number affected, mitigation, steps to notify individuals, and a contact person.
- **Breach register:** a **record of all breaches** must be kept, covering facts, effects and remediation (NDPA s.40(8)).

## 10. Cross-border transfer

- A transfer from Nigeria needs one of:
  - **adequacy**: the recipient is bound by a law, BCRs, contractual clauses, a code or a certification giving adequate protection (s.41(1)(a), s.42)
  - **a s.43 ground**: informed consent to the risks; contract necessity; the subject's sole benefit; public interest; legal claims; or vital interests
- **Record the transfer basis and the adequacy assessment** (s.41(2)).
- No NDPC determination ≠ adequacy (s.42(6)). Schedule 5 is the evaluation guidance (GAID Art.45).
- A transfer to a country without an adequacy decision needs **consent** (GAID Art.18(1)(e)). Treat the consent route cautiously; SCC-style contractual clauses are the more robust basis.
- **Code implication:** anywhere personal data leaves Nigeria counts. That includes:
  - a cloud region outside Nigeria
  - foreign SaaS such as analytics, email, CRM, error tracking or LLM APIs
  - support tools

  Each needs a recorded basis and, usually, a DPA.
- **Sector rules may be stricter.** For example, CBN rules for financial data and NITDA's Guidelines for Nigerian Content in ICT have localisation expectations. Flag these as "check sector regulator" rather than citing them as NDPA.

## 11. Retention

- Keep data no longer than necessary for the lawful basis (NDPA s.24(1)(d)), and erase when it is no longer needed or no basis remains (s.34(2)).
- **Default ceiling: GAID Art.49(3).** Where no law sets a period, storage "shall lapse not later than **six (6) calendar months** when the original purpose of the processing has been accomplished."
- Retention for **defence of legal claims or due diligence** is allowed with appropriate TOMs (Art.49(4)).
- **Code implication:** look for retention jobs, TTLs and soft-delete purges. Soft-deleted rows kept forever, backups that never expire, and logs kept indefinitely are common gaps.

## 12. Organisational duties

These obligations usually can't be proven from code. Report them as "confirm with the organisation", not as code findings.

- **Data controller/processor of major importance (DCPMI):**
  - **Who qualifies (GAID Sch.7 para 1):** having a filing system plus any one of:
    - more than 200 data subjects in 6 months
    - commercial ICT services on others' devices
    - operating in a listed sector: aviation, communication, education, electric power, export/import, financial, health, hospitality, insurance, oil & gas, tourism, e-commerce, public service
  - **Tiers (Sch.7 para 2–3), with registration fees:**

    | Tier | Fee | Who falls in it |
    |---|---|---|
    | **UHL** (Ultra-High) | ₦250,000 | Commercial banks, telcos, insurers, multinationals, DisCos, oil & gas, public social-media and email apps, device makers, payment gateways, **fintechs**, and anyone with >5,000 subjects in 6 months |
    | **EHL** (Extra-High) | ₦100,000 | MDAs, microfinance banks, higher institutions, secondary/tertiary hospitals, mortgage banks, and anyone with 1,000–5,000 subjects in 6 months |
    | **OHL** (Ordinary-High) | ₦10,000 | Primary and secondary schools, corporate trainers, primary health centres, independent labs, small hotels, and processors of sensitive data of more than 200 subjects |

    Fees and lists can change, so tell users to confirm on ndpc.gov.ng.
- **Registration** with the NDPC (NDPA s.44). Notify significant changes within **60 days** (s.44(3); GAID Art.9(4)).
  - UHL and EHL register once, then file CAR annually (GAID Art.9(2)).
  - OHL renews registration annually instead of filing CAR (Art.9(3)).
- **DPO:** a DCPMI must designate one with expert knowledge. The DPO may be an employee or a contractor (NDPA s.32; GAID Art.11–14).
- **Compliance Audit Returns (CAR):** filed annually through the NDPC portal (GAID Art.10(6),(12)).
  - **Deadline:**
    - **31 March** each year if established before 12 June 2023 (Art.10(7))
    - otherwise within **15 months** of establishment, then annually (Art.10(8))
  - **Late filing:** +50% of the filing fee (Art.10(9)).
  - **UHL and EHL must file through a licensed DPCO** (Data Protection Compliance Organisation, licensed under NDPA s.33) (Art.10(14)).
  - **Filing fees** are in Schedule 10:

    | Tier | Fee range |
    |---|---|
    | UHL | ₦500k–₦1M |
    | EHL | ₦100k–₦250k |
- **Other GAID Art.7 duties:**
  - semi-annual internal data protection report (Art.7(e), Art.13)
  - staff training within 6 months of starting, then annually (Art.7(v), Art.30)
  - a published privacy policy (Art.7(j)–(k))
  - updated processor agreements (Art.7(r))

## 13. Enforcement and penalties

- **Compliance orders** (NDPA s.47): a warning, a requirement to comply, or a **cease-and-desist**, which can stop processing.
- **Enforcement orders and sanctions** (s.48):
  - remedy the violation
  - pay compensation
  - account for profits
  - pay a penalty or remedial fee
- **Penalty caps:**

  | Who | Cap | Cite |
  |---|---|---|
  | DCPMI | the **greater of ₦10,000,000 or 2% of annual gross revenue** in the preceding financial year | s.48(3)(a), (4) |
  | Everyone else | the **greater of ₦2,000,000 or 2%** | s.48(3)(b), (5) |

  Factors include gravity, number of subjects, intent or negligence, mitigation, **cooperation**, and the data types involved (s.48(6)).
- **Failing to comply with an order is an offence** (s.49): a fine up to the same caps and/or up to 1 year's imprisonment.
- **Data subjects can sue** for civil remedies (s.51).
- **DPIA failure** may lead to restriction of the controller's platforms (GAID Art.28(6)).

## 14. Citation mistakes to avoid

These are frequently mis-cited (including in commercial tools):
- **Breach notification is s.40**, not s.29. (s.29 covers processor obligations and DPAs.)
- **DPIA is s.28**, not s.35. (s.35 is withdrawal of consent.)
- **Lawful basis is s.25**; principles are s.24.
- **Penalties are s.48** (s.49 is the criminal offence for ignoring orders).
- **CAR comes from GAID Art.10**, not an NDPA section. s.33 licenses DPCOs.
- **Rights are Part VI, ss.34–38**; security is s.39; transfers are ss.41–43; registration is s.44.
