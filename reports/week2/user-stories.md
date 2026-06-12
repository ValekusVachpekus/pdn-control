# User Stories

## US-01: Basic website scan

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a small or medium business owner, 
I want to enter my website URL and start a scan, 
so that I can check my site's compliance with FZ-152.

### Notes and constraints
- Supports public HTTP/HTTPS URLs only.
- Initial version may only scan the homepage.

## US-02: Total potential fine display

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a small or medium business owner, 
I want to see the total potential fine amount at the top of the report, 
so that I can immediately understand the financial risk.

### Notes and constraints
- Calculation must be based on current Administrative Code (KoAP RF).

## US-03: Detailed list of violations

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a small or medium business owner, 
I want to see a point-by-point list of violations with the fine cost for each one, 
so that I know what is missing and what it will cost me.

### Notes and constraints
- Each violation should have a human-readable title (e.g., "Missing Privacy Policy").

## US-04: Legal article references

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a small or medium business owner, 
I want each violation to reference the specific article of FZ-152 it relates to, 
so that I can understand the legal basis for each finding.

### Notes and constraints
- References should be kept up to date with the latest legal amendments.

## US-05: Free tier limited check

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a free-tier user, 
I want to run a limited check (e.g., homepage only), 
so that I can get a basic idea of my compliance without paying.

### Notes and constraints
- Results might be blurred or restricted until the user upgrades.

## US-06: Paid tier full analysis

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a paid-tier user, 
I want a full crawl and analysis of my entire site, 
so that I receive a complete and detailed compliance report.

### Notes and constraints
- Requires integration with a payment gateway (e.g., YooKassa or Stripe).

## US-07: Compliance score (0-100)

**Requirement Status:** Active
**MoSCoW priority:** Must Have

As a small or medium business owner, 
I want to see a 100-point compliance score, 
so that I can quickly understand how serious my site's overall risk level is.

### Notes and constraints
- Score formula: 100 minus weighted penalties for each violation.
- **Priority raised from `Should Have` to `Must Have`** at the customer's request during the Week 2 review (2026-06-12): the score must carry equal weight with the total fine (US-02) and be shown next to it on the result screen with the same visual emphasis. See `customer-meeting-summary.md`.
- Kept out of the initial proposed MVP v1 scope below: the customer-approved scope (US-01–US-05) was left unchanged at this review; US-07 is prioritized as Must Have for delivery by the end of the course but is not part of the first prototyped slice.

## US-08: PDF Report Download

**Requirement Status:** Active
**MoSCoW priority:** Should Have

As a small or medium business owner, 
I want to download a professionally designed PDF report, 
so that I can share it with my team or use it for legal reference.

### Notes and constraints
- PDF must include the scan timestamp and a summary of all findings.

## US-09: Multi-page and JS crawling

**Requirement Status:** Active
**MoSCoW priority:** Could Have

As a small or medium business owner, 
I want the scanner to crawl the entire site and execute JS scripts, 
so that dynamic pages, SPAs, and cookie banners are also analyzed.

### Notes and constraints
- Technically complex; may significantly increase scan duration.

## US-10: Captcha block notification

**Requirement Status:** Active
**MoSCoW priority:** Could Have

As a small or medium business owner, 
I want to receive a notification if a captcha blocks the scan, 
so that I know which pages could not be fully analyzed.

### Notes and constraints
- Scanner will not attempt to bypass captchas (out of scope).

## US-11: Automatic AI code remediation

**Requirement Status:** Active
**MoSCoW priority:** Won't Have

As a small or medium business owner, 
I want the tool to automatically fix my website's code to resolve violations, 
so that I don't have to do it manually.

**Reason:** This feature is excluded due to high technical risk, potential security concerns related to modifying user source code, and the complexity of integrating with various CMS platforms.

---

## Initial proposed MVP v1 scope

The following stories are selected for the initial MVP v1:
- US-01: Basic website scan
- US-02: Total potential fine display
- US-03: Detailed list of violations
- US-04: Legal article references
- US-05: Free tier limited check