You are verifying U.S. importer sales leads. Research only: do NOT contact anyone, submit forms, or pay for anything. Never invent data — if you cannot verify a field on a real page you fetched, it does not exist.

INPUT: a JSON file of candidates. Each is a U.S. company that personally requested a CBP tariff ruling (rulings.cbp.gov, last 24 months) for a product imported from China/Asia. `url` is the import-evidence URL; `name` is the person who signed the ruling request (title unknown).

For EACH candidate, decide KEEP or KILL.

KEEP requires ALL of:
1. Company is a U.S. mid-market importer/brand/manufacturer (~$5M–$250M revenue, or plausibly multi-container Asia inbound). KILL if: freight forwarder, customs broker, 3PL, law/consulting firm, tariff-recovery firm, retailer that doesn't control its own imports, Amazon-only shell, one-person hobby/individual, or a large public/Fortune-1000-scale company or a U.S. subsidiary of a large foreign conglomerate (reason "out-of-icp-size"). Also KILL if not a physical-goods importer in any sensible vertical.
2. A named decision-maker (first + last name) with one of these titles: Owner, Founder/Co-Founder-Owner, President, CEO, CFO, Controller, COO/VP Operations, Import/Logistics/Supply Chain/Trade Compliance Manager or Director (or VP of those). Take title ONLY from a page you fetched (company About/Leadership/Team/Contact page, press release, trade pub, association directory, state business filing). The ruling signer counts ONLY if a fetched page shows them with a qualifying title. Otherwise use another person from the company's own site. NO LinkedIn, ZoomInfo, RocketReach, Apollo, Crunchbase-paywalled, or other paid/login databases.
3. A phone number that rings the company (main line or direct), published on a fetched page (normally the company website contact page/footer). Format as (XXX) XXX-XXXX (add ext if shown). Toll-free OK.
4. The decision-maker's name appears on a page you cite (contact_source_url).

Tools: use WebSearch to find the company website, then WebFetch (or `curl -sL -A "Mozilla/5.0"` via Bash if WebFetch fails) for the homepage / about / team / contact pages. Spend at most ~6 tool calls per candidate; if nothing turns up, KILL with the right reason and move on. Skip anything behind login/CAPTCHA/paywall.

Email: only if it's published on a page you fetched AND belongs to the named person or is clearly theirs; else "".

OUTPUT: append one JSON object per candidate (one per line) to OUTFILE, writing as you go (after each candidate) using Bash `cat >> OUTFILE <<'EOF' ... EOF` or python. Fields:
{"ruling":..., "company": "<official company name>", "status":"keep"|"kill", "reason": "<if kill: no-name | no-phone | no-website | forwarder | broker | law-firm | retailer | out-of-icp-size | not-importer | individual | foreign-only | other:<short>>", "city":..., "state":..., "phone":"(xxx) xxx-xxxx", "contact_name":"First Last", "title":"...", "email":"", "website":"https://...", "contact_source_url":"<page where name+title appear>", "phone_source_url":"<page where phone appears>", "vertical":"<auto parts|hardware/fasteners|housewares|apparel/softgoods|medical supplies|pet|packaging|chem/plastics|electronics accessories|sporting goods|furniture/home decor|ag equipment parts|HVAC components|toys/games|other:...>", "import_signal":"<country, product, HTS, ruling date — from input>", "evidence_url":"<input url>"}
Use the company's HQ city/state if the site shows it; otherwise the ruling's.

When done, reply with just: "<N> keeps, <M> kills" for your file.

ADDENDUM (important, raises yield): BBB business profiles (bbb.org/us/<st>/<city>/profile/...) are an allowed public source. Fetch them with WebFetch (curl gets 403). They list "Business Management" names with titles (e.g. "Mr. John Smith, President") and the business phone. If the company site lacks a named decision-maker, find the BBB profile (WebSearch "<company> <city> bbb", or WebFetch https://www.bbb.org/search?find_text=<company>&find_loc=<City>%2C%20<ST>) and use it as contact_source_url (and phone_source_url if needed). Title must still qualify (Owner/President/CEO/CFO/Controller/VP Ops/COO/Import-Logistics-Supply Chain Mgr). Also allowed: state Secretary of State / public business-filing pages that show officer name + title, if not behind CAPTCHA.
