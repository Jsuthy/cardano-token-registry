# STATUS: Tariff refund prospect build

Run date: 2026-09-28. Import-evidence window: rulings dated 2024-09-28 to 2026-09-28.

## Totals

| Stage | Count |
|---|---|
| CBP ruling index entries pulled (Asia-origin keyword searches, NY rulings) | 5,033 |
| Ruling full texts inside the 24-month window | 4,666 |
| Direct-filer letters addressed to a U.S. company (not "on behalf of" a client) | 1,122 |
| Unique direct-filer companies after dedupe and a pre-filter for brokers, law firms and mega-caps | 558 |
| Broker-filed "on behalf of \<client\>" importers, extra pool after dedupe and filtering | 584 |
| Research verdicts written (pass 1, pass 2 re-check, broker pool; includes re-checks) | 1,403 |
| **Kept** (`tariff-refund-prospects.csv`) | **125** |
| **Killed** (`killed.csv`, one row per company) | **1,012** |

The 300-keep cap was not reached. With the "named decision-maker on a cited page + published phone" rule, about 10% of real importers survive. Most small importers publish a phone number but no named executive, and many have no findable website. See "Next steps" below for how to raise volume.

## Killed by reason

| Reason | Count |
|---|---|
| no-name (no qualifying named decision-maker on any fetched page) | 274 |
| out-of-icp-size (public, mega-cap, large-group subsidiary, or too small) | 255 |
| no-website (no verifiable web presence or BBB listing) | 216 |
| foreign-only (foreign manufacturer, or U.S. arm of a large foreign group) | 151 |
| no-phone | 45 |
| individual / hobby / micro shell | 16 |
| not-importer (service firm, nonprofit, etc.) | 13 |
| broker (customs broker, sourcing agent) | 13 |
| other (garbled ruling data, pre-launch, etc.) | 11 |
| site-unreachable (503, DNS failure, bot wall) | 5 |
| forwarder | 5 |
| law-firm | 4 |
| non-asia-origin | 3 |
| weak-import-evidence | 1 |

## Sources: worked vs. blocked

| Source | Result |
|---|---|
| CBP CROSS rulings (`rulings.cbp.gov/api`) | **Worked.** Primary import-evidence source. Free JSON API, no key. |
| Company websites (About / Team / Contact) | **Worked.** Main source for names, titles and phones. Some sites are Cloudflare-walled or return 503. |
| BBB business profiles and BBB search (via fetch tool) | **Worked.** Best fallback for owner/president names and phones. Plain `curl` gets 403. |
| Trade press / press releases (FCNews, Nutraceuticals World, AAM, Home Textiles Today, PR Underground) | Worked, occasionally |
| ImportYeti | **Blocked.** HTTP 403 to both curl and the fetch tool. |
| regulations.gov (Section 301 exclusion dockets) | **Blocked.** Web UI returns 403. The API's free `DEMO_KEY` returned `OVER_RATE_LIMIT`. No paid or registered key was used. |
| Web search tool | **Partly worked.** A shared 200-call session quota ran out partway through pass 1. That caused many false-negative kills, which pass 2 re-checked through BBB search. |
| DuckDuckGo / Bing / Brave / Yahoo HTML via curl | **Blocked or useless.** CAPTCHA, 429, 500, or stale off-topic results. |
| LinkedIn, ZoomInfo, RocketReach, Apollo, D&B, ImportGenius, Panjiva | **Not used** (per brief) |

## QA spot-check (10 random keeps, seed 20260928)

I re-fetched each cited contact page and phone page and re-read each ruling.

| Company | Name + title on cited page | Phone on cited page | Ruling names company, Asia origin | Result |
|---|---|---|---|---|
| Jiaherb, Inc. | ✔ "Scott Chen, president" (Nutraceuticals World, Nov 2024) | ✔ (973) 439-6869 | ✔ N349925, China | Pass |
| eSpecial Needs, LLC | ✔ BBB: Carrie Ann Kouri, Owner | ✔ (877) 664-4565 | ✔ N351121, Taiwan | Pass |
| McIntire Business Products | ✔ "Cyndi Christie, President and Owner" | ✔ (800) 847-2463 | ✔ N354287, Vietnam | Pass |
| Mark Henry Corp. | ✔ "company founder Mois Medine" | ✔ (212) 986-5700 | ✔ N356047, India processing; CBP origin U.S. | Pass. Origin label corrected. |
| Good Life, Inc. | ✔ BBB: Jason Alexander, CEO | ✔ (800) 657-8214 | ✔ N348388, China | Pass |
| Nonin Medical, Inc. | ✔ Jackie Robinson, VP Quality & Operations | ✔ (800) 356-8874 | ✘ The ruling's goods are from an "unidentified country" | **Killed** (weak-import-evidence) |
| PanTim Wood Products | ✔ Harro Jakel, president (FCNews, Jul 2026) | ✔ (207) 799-0010 | ✔ N348114, Thailand | Pass. Note: its distributor business was sold to Havencrest in 7/2026; other channels continue. |
| NOA Medical Industries | ✔ Ray Ganz, CEO | ✔ 1-800-633-6068, normalized to (800) 633-6068 | ✔ N351539, China | Pass |
| Nutritional Products International | ✔ BBB: Mitch Gould, CEO | ✔ | ✘ BBB categorizes it as a marketing consultant (a service firm, not a brand importer) | **Killed** (not-importer) |
| Permco, Inc. | ✔ BBB: Karen Slayko, Controller | ✔ (330) 626-2801 | ✔ N354559, China | Pass |

Follow-up fixes the spot-check triggered:

- The automatic origin detector was tightened. Any keep whose origin was only inferred (not stated in the ruling subject) was re-read by hand. That review killed **Carwild Corporation** (Dominican Republic origin). It also corrected multi-country origin labels on 11 rulings, via `scripts/overrides.json`.
- A "South Korea" matching bug was fixed.
- **Johnny Was** was killed after review: it is a subsidiary of NYSE-listed Oxford Industries.

Automated checks on the final file:

- All 125 phones are in `(XXX) XXX-XXXX` format.
- No duplicate phones or companies.
- Segment, tier and disposition are constant (`CAPE-IEEPA` / `unconfirmed` / `New`).
- Callback, Caller and Call Date are blank.
- Exactly one email is present, copied from the cited page.

`exclude.csv` was not provided, so no exclusion matching was applied.

## Known limitations

- **Size fit** was judged from public signals only, with no revenue data. Treat borderline names as unconfirmed ICP fit: Nexgrill, Horizon Hobby, Kreg Tool, Power Stop, Clearfield, Culp, Woodstream, JLA Home.
- **Contact titles:** some contacts are the company's top executive rather than the import/logistics owner. Purchasing and Trade Compliance titles are treated as supply-chain decision-makers.
- **Import evidence** is a CBP ruling request. It shows intent to import that product from that origin, not a verified shipment count. Where a ruling lists IEEPA 9903.01.xx lines, Notes says so.

## Next steps to raise volume (not done)

- Use a registered free regulations.gov API key to mine Section 301 exclusion dockets. These often name a company contact and phone.
- Take a second pass on the 274 "no-name" kills with more search budget (chamber directories, state SOS officer filings).
- Extend the CBP pull to older rulings, or to additional HTS-chapter searches.
