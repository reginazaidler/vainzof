# Mobile button clickability check (manual automation)

Date: 2026-03-14
Environment: local static server (`python3 -m http.server 4173`) + Playwright Firefox mobile viewport (390x844).

## Scope
Tested `index.html` in a mobile viewport and attempted to click all detected button-like elements:
- `button`
- links with classes containing `btn`, `button`, `cta`
- phone/mail/WhatsApp protocol links
- `[role="button"]`

## Result summary
- Elements detected: **15**
- Clearly clickable / actionable: **9**
- Not clickable in current mobile flow: **6**

## Non-clickable items observed
1. `052-4520222` (`tel:` link) — hidden in current state.
2. `לתיאום בדיקה אישית` — hidden in current state.
3. `לתיאום בדיקה אישית` — click timeout (likely covered by overlay or not interactable at that moment).
4. `לתיאום בדיקה אישית` — click timeout (likely covered by overlay or not interactable at that moment).
5. Empty-text button-like element — hidden in current state.
6. `שלחו צילום לבדיקה בוואטסאפ` — hidden in current state.

## Notes
- Some failures are due to **visibility/state**, not necessarily broken links.
- Re-testing after explicitly opening/closing modal states may reduce false negatives.
