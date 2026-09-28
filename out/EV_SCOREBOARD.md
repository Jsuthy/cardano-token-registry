# EV Scoreboard: portfolio shootout (2026-09-28)

**Scoring rule:** EV (1–10) = expected dollars Jeff can *pursue* within 14 days, adjusted for how much he'd have to do himself, legal fit, and whether this session can ship a real, sendable asset.
Every price in this file is a **hypothesis** unless marked verified. No price here has been verified with a buyer.

**What this session could actually reach (tested, not assumed):**
- Google Maps listings via headless Chromium: ✅ name, rating, review count, category, address, phone, website.
- Texas TDLR license feed (data.texas.gov `7358-krk7`): ✅ business name, owner name, and county for A/C and Electrical contractors. It has **no phones** for those license types.
- Company websites (plain HTTP): ✅ emails, tech-stack fingerprints, site-quality signals.
- KCMO permit data: ✅ but no contractor names, so it's useless for a lead list.
- US importer lists with a contact name and phone: ❌ no free public source. Bill-of-lading sites show company names only; phone and name need paid data or manual digging.
- LO / realtor emails at scale: ⚠️ possible, but per-row site digging, `.edu` quarantine, and a "no messy CSV" bar make it low-yield.

| # | Idea | Lane | Who pays | Price hypothesis | Time to first $ | Jeff hrs/wk | Buildable this session? | Moat | Main risk | EV | Verdict |
|---|------|------|----------|------------------|-----------------|-------------|-------------------------|------|-----------|----|---------|
| 1 | **Care + AI Ops client factory, KC + DFW trades** (Maps + TDLR + site fingerprint → scored CSV + first-touch drafts) | Masterplan × Matt | Trade owners (5–50 staff) pay Masterplan; Jeff gets rev share or a build fee | Care $300–750/mo; AI Ops/FieldEdge setup $1.5–5k + $500–1.5k/mo | 7–21 days (Matt already sells books/tax to this ICP) | 3–5 (Matt / Jeff call the top tier) | **Yes, fully**: real data, reusable engine | Rerunnable engine; TDLR owner join; FSM-stack detection (FieldEdge/ServiceTitan/HCP/Jobber); SEO-vendor conflict flag | Close depends on Matt's calendar; small accounts churn | **8** | **KEEP: WINNER** |
| 2 | **PinAudit in a box** ($197 GBP audit: public Maps data → PDF) | PinAudit | The same trade owners, or Care as a paid door-opener | $197 one-time; credited toward Care | 3–10 days | 2–3 | **Yes, as a stretch**: reuses #1's Maps engine | Thin alone; strong as the front of #1 | Low ticket; "audit" fatigue | 7 | **KEEP as stretch (feeds #1)** |
| 3 | Tariff refund war room (name + phone CSV factory for IEEPA/CAPE recovery) | TariffsTool / OpenTier | Licensed filer / partner pays per qualified importer, or seat | $150–500/qualified lead, or $1.5–4k/mo seat | 14–45 days (needs a partner seat; refund timing depends on litigation and CBP) | 4–8 | **No, not to bar**: no public name + phone source for importers, and per-row manual digging kills the budget | Timing window | Can't meet campaign-ready (name + phone) from free public data; partner gating | 5 | **KILL for this session.** Revisit with a paid data source (ImportYeti Pro / ZoomInfo trial) or partner-supplied importer lists |
| 4 | LO seat OS (scout pack + geo-exclusivity one-pager for Nate / NAF desk) | Loans by Nate Jones | LOs or the regional desk | $500–2k/seat/mo; $15–80k/mo desk (hypothesis) | 30–60 days: needs Nate's boss meeting | 3–6 | Partly: one-pager yes, clean lists slow | Geo-exclusivity | Big-number pitch with no proof; enterprise cycle | 5 | **KILL now.** Nate should run his current scout loop first; a desk pitch without a 30-day result is vapor |
| 5 | Realtor 3-2-1 engine (research / draft / tracker, human IG taps) | Nate / LO | Nate (paid layer) | $200–250/mo | 7–14 days | 2 | Yes | None | Tiny ticket; one buyer | 4 | **KILL**: ceiling is ~$250/mo |
| 6 | Partner feed v0 (one vertical, ranked, licensed partner delivers), e.g. utility-bill / WC audit partners | Score / recovery | Licensed recovery partner | $1.5–4k/mo | 30–60 days (partner hunt) | 4 | Sample yes; the partner is the gate | Ranking model | No named partner; many earlier spikes died | 4 | **KILL**: no partner in hand |
| 7 | PourDay contractor wedge (concrete subs / ready-mix distribution) | PourDay | Ready-mix plants, concrete subs | $20–100/seat/mo | 30+ days | 3 | Lead list yes; product not changing | Existing app | Sub-scale revenue in 14 days | 3 | **KILL**: EV well below #1 |
| 8 | Site-care portfolio expansion (Decision Pack Care) | Site-care | Existing / new SMB sites | $150–400/mo | 7–14 days | 2 | Folds into #1 (same Care offer) | Process locked | Duplicates #1 | 6 | **MERGE into #1** |
| 9 | Drawback / sales-tax / unclaimed property spikes | Score / recovery | Contingency partners | % of recovery via partner | 60–180 days | 4 | No | None | Jeff can't be principal; long cycle | 2 | **KILL** (already killed; stays dead) |
| 10 | "SEO displacement" of CompletSEO-type vendors | Masterplan | Trades | $1–3k/mo | 60–120 days | 4 | Flag only | — | Dual-edit ban; slow switch | 4 | **PARK**: the factory flags vendor-managed sites and routes them to FieldEdge/ops or Care-later, never to site edits |
| 11 | Wildcard: **FieldEdge / FSM switcher list** (trades whose sites show no online booking or a legacy FSM → AI Ops pitch) | Masterplan | Trades | Setup $1.5–5k | 7–21 days | incl. in #1 | Yes: an `ops_stack_hint` column in #1 | Stack fingerprints | FSM detection only sees what's public | — | **MERGE into #1** (it's a column and a tier driver) |

## Decision
- **Winner: #1, the Masterplan Care + AI Ops client factory (KC + DFW, 5 verticals).** It's the only candidate that (a) has a seller already in the room (Matt), (b) can produce real named accounts with phones by Monday from public data, and (c) leaves Jeff a rerunnable engine. #8 and #11 merge into it.
- **Stretch: #2, PinAudit in a box**, a thin v0 on the same Maps engine. It works as a $197 door-opener into Care.
- **Killed in writing:** #3 tariffs (can't meet the name + phone bar from free data this session; revisit with a paid source or partner list), #4 LO seat OS, #5 realtor, #6 partner feed, #7 PourDay, #9 recovery spikes. #10 is parked.
