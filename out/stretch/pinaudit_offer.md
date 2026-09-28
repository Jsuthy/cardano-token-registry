# PinAudit: $197 Google Business Profile fix (STUB)

**Status:** stub. No checkout, no payment link, nothing live. The price is a hypothesis.

**What the buyer gets**
1. The one-page audit (sample PDFs in this folder, built from public Maps data plus the public homepage)
2. Done for you within 7 days, on items the owner approves: categories, services, booking link, profile description, photo plan, a review-request text template, and the click-to-call / booking CTA on the landing page **only if no other agency manages the site**
3. A before/after snapshot of the same query 30 days later

**Price:** $197 one-time, credited toward Master Plan Website Care ($300–750/mo, hypothesis) if they continue within 60 days.

**Who delivers:** Master Plan / Jeff's DFY ops lane. It needs GBP manager access, granted by the owner. No passwords are collected by email.

**Stripe / checkout:** not created (this session had a no-spend, no-live-send rule). Next step: Matt decides whether PinAudit sits under the Master Plan brand, then creates a Payment Link.

## How to make audits
```bash
cd out/stretch
python3 pinaudit.py "Company Name"          # -> audit-<slug>.html (any business in data/maps_raw.jsonl)
node render_pdf.js audit-<slug>.html audit-<slug>.pdf
python3 pick_prospects.py                   # re-pick 10 prospects (5 KC / 5 DFW, one per vertical) and render all
```
`pinaudit_prospects.csv` lists the 10 prospects: shops outside the top 3 for their own search, below the local median review count, and with no GBP booking link. Every one has a phone.
