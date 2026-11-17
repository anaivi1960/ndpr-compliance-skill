#!/usr/bin/env python3
"""
NDPA signal scanner: a fast, dependency-free first pass over a codebase.

It finds *signals*, not verdicts: places where personal data, trackers,
third-party processors, foreign hosting regions, PII logging, consent
defaults, retention jobs and data-subject-rights features probably live.
The agent then reads those files to confirm or dismiss each one.

Usage:
    python scan_signals.py <repo_path> [--json] [--max-per-rule N]

Python 3.8+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "out",
    "coverage", "__pycache__", ".venv", "venv", "env", ".tox", "target", ".gradle",
    "Pods", ".turbo", ".cache", ".svelte-kit", ".expo", "bower_components",
    "test-results", "playwright-report", ".terraform",
}
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock",
    "Cargo.lock", "composer.lock", "Gemfile.lock", "go.sum",
    "NDPA-COMPLIANCE-REPORT.md",
}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".py", ".rb", ".php", ".go", ".java", ".kt", ".kts", ".swift", ".dart", ".cs",
    ".rs", ".scala", ".ex", ".exs", ".sql", ".prisma", ".graphql", ".gql",
    ".html", ".htm", ".ejs", ".hbs", ".erb", ".twig", ".jinja", ".j2",
    ".json", ".yaml", ".yml", ".toml", ".tf", ".hcl", ".xml", ".plist", ".gradle",
    ".env", ".example", ".md", ".mdx", ".txt", ".ini", ".cfg", ".conf",
}
MAX_BYTES = 1_000_000

# (rule_id, group, description, regex, flags)
RULES = [
    # --- Personal data fields (inventory) ---
    ("pii.ng_identifier", "inventory", "Nigerian national/financial identifier (BVN, NIN, TIN, voter/driver/passport no.)",
     r"\b(bvn|nin|national_?id(entification)?(_?number)?|voters?_?(card|id)|drivers?_?licen[cs]e|passport_?(no|number)|\btin\b|tax_?id)\b", re.I),
    ("pii.contact", "inventory", "Contact data (email, phone, address)",
     r"\b(email(_?address)?|phone(_?number)?|msisdn|mobile(_?number)?|home_?address|street_?address|residential_?address)\b", re.I),
    ("pii.dob_age", "inventory", "Date of birth / age (possible child data, s.31)",
     r"\b(date_?of_?birth|dob|birth_?date|birthday|is_?minor|under_?18|guardian|parental_?consent)\b", re.I),
    ("pii.financial", "inventory", "Financial data (card, account, bank)",
     r"\b(card_?number|\bpan\b|cvv|cvc|account_?number|acct_?no|iban|bank_?account|bank_?code|sort_?code)\b", re.I),
    ("pii.location", "inventory", "Location data",
     r"\b(latitude|longitude|geo_?location|gps|lat_?lng|current_?location)\b", re.I),
    ("pii.device", "inventory", "Online identifiers (IP, device ID, advertising ID)",
     r"\b(ip_?address|remote_?addr|x-forwarded-for|device_?id|advertising_?id|idfa|gaid|fingerprint_?js|fingerprintjs)\b", re.I),
    ("sensitive.biometric", "sensitive", "Biometric data (s.65 sensitive)",
     r"\b(biometric|finger_?print|face_?(id|match|template|embedding|print)|selfie|liveness|facial_?(recognition|verification))\b", re.I),
    ("sensitive.health", "sensitive", "Health data (s.65 sensitive)",
     r"\b(health|medical|diagnos(is|es)|blood_?(group|type)|genotype|hiv|disabilit(y|ies)|allerg(y|ies)|prescription|pregnan(t|cy)|patient)\b", re.I),
    ("sensitive.beliefs_origin", "sensitive", "Religion / ethnicity / state of origin (s.65 sensitive or proxy)",
     r"\b(religion|religious|ethnic(ity)?|tribe|race|state_?of_?origin|lga_?of_?origin)\b", re.I),
    ("sensitive.other", "sensitive", "Sex life / political / trade union (s.65 sensitive)",
     r"\b(sexual_?orientation|sex_?life|political_?(party|affiliation|opinion)|trade_?union)\b", re.I),

    # --- Trackers (GAID Art.19) ---
    ("tracker.analytics", "trackers", "Analytics / ads / session-replay tracker",
     r"(googletagmanager\.com|google-analytics\.com|gtag\(|\bfbq\(|connect\.facebook\.net|analytics\.tiktok\.com|ttq\.|hotjar|clarity\.ms|mixpanel|segment\.(com|io)|analytics\.js|amplitude|posthog|fullstory|logrocket|heap\.io|smartlook|mouseflow|@vercel/analytics|plausible|matomo|branch\.io|appsflyer|adjust\.com|firebase/analytics|firebase-analytics)", re.I),
    ("tracker.cookie_write", "trackers", "Direct cookie / storage writes (check purpose)",
     r"(document\.cookie\s*=|setCookie\(|cookies\(\)\.set|res\.cookie\(|set_cookie\(|localStorage\.setItem)", 0),
    ("consent.banner_lib", "consent", "Cookie-consent library / banner component",
     r"(cookieconsent|cookie-consent|cookiebot|onetrust|osano|klaro|react-cookie-consent|vanilla-cookieconsent|CookieBanner|ConsentBanner|consent_?mode|gtag\('consent')", re.I),

    # --- Consent defaults (s.26(7)) ---
    ("consent.prechecked", "consent", "Possibly pre-selected consent/marketing option (s.26(7)(a))",
     r"((marketing|newsletter|consent|opt_?in|subscribe|promo|share_?data|terms)\w*[^\n]{0,80}(defaultChecked|checked\s*=\s*\{?\s*true|default\s*[:=]\s*true|default\s*=\s*True|initialValue\s*:\s*true|@default\(true\)))|((defaultChecked|checked\s*=\s*\{?\s*true)[^\n]{0,80}(marketing|newsletter|consent|opt_?in|subscribe|promo))", re.I),
    ("consent.bundled", "consent", "Bundled / implied consent wording (s.26(2), s.26(3))",
     r"(by (continuing|signing up|registering|using|creating an account|clicking)[^\n]{0,60}(you )?(agree|consent|accept)|(agree|consent)[^\n]{0,40}(share|sharing)[^\n]{0,30}(partners|third[ -]part))", re.I),

    # --- Third parties / processors (s.29, ss.41-43) ---
    ("tracker.session_replay", "trackers", "Session-replay / keystroke recording (can capture BVN, card, passwords; check input masking)",
     r"(hotjar|clarity\.ms|fullstory|logrocket|smartlook|mouseflow|session_?replay|sessionRecording|record_?sessions|posthog[^\n]{0,80}(record|session)|replaysSessionSampleRate|replayIntegration)", re.I),
    ("thirdparty.processor", "third_parties", "Third-party processor SDK / API",
     r"\b(sendgrid|mailgun|resend|postmark|mailchimp|brevo|sendinblue|twilio|termii|africastalking|vonage|paystack|flutterwave|stripe|monnify|interswitch|remita|smile_?id|smileidentity|dojah|prembly|youverify|qoreid|verifyme|mono\.co|withmono|okra|hubspot|intercom|zendesk|freshdesk|crisp|salesforce|zoho|openai|anthropic|generativelanguage|gemini|cohere|mistral|replicate|huggingface|cloudinary|uploadthing|pusher|onesignal|firebase|supabase|algolia|sentry|datadog|newrelic|bugsnag|rollbar|auth0|clerk|okta)\b", re.I),
    ("thirdparty.llm_prompt_pii", "third_parties", "LLM call possibly including user data (check prompt contents)",
     r"(chat\.completions\.create|messages\.create|generateText|streamText|generateContent|responses\.create)", 0),

    # --- Hosting regions (cross-border) ---
    ("transfer.region", "transfers", "Cloud region outside Nigeria (s.41). Note this may be compute only; also check DB/storage host strings and each SaaS processor's location",
     r"\b((us|eu|ap|sa|ca|me|af|il|mx)-(east|west|central|north|south|southeast|northeast|northwest|southwest)-\d|(us|europe|asia|australia|africa|southamerica|northamerica|me)-(central|east|west|north|south|southeast|northeast)\d|(eastus|westus|westeurope|northeurope|southafricanorth|uksouth|ukwest)\d?|\b(iad1|sfo1|cle1|pdx1|fra1|lhr1|cdg1|arn1|dub1|hnd1|icn1|sin1|syd1|gru1|cpt1|bom1|hkg1|kix1)\b)", re.I),

    # --- Logging of PII (s.24(1)(f), s.39) ---
    ("security.pii_logging", "security", "Logging that may include personal data",
     r"(console\.(log|info|debug|warn|error)|logger\.(info|debug|warn|error|log)|log\.(info|debug|warn|error)|print\(|logging\.(info|debug|warning|error)|Log\.(d|i|e|w))[^\n]{0,120}\b(req\.body|request\.body|user\b|email|phone|bvn|nin|password|payload|customer|profile|card|address|dob)", re.I),
    ("security.sentry_pii", "security", "Error tracker configured to send default PII",
     r"(sendDefaultPii\s*:\s*true|send_default_pii\s*=\s*True)", 0),
    ("security.weak_hash", "security", "Weak hash (check if used for passwords/IDs)",
     r"\b(md5|sha1)\s*\(|createHash\(\s*['\"](md5|sha1)['\"]|hashlib\.(md5|sha1)\(", re.I),
    ("security.strong_hash", "security", "Password hashing library (good signal)",
     r"\b(bcrypt|argon2|scrypt|passlib|pbkdf2)\b", re.I),
    ("security.tls_disabled", "security", "TLS verification disabled",
     r"(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true)", 0),
    ("security.hardcoded_secret", "security", "Possible hard-coded secret",
     r"((sk|pk)_(live|test)_[0-9a-zA-Z]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,}|ghp_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9_-]{30,})", 0),
    ("security.public_bucket", "security", "Public object storage / ACL",
     r"(public-read|acl\s*[:=]\s*['\"]public|PublicRead|allUsers|block_public_acls\s*=\s*false|public\s*:\s*true[^\n]{0,40}bucket)", re.I),
    ("security.encryption", "security", "Field/app-level encryption (good signal)",
     r"\b(encrypt|decrypt|createCipheriv|AES|kms|fernet|pgcrypto|crypto\.subtle)\b", 0),

    # --- Rights (Part VI) ---
    ("rights.export", "rights", "Data export / access (s.34, s.38)",
     r"\b(export_?(my_?)?data|data_?export|download_?(my_?)?data|dsar|subject_?access|takeout|portability)\b", re.I),
    ("rights.delete", "rights", "Account / data deletion (s.34(1)(d))",
     r"\b(delete_?account|deleteAccount|account_?deletion|close_?account|erase|erasure|right_?to_?be_?forgotten|anonymi[sz]e)\b", re.I),
    ("rights.soft_delete", "rights", "Soft delete (check there is a purge job)",
     r"\b(deleted_?at|deletedAt|is_?deleted|isDeleted|paranoid\s*:\s*true|SoftDeletes)\b", 0),
    ("rights.unsubscribe", "rights", "Unsubscribe / marketing opt-out (s.36(3))",
     r"\b(unsubscribe|opt_?out|optOut|suppression|List-Unsubscribe)\b", re.I),

    # --- Retention (s.24(1)(d), GAID Art.49) ---
    ("retention.job", "retention", "Retention / purge mechanism",
     r"\b(retention|purge|ttl|expireAfterSeconds|expire_?at|expires_?at|lifecycle_?rule|LifecycleConfiguration|cleanup|prune)\b", re.I),
    ("retention.scheduler", "retention", "Scheduled job definition (check what it does)",
     r"(\bcron\b|node-cron|@Cron\(|schedule\.every|celery\.beat|crontab|\"crons\"|vercel\.json)", re.I),

    # --- Breach readiness (s.40) ---
    ("breach.incident", "breach", "Incident / breach handling artefact",
     r"\b(incident_?response|breach_?(log|register|notification|record)|security_?incident|data_?breach|ndpc)\b", re.I),
    ("breach.audit_log", "breach", "Audit log of access (helps scope a breach)",
     r"\b(audit_?log|auditLog|AuditTrail|activity_?log|access_?log)\b", re.I),

    # --- Automated decisions (s.37) ---
    ("adm.decision", "automated_decisions", "Possible automated decision / scoring",
     r"\b(credit_?score|risk_?score|fraud_?score|auto_?(approve|reject|decline)(d|ed|s)?|eligibility|underwrit\w*|scoring_?model|kyc_?(status|decision)|loan_?decision)\b", re.I),

    # --- Mobile permissions / disclosures ---
    ("mobile.permission", "mobile", "Mobile permission / usage description",
     r"(android\.permission\.(ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|READ_CONTACTS|READ_SMS|RECORD_AUDIO|CAMERA|READ_CALL_LOG|READ_PHONE_STATE)|NS(Location\w*|Contacts|Camera|Microphone|PhotoLibrary|UserTracking)UsageDescription)", 0),

    # --- Governance docs ---
    ("docs.privacy", "governance_docs", "Privacy policy / notice reference",
     r"\b(privacy_?policy|privacy-policy|privacy_?notice|cookie_?policy|cookie-policy)\b", re.I),
    ("docs.governance", "governance_docs", "DPIA / ROPA / DPA / retention schedule reference",
     r"\b(dpia|data_?protection_?impact|privacy_?impact|ropa|record_?of_?processing|data_?processing_?agreement|\bdpa\b|retention_?schedule|transfer_?impact)\b", re.I),
]

# Identifier-aware word boundary: treats "_" and camelCase humps as separators,
# so `selfieUrl`, `user_bvn` and `dateOfBirth` all match.
_B = r"(?:(?<![A-Za-z0-9])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?![A-Za-z0-9]))"
_CAMEL = re.compile(r"([a-z0-9])([A-Z])")


def _split_camel(line):
    return _CAMEL.sub(r"\1_\2", line)


COMPILED = [(rid, grp, desc, re.compile(rx.replace(r"\b", _B), fl)) for rid, grp, desc, rx, fl in RULES]
_CASE_INSENSITIVE = {rid for rid, _, _, _, fl in RULES if fl & re.I}

# Rules that are about presence/absence (summarised by file count, fewer snippets).
PRESENCE_GROUPS = {"rights", "retention", "breach", "governance_docs", "consent"}


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in {".github", ".env"}]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXT_EXT and not name.startswith(".env") and name not in {"Dockerfile", "Procfile"}:
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


_SECRET_RX = re.compile(
    r"((?:sk|pk|rk)[-_][A-Za-z0-9_-]{6,}|AKIA[0-9A-Z]{16}|gh[pousr]_[0-9A-Za-z]{20,}|xox[baprs]-[0-9A-Za-z-]{10,}"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"
    r"|(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s'\"]+)"
)
_ASSIGN_RX = re.compile(r"((?:secret|token|password|passwd|api_?key|private_?key)[A-Za-z0-9_]*\s*[:=]\s*['\"]?)([^'\"\s,;]{6,})", re.I)


def redact(text):
    """Never echo credentials: the scan output ends up in an LLM context and in reports."""
    text = _SECRET_RX.sub(lambda m: m.group(0)[:4] + "…[REDACTED]", text)
    return _ASSIGN_RX.sub(lambda m: m.group(1) + "[REDACTED]", text)


def is_minified(line):
    return len(line) > 400


def scan(root, max_per_rule):
    hits = defaultdict(list)
    counts = defaultdict(int)
    files_by_rule = defaultdict(set)
    scanned = 0
    for path in iter_files(root):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        scanned += 1
        for lineno, line in enumerate(lines, 1):
            if is_minified(line):
                continue
            split = _split_camel(line)
            for rid, grp, desc, rx in COMPILED:
                if rx.search(line) or (rid in _CASE_INSENSITIVE and rx.search(split)):
                    counts[rid] += 1
                    files_by_rule[rid].add(rel)
                    if len(hits[rid]) < max_per_rule:
                        hits[rid].append({"file": rel, "line": lineno, "text": redact(line.strip()[:200])})
    return scanned, hits, counts, files_by_rule


def to_markdown(root, scanned, hits, counts, files_by_rule):
    out = [f"# NDPA signal scan: `{os.path.abspath(root)}`", "",
           f"Scanned {scanned} text files. These are **signals to investigate**, not findings. "
           "Read each file before drawing conclusions.", ""]
    groups = []
    for rid, grp, desc, _ in COMPILED:
        if grp not in groups:
            groups.append(grp)
    absent = []
    for grp in groups:
        rules = [(rid, desc) for rid, g, desc, _ in COMPILED if g == grp]
        section = []
        for rid, desc in rules:
            n = counts.get(rid, 0)
            if n == 0:
                absent.append(f"`{rid}`: {desc}")
                continue
            nfiles = len(files_by_rule[rid])
            section.append(f"### `{rid}`: {desc}\n{n} matches in {nfiles} files.")
            limit = 5 if grp in PRESENCE_GROUPS else None
            shown = hits[rid][:limit] if limit else hits[rid]
            for h in shown:
                section.append(f"- `{h['file']}:{h['line']}`: `{h['text'].replace('`', ' ')}`")
            section.append("")
        if section:
            out.append(f"## {grp}")
            out.extend(section)
    if absent:
        out.append("## No matches. Absence is NOT a pass: no deletion, retention, consent banner or privacy notice signal is often a finding; confirm by reading the code")
        out.extend(f"- {a}" for a in absent)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    ap.add_argument("--max-per-rule", type=int, default=25)
    args = ap.parse_args()
    if not os.path.isdir(args.root):
        sys.exit(f"not a directory: {args.root}")
    scanned, hits, counts, files_by_rule = scan(args.root, args.max_per_rule)
    if args.json:
        print(json.dumps({
            "root": os.path.abspath(args.root),
            "files_scanned": scanned,
            "rules": {rid: {"group": grp, "description": desc, "matches": counts.get(rid, 0),
                            "files": sorted(files_by_rule.get(rid, [])), "samples": hits.get(rid, [])}
                      for rid, grp, desc, _ in COMPILED},
        }, indent=2))
    else:
        sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
        print(to_markdown(args.root, scanned, hits, counts, files_by_rule))


if __name__ == "__main__":
    main()
