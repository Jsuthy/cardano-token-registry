# Master Plan Trades Ops + Care: one-page offer (DRAFT)

> For Matt (Master Plan Advisory Group) and Jeff. Use it in calls and as a leave-behind.
> **Prices are hypotheses to test on the first 10 calls, not quotes.** No results or case studies are claimed; there are none yet.

## Who it's for
Owner-run **HVAC, plumbing, electrical, roofing and GC shops in Kansas City and DFW**, roughly 5–50 people.
The owner is still the fallback dispatcher. Missed calls after 5pm are lost jobs. The website was "done" years ago.

## The problem, in the owner's words
- "We miss calls when the techs are out and the office is slammed."
- "FieldEdge / our software does way more than we use."
- "The website's fine, I think? Nobody's touched it in a while."
- "My books guy and my marketing guy don't talk."

## What Master Plan does (three doors; start with whichever one is open)

| Door | What we do | Price hypothesis | Proof we can show the prospect up front |
|------|-----------|------------------|------------------------------------------|
| **1. Ops tune-up (AI Ops)** | Missed-call text-back, after-hours booking capture, review-request follow-up; tune FieldEdge (or another FSM) for booking, memberships and follow-ups; a weekly "leaks" report | Setup **$1,500–5,000**; then **$500–1,500/mo** | Their public signals (from the lead file): no online booking, no FSM detected, and so on |
| **2. Website Care (SITE-EDIT)** | Monthly Decision Pack Care: fixes, speed, click-to-call, booking CTA, schema, content refresh. **Only on sites no other agency is actively managing.** | **$300–750/mo** | A punch list from the site-quality notes |
| **3. Books + advisory (existing)** | Master Plan's core bookkeeping, tax and advisory | Existing pricing | Matt's existing clients |

**Bundle hypothesis:** books + Care + Ops for **$1,500–2,500/mo**. The pitch is one throat to choke for the back office.

## Guardrails (non-negotiable)
- If the lead file flags an **SEO/web vendor footprint** (Scorpion, Blue Corona, Contractor Commerce, Hibu, Thryv, and so on), pitch **Door 1 only**. No site edits while the vendor is active, and no "fire your SEO guy."
- No claims of results we don't have. Offer the free one-page punch list as the proof.
- Every email needs a physical address and an opt-out line (CAN-SPAM). The drafts in `data/first_touch_drafts.csv` carry placeholders for both.

## The 15-minute call
1. "Walk me through what happens when a call comes in at 6:30pm." (This finds the missed-call leak.)
2. "What does [FieldEdge / your software] do for you today? What did you buy it for?" (Ops gap.)
3. "When did someone last change the website? Who has the login?" (Care, or the vendor guardrail.)
4. Offer: "I'll send a one-page punch list for [company] this week. If two items are worth fixing, we talk price."

## The free punch list (the wedge)
It's built from `data/leads_scored.csv`: the `site_quality_notes` and `ops_stack_hint` columns, plus the GBP rating and review count.
The stretch PinAudit generator (`stretch/`) renders the same data as a one-page Google Business Profile audit. It can be free, or $197 credited toward Care.

## Why these accounts first
`combined-top100.csv` ranks shops by: size fit (review volume as a proxy for 5–50 staff), how much Care opportunity the site shows, how much ops opportunity there is (no FSM or booking detected), how reachable the contact is (phone, email, named owner), and reputation health. Franchise and big-brand units are removed.
