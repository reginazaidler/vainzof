# Security Review (Static Website)

Date: 2026-03-14
Repository: `vainzof`

## Scope
A static review of the HTML/CSS site was performed, focused on common client-side/security-hardening risks:
- Third‑party script/style loading
- Link safety (`target="_blank"` + rel attrs)
- Mixed content
- Form handling and data submission
- Browser hardening headers/tags that can be controlled from HTML

## Findings

### 1) Third‑party scripts are loaded from CDNs without integrity pinning
**Severity:** Medium  
**Evidence:**
- Google Analytics script from `googletagmanager.com` in page heads.
- Tailwind runtime CDN script (`https://cdn.tailwindcss.com`) in page heads.

**Risk:** If a third‑party CDN or dependency path is compromised, malicious JavaScript could execute in visitors' browsers.

**Recommendation:**
- Prefer self-hosted, version-pinned assets built at deploy time.
- If using external scripts that support immutable versioning, add `integrity` + `crossorigin` attributes.

---

### 2) Missing Content Security Policy (CSP)
**Severity:** Medium  
**Evidence:** No CSP found in HTML via `<meta http-equiv="Content-Security-Policy" ...>`.

**Risk:** Increases impact of potential XSS/injected content because the browser has fewer execution restrictions.

**Recommendation:**
- Configure CSP as an HTTP response header at hosting level (preferred).
- As a partial fallback for static hosting, add a meta CSP and progressively tighten policy.

---

### 3) Missing explicit Referrer-Policy and Permissions-Policy
**Severity:** Low  
**Evidence:** No hardening meta/headers found for these policies.

**Risk:** More metadata may be shared to third parties than needed; browser features may be less constrained.

**Recommendation:**
- Set `Referrer-Policy: strict-origin-when-cross-origin`.
- Set a restrictive `Permissions-Policy` header (disable unused APIs).

---

### 4) Contact form posts directly to Formspree (third-party processor)
**Severity:** Low (security) / Medium (privacy & abuse resilience)  
**Evidence:** Forms submit with `fetch('https://formspree.io/f/mdawkwwn', { method: 'POST', body: new FormData(form) })`.

**Risk:**
- Client-side validation can be bypassed.
- Potential spam abuse if endpoint is discovered.
- Data handling depends on third-party processor policy.

**Recommendation:**
- Add anti-abuse controls (honeypot/CAPTCHA/rate limiting if supported).
- Ensure Formspree project uses allowed-origin restrictions.
- Document privacy handling and retention.

## Positive Checks
- No obvious `eval`, `document.write`, or inline DOM sinks like `innerHTML` detected in scanned files.
- External links with `target="_blank"` were found to include `rel="noopener noreferrer"`.
- No insecure `http://` application links detected (excluding SVG XML namespace declarations).

## Suggested Next Actions (Priority)
1. Move away from runtime Tailwind CDN to a local compiled CSS build.
2. Add CSP (header-level preferred) and test for breakages.
3. Add `Referrer-Policy` and `Permissions-Policy` at host config.
4. Harden Formspree intake against spam/abuse and verify privacy disclosures.
