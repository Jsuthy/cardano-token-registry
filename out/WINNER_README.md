# Winner: Masterplan Care + AI Ops client factory (KC + DFW trades)

A rerunnable engine that turns **public** data into a scored, callable list of HVAC, plumbing, electrical, roofing and GC shops in Kansas City and DFW. Each row carries the evidence behind its pitch.

## What's in the box
| Path | What it is |
|------|-----------|
| `data/leads_scored.csv` | **Main deliverable.** The 40/60 KC/DFW cut, balanced across verticals, in the required schema |
| `data/combined-top100.csv` | Top 40 KC + top 60 DFW: call these first |
| `data/first_touch_drafts.csv` | Email draft + call opener per top-100 row, with a `hook_evidence` column. **DRAFTS, NOT SENT** |
| `data/leads_all_scored.csv` | Every in-scope unique business, scored (includes franchises and 1–4-person shops excluded from the cut) |
| `data/maps_raw.jsonl` | Raw Maps results (name, phone, site, rating, reviews, categories, GBP booking link, lat/lng, place_id) |
| `data/site_enrichment.jsonl` | Per-website findings: emails, FSM / marketing / CMS / SEO-vendor fingerprints, quality notes |
| `data/tdlr_dfw_contractors.json` | Texas TDLR public license records (A/C + Electrical contractors, 9 DFW counties) |
| `data/queries.tsv` | The query grid (2 metros × 5 verticals × 10–14 cities) |
| `scripts/` | The engine (below) |
| `offer-or-pitch.md` | One-page offer + call script for Matt |

## Rerun it (about 45 minutes end to end, $0)
```bash
cd out/scripts
python3 build_queries.py ../data/queries.tsv            # edit cities/verticals here (e.g. add Tulsa / OKC)
python3 maps_engine.py ../data/queries.tsv ../data/maps_raw.jsonl 2   # resumable; 2 pages = up to 40/query
python3 tdlr_pull.py ../data/tdlr_dfw_contractors.json   # Texas only
python3 enrich_sites.py ../data/maps_raw.jsonl ../data/site_enrichment.jsonl   # resumable
TARGET_TOTAL=500 python3 build_leads.py
python3 first_touch.py
```
Requires only Python 3 and `requests`.
`maps_engine.py` replays the same public `/search?tbm=map` request the Maps web page makes, with no login and no API key. If Google changes the request format, recapture `maps_pb_template.txt`: open Maps in any browser, search once, copy the `search?tbm=map` request URL from DevTools, and swap in `plumber+Denton+TX` as the query.

## How rows are scored (0–100)
| Component | Points | Logic (hypothesis: tune after 20 calls) |
|---|---|---|
| Size fit (5–50 staff proxy) | 0–30 | Google review count: 100–1,200 → 30; 40–99 → 22; 1,201–2,500 → 18; 15–39 → 12; else 5 |
| Care opportunity | 0–25 | Weak-site signals (no HTTPS, no viewport, no click-to-call, no schema, weak title, no meta description, stale © year, no booking CTA). No website → 14 |
| AI Ops opportunity | 0–20 | No FSM detected → 20; FieldEdge → 18 (Matt's near-term angle); Housecall Pro / Jobber / Successware etc. → 12; ServiceTitan → 6 |
| Contact path | 0–15 | Phone 5, email 5, named contact 5 |
| Reputation health | 0–10 | ≥4.5★ → 10; ≥4.0 → 7; else 4 |
| Penalties | −15 / −5 | Franchise or national brand −15 (excluded from the cut); active SEO/web vendor −5 |

Tiers: **A ≥ 80, B 68–79, C < 68.**

## Honesty labels
- **Verified (public source, cited per row):** company name, phone, website, rating, reviews, categories (Google Maps, `source_url`); emails (published on the company's own site); contact names (either the **TDLR public license holder**, or a person the company's site names as Owner/President/Founder; the `notes` column says which).
- **Hypothesis:** `employee_band` (inferred from review volume, not a headcount); `ops_stack_hint` "no FSM detected" (it means nothing *public*: many shops run ServiceTitan or FieldEdge with no website widget); all prices in the offer.
- **Not done:** no emails were guessed or pattern-built (no `first.last@` inference), nothing was sent, and no paid data was used.
- **TDLR name join** is exact-match on the normalized business name. A license holder can be the qualifying technician rather than the owner, so confirm on the call ("Is [Name] still the license holder there?").
- **Website owner names** come from a regex over "Name, Owner" / "Owner: Name" patterns. Spot-check before using a first name in an email.

## Compliance guardrails baked in
- The `site_quality_notes` column flags SEO/web-vendor footprints (Scorpion, Blue Corona, Contractor Commerce, Hibu, Thryv, …) with "NO site edits while vendor active". The first-touch drafts switch to an ops-only pitch for those rows.
- Drafts include CAN-SPAM placeholders (physical address, opt-out). Send from Master Plan's domain, as Matt or a Master Plan rep, **not as Jeff**.
