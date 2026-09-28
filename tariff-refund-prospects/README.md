# Tariff Recovery Today: U.S. importer lead list

Find-and-contact data only. Nothing in this folder sends outreach, dials, writes to a CRM, or calls a paid API.

## Files

| File | What it is |
|---|---|
| `tariff-refund-prospects.csv` | Verified keeps, in the requested 13-column layout. `Segment=CAPE-IEEPA`, `Est Refund Tier=unconfirmed`, `Disposition=New`. Callback, Caller and Call Date are left blank. |
| `killed.csv` | Every candidate that was researched and rejected, with a reason. |
| `STATUS.md` | Counts (scraped, kept, killed by reason) and which sources worked or were blocked. |
| `scripts/` | The pipeline used to build this list (see the re-run recipe). |

## Sources

1. **CBP CROSS rulings** (`rulings.cbp.gov`; public JSON API at `/api/search` and `/api/ruling/<id>`). This was the primary source. A binding ruling request is filed by or for an importer about a specific product and origin, so it is dated, first-party import evidence. Each ruling also gives the product, the HTS code and, often, the IEEPA 9903.01.xx duty lines.
   - *Direct filers.* The letter is addressed to someone at the importer, which gives the company, a named person, and the city and state.
   - *Broker- or attorney-filed.* The ruling names "your client, X Inc." The company comes from the ruling. Contact data has to be found elsewhere.
2. **Company websites** (About, Leadership, Team and Contact pages) for the decision-maker's name and title and the main phone number.
3. **BBB business profiles** (`bbb.org`, public, no login). These list "Business Management" names with titles, plus the business phone. BBB's own search page doubles as a business search engine.
4. **Trade press, press releases and chamber-of-commerce member pages**, only where they state a person's name and title.

**Not used:** LinkedIn, ZoomInfo, RocketReach, Apollo, SignalHire, D&B, paywalled Crunchbase, ImportGenius, Panjiva, or anything behind a login, CAPTCHA or paywall.

**Blocked from this environment:**
- ImportYeti returns HTTP 403 to both curl and the fetch tool.
- regulations.gov returns 403 on the web UI. The API's free `DEMO_KEY` came back `OVER_RATE_LIMIT`, and no key was bought, per the brief.

For both, see `STATUS.md`.

## Kill rules

A row is kept only if **all** of these are verified on a page that was actually fetched:

- **Company name**, for a U.S. mid-market importer, brand or manufacturer (about $5M–$250M, or plausibly multi-container Asia inbound).
- **Named decision-maker**, first and last name, with one of these titles: Owner, Founder, President, CEO, CFO, Controller, COO or VP Operations, or Import / Logistics / Supply Chain / Purchasing / Trade Compliance Manager or Director.
  - The ruling signer is used only when a fetched page shows them with a qualifying title. Otherwise a qualifying executive from the company's own site or BBB profile is used.
  - Purchasing and Trade Compliance roles are counted as "Import / Supply Chain Manager". This is a judgment call; filter on `Title` if you want a stricter list.
- **Phone that rings the company** (main line or direct), published on a cited page, formatted `(XXX) XXX-XXXX`.
- **City and State.**
- **Import evidence URL**, which is the CBP ruling, dated within the last 24 months (on or after 2024-09-28).
- **Asia origin.** The ruling's product is from China, Vietnam, Taiwan, India, Thailand, Malaysia, Indonesia, Cambodia, Korea, Japan, the Philippines, etc. Non-Asia origins are killed as `non-asia-origin`.
- **The person's name appears on the cited contact page** (`contact:` URL in Notes).

Kill reasons used in `killed.csv`:

| Reason | Meaning |
|---|---|
| `no-name` | No qualifying named decision-maker found |
| `no-phone` | No published phone found |
| `no-website` | No verifiable web presence found |
| `forwarder` / `broker` / `law-firm` | Excluded business type |
| `retailer` | Retailer with no import control |
| `individual` | Individual, hobby business or Amazon-only micro shell |
| `out-of-icp-size` | Too large, public mega-cap, or U.S. arm of a large foreign group |
| `foreign-only` | No real U.S. operation |
| `not-importer` | Not a physical-goods importer |
| `non-asia-origin` | Ruling product is not from Asia |
| `non-qualifying-title` | Only non-qualifying titles found |
| `weak-import-evidence` | Ruling does not establish an Asia-origin import |
| `bad-phone-format` | Phone could not be normalized |
| `excluded` | Matched `exclude.csv` |
| `other:*` | Anything else, e.g. site unreachable or garbled ruling data |

**Never invented:** emails appear only when published on the cited page. No dollar refund estimates are made.

`exclude.csv`: none was attached to this run. If `exclude.csv` (columns `Company`, and optionally `Domain`) is placed next to `assemble.py`, rows are matched on normalized company name and killed as `excluded`.

## Dedupe method

- A company key is built by lower-casing the name, stripping legal suffixes (`inc`, `llc`, `corp`, `co`, `ltd`, `company`, `the`, `usa`, `us`, `america`, `group`) and removing non-alphanumerics.
- Rulings are deduped on that key, keeping the most recent ruling per company. The broker-filed pool excludes any key already in the direct-filer pool.
- At assembly, a `keep` from any pass wins over a `kill`, and each company appears once in either the prospects file or `killed.csv`. Keeps are also deduped on (contact name, state). Manual corrections (kills and origin labels) live in `scripts/overrides.json`.

## Re-run recipe

Run from a working directory containing `scripts/`, with Python 3 and outbound HTTPS:

```bash
cd scripts
python3 pull.py China Vietnam Taiwan India Thailand Malaysia Indonesia Cambodia Korea   # ruling index -> index.json
python3 texts.py      # full ruling texts for the last 24 months -> txt/
python3 parse.py      # direct-filer addressee blocks -> cands.csv (filters brokers, law firms, mega-caps)
python3 pool2.py      # broker-filed "on behalf of <client>" importers -> pool2.json
```

1. Change the 24-month cutoff date in `pull.py` / `texts.py` for a new window.
2. Split `cands.csv` (and `pool2.json`) into chunks of about 30. Have a research agent (or a person) follow `agent_prompt.md` / `agent_prompt2.md` for each chunk, appending one JSON line per candidate to `results*/<chunk>.jsonl`.
3. Rebuild the prospect list:

   ```bash
   OUT=.. python3 assemble.py   # validates, dedupes, origin-checks, normalizes phones, and writes the CSVs
   ```

4. Spot-check a random sample of keeps before use. Re-fetch the contact page, confirm the name and title, confirm the phone, and confirm the ruling shows the product and origin.
