# Architectural Decision Record: Newsletter & Communications Layer

- **Status:** Documented / Deferred (Zero Code Implemented)
- **Date:** October 2026
- **Context:** Signal Earth is an open-access, static, globe-first environmental data portal maintained by Avnish Singh (undergraduate civil engineering student at HBTU Kanpur).
- **Core Principle:** Zero cookies, zero third-party tracking scripts, zero forms, and zero server-side state.

---

## 1. Architectural Context & Decision

Signal Earth currently operates as a completely static site hosted on Netlify / GitHub Pages. There are no user accounts, no login mechanisms, no marketing funnels, and no telemetry cookies.

Per project specification, **no email signup form or subscription code is built into the website front end**.

This document serves as the formal architectural reference and compliance roadmap should an asynchronous broadcast or notification mechanism be considered in the future.

---

## 2. Infrastructure & Provider Options

If a newsletter or dispatch mechanism is deployed in the future, third-party commercial platforms that inject cross-site trackers or analytics pixels (e.g., Mailchimp, Substack, ConvertKit) are strictly disallowed.

The following privacy-respecting alternatives are evaluated:

| Option | Architecture | Privacy & Tracking Profile | Evaluation & Feasibility |
| :--- | :--- | :--- | :--- |
| **Option A: Self-Hosted Listmonk** (Recommended) | Self-hosted Go binary with PostgreSQL on a sovereign VPS (e.g., Hetzner / Linode in Mumbai/Frankfurt). | 100% first-party control. Pixel tracking and link click tracking can be completely disabled in configuration. | High data sovereignty. Requires ongoing server patching, backup automation, and transactional SMTP configuration. |
| **Option B: Buttondown** | SaaS newsletter service designed for minimalists and developers. | Privacy-first defaults. Supports disabling tracking pixels and link tracking natively. GDPR and privacy compliant. | Minimal operational maintenance. Cost scales with subscriber tiers. Third-party data processor agreement required. |
| **Option C: Serverless Microservice + Postmark / SES** | AWS Lambda / Cloudflare Worker invoking Postmark or Amazon SES via transactional API. | Zero telemetry beyond mail server bounce logs. Full programmatic control over subscriber storage. | High development overhead to maintain unsubscribe lists, suppression tables, and compliance endpoints. |

---

## 3. Double Opt-In Cryptographic Handshake

Any future implementation must enforce a strict double opt-in protocol:

1. **Submission**: Subscriber submits email via an isolated, minimal HTTPS endpoint.
2. **Token Generation**: The server generates a high-entropy, cryptographically secure token (HMAC-SHA256 of the email, timestamp, and a rotating server secret) with a 24-hour expiration.
3. **Pending Quarantine**: The email is stored in a `pending_verification` table with an automatic 48-hour purge TTL. No broadcast emails may be sent to pending addresses.
4. **Confirmation Link**: A plain-text email is transmitted containing a single-use verification URL:
   `https://api.signal-earth.org/subscriptions/confirm?token=<HMAC_TOKEN>`
5. **Activation**: Upon verification link access, the address is transitioned to `active_subscribers`, recording the timestamp and IP address exclusively for audit proof of consent.
6. **One-Click Unsubscribe**: Every outgoing email must contain both:
   - A header compliant with RFC 8058 (`List-Unsubscribe: <https://api.signal-earth.org/subscriptions/unsubscribe?token=...>`, `List-Unsubscribe-Post: List-Unsubscribe=One-Click`).
   - A direct, authentication-free unsubscribe link in the footer.

---

## 4. Privacy Policy Modifications Required Prior to Launch

Deploying an email mechanism would require amending `privacy.html` to establish:

1. **Specific Purpose Limitation**: Clarifying that email addresses are collected solely to deliver dispatches regarding new datasets, research reports, or methodology updates.
2. **Non-Commercial Commitment**: Explicit guarantee that subscriber lists will never be sold, leased, rented, or shared with commercial entities or academic institutions.
3. **Data Retention Schedule**: Immediate deletion of personal records upon receipt of an unsubscribe request or after 12 months of delivery inactivity (hard bounce).
4. **Subprocessor Disclosures**: Full listing of mail transmission subprocessors (e.g., Postmark or EU-based VPS hosting provider) and their jurisdiction.

---

## 5. Regulatory Compliance: India DPDP Act 2023 Obligations

> Note: The analysis below reflects technical architectural planning and does not constitute formal legal counsel. Prior to collecting digital personal data from users under the Digital Personal Data Protection Act, 2023, formal review by qualified legal counsel must be conducted.

As the maintainer is an Indian resident and the primary server operations touch Indian citizens, any collection of digital personal data is governed by the **Digital Personal Data Protection Act, 2023 (DPDP Act)**:

1. **Data Fiduciary Classification**:
   - The maintainer (Avnish Singh) operates as a Data Fiduciary under Section 2(i).
2. **Notice Requirement (Section 5)**:
   - Every request for consent must be accompanied or preceded by an itemized notice in plain language describing the personal data sought, the specific purpose of processing, the manner in which the Data Principal may exercise rights (under Section 6), and the grievance redressal mechanism.
3. **Consent Standard (Section 6)**:
   - Consent must be free, specific, informed, unconditional, unambiguous, and signified through a clear affirmative action.
   - Pre-checked boxes, implied consent, or bundled terms are legally void.
4. **Right to Withdraw Consent (Section 6(4))**:
   - The Data Principal must be able to withdraw consent with the same ease with which it was given.
5. **Data Principal Rights (Sections 11 - 14)**:
   - Right to access a summary of personal data being processed.
   - Right to correction, completion, and erasure of outdated or unnecessary personal data.
   - Right to nominate an individual to exercise rights in the event of death or incapacity.
6. **Technical & Organizational Safeguards (Section 8(5))**:
   - Implementation of encryption in transit (TLS 1.3) and at rest (AES-256).
   - Mandatory personal data breach reporting to the Data Protection Board of India and affected individuals without delay.
7. **Institutional Independence**:
   - The newsletter must explicitly reiterate that Signal Earth is an independent student project and carries no institutional connection to Harcourt Butler Technical University (HBTU) Kanpur.

---

## 6. Final Decision & Status

**Conclusion**: In alignment with the static, low-carbon, trackerless architecture of Signal Earth, no newsletter form will be built into the website. Users wishing to follow research updates are directed to the open, decentralized, trackerless RSS feed located at:
`https://avnish36singh-arch.github.io/signal-earth-portal/notes/feed.xml`
