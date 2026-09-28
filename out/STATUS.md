# STATUS: 2026-09-28 (session complete)

**Budget:** I can't read the dollar meter from inside the session. My estimate is well under the $100 soft stop (mostly waiting on scrapes). $0 external spend: no paid APIs or data.
**Rules held:** no sends, no invented contacts or emails (nothing pattern-guessed), no ARR or LOI claims, nothing sent as Jeff, public web only.

## Shipped
| Item | Where | State |
|---|---|---|
| EV scoreboard (11 ideas, kill/keep) | `EV_SCOREBOARD.md` | ✅ Winner = Masterplan Care + AI Ops factory; stretch = PinAudit; tariffs / LO / realtor / partner feed / PourDay / recovery killed in writing |
| Lead engine (Maps HTTP engine, TDLR pull, site enricher, scorer, draft generator) | `scripts/` | ✅ Reruns in about 45 minutes for $0; resumable |
| **500 scored rows, 200 KC / 300 DFW (40/60), 100 per vertical** | `data/leads_scored.csv` | ✅ Meets the 400–600 bar. Required schema |
| Top 100 (40 KC / 60 DFW) | `data/combined-top100.csv` | ✅ |
| 100 first-touch drafts (email + call opener, evidence-cited) | `data/first_touch_drafts.csv` | ✅ **DRAFTS, NOT SENT** |
| One-page offer + call script | `offer-or-pitch.md` | ✅ Prices labeled hypothesis |
| Stretch: PinAudit v0: generator, 10 audit PDFs, 10 prospects, $197 stub | `stretch/` | ✅ Stub only, no checkout |

## Data quality (verified counts)
| Set | Rows | Phone | Email (published on own site) | Named contact | Tier A |
|---|---|---|---|---|---|
| Cut: KC | 200 | 199 | 74 | 23 | 6 |
| Cut: DFW | 300 | 300 | 109 | 69 | 31 |
| Top 100: KC | 40 | 40 | 18 | 5 | 6 |
| Top 100: DFW | 60 | 60 | 28 | 22 | 24 |

Source funnel: 4,715 raw Maps rows → 3,569 unique in-metro businesses in the 5 verticals → 2,147 in the ICP (franchises / big brands and 1–4-person shops removed) → 500-row cut.

## Honest shortfalls
1. **KC named contacts are thin (23/200).** Texas publishes contractor license holders (TDLR). Kansas and Missouri have no equivalent statewide open feed. Fix: KC-area city license lists (Overland Park, Olathe and KCMO publish contractor lists, often as PDFs), or the owner's name from the first call.
2. **FSM detection is public-only.** 492/500 show "no FSM detected publicly". FieldEdge and ServiceTitan usually leave no website fingerprint, so this column is a *hint*, not proof. The first call confirms it.
3. **`employee_band` is a hypothesis** derived from review counts, not a headcount.
4. **About 20% of sites were bot-walled** (SiteGround / Cloudflare), so their quality is "not assessed". Those rows score neutral.
5. **Named contacts need a spot check.** Website names come from a regex. TDLR license holders may be the qualifying tech rather than the owner.

## Jeff's next 48 hours
- **Today (30 min):** read `offer-or-pitch.md` and send it to Matt with `combined-top100.csv`. Agree who calls (Matt or a Master Plan rep, **not Jeff**) and which domain sends.
- **Today (20 min):** Matt picks the door he can deliver in 14 days (Ops tune-up vs. Care). Set the price to test on calls 1–10.
- **Tomorrow:** call blocks, 20 Tier-A DFW + 10 Tier-A/B KC. Log outcomes in a new `call_outcome` column.
- **Tomorrow:** add CAN-SPAM footer and opt-out to the drafts. Matt personally reviews and sends up to 20 emails from the Master Plan domain.

## Next 10 actions (one page)
1. Hand Matt `offer-or-pitch.md` + `combined-top100.csv`. Owner: Jeff. Time: 30 min.
2. Matt confirms the offer door and price hypothesis. Owner: Matt. Time: 20 min.
3. Call the top 30 (phone for every row). The script is on the offer page. Owner: Matt / rep.
4. Send ≤20 reviewed drafts from the Master Plan domain with a physical address and opt-out. Owner: Matt.
5. Send a PinAudit PDF as the "free punch list" to any warm reply. PDFs are in `stretch/`; generate more with `pinaudit.py`.
6. Spot-check 20 contact names and emails in the top 100 before any sends. Delete anything that looks off.
7. Rerun the engine for Tulsa / OKC / Wichita (edit `build_queries.py`) only if the first 30 calls produce 2+ meetings.
8. Get KC owner names from city contractor-license lists for the KC top 40.
9. After 20 calls, retune the score weights in `build_leads.py` using what actually converted.
10. Decide on PinAudit: a $197 Payment Link under Master Plan, or keep it free as the Care door-opener. Owner: Matt / Jeff.

## Parked / killed (see scoreboard)
Tariff refund pipe: killed for this session. There's no free public importer name + phone source; revisit with partner-supplied lists or a paid data trial. LO seat OS, realtor 3-2-1, partner feed, PourDay wedge, recovery spikes: killed. SEO displacement: parked; the vendor flag routes those shops to an ops-only pitch.
