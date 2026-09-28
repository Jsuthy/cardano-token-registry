SECOND-PASS lead verification. Follow ALL rules in /tmp/claude-0/-home-user-cardano-token-registry/cad795f2-7b0f-5729-8aaf-8fb5d0646f82/scratchpad/agent_prompt.md (read it first: keep/kill criteria, allowed/banned sources, output JSON format). Research only; never invent data.

These candidates were killed in pass 1 only because web search ran out (reasons no-name / no-website / no-phone / site-unreachable). Fields pass1_website / pass1_phone / pass1_contact hold anything pass 1 already found — reuse but re-verify by fetching. Candidates in the input without a `name` come from broker-filed rulings: the ruling URL is the import evidence; you must find city/state, phone and decision-maker yourself.

SEARCH STRATEGY (WebSearch has a shared quota that may be exhausted — if a WebSearch call errors, stop using it and rely on the methods below):
1. BBB business search via WebFetch (works; curl gets 403):
   https://www.bbb.org/search?find_country=USA&find_text=<Company%20Name>&find_loc=<City>%2C%20<ST>
   (drop find_loc if no hit). Open the matching profile URL with WebFetch and ask for "business phone, address, website, and all names/titles under Business Management / Contact Information / Principal Contacts". BBB profile = valid contact_source_url and phone_source_url.
2. The company website (from BBB profile or pass1_website): about / team / leadership / contact pages.
3. WebSearch only if it still works: "<company> <city> president OR owner OR CEO" — acceptable citation pages: company site, BBB, chamber-of-commerce member pages, press releases, local news/trade pubs, theorg.com. NOT LinkedIn/ZoomInfo/RocketReach/Apollo/Crunchbase/SignalHire/D&B.
Qualifying titles only (Owner, Founder, President, CEO, CFO, Controller, COO/VP Ops, GM/Managing Member of a small co counts as Owner only if the page says owner/managing member, Import/Logistics/Supply Chain/Purchasing/Trade Compliance Manager/Director). A BBB contact listed as "Owner", "President", "CEO", "Managing Member", "Principal" (for an LLC) qualifies.
~6 tool calls per candidate, then move on.

Write one JSON line per candidate to OUTFILE (same schema as pass 1), appending after each candidate.
When done reply only "<N> keeps, <M> kills".
