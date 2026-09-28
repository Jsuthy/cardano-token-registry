"""Generate first-touch DRAFTS (email + call opener) for combined-top100.csv from observed public signals.
Nothing is sent. Every hook cites the evidence it came from. Output: ../data/first_touch_drafts.csv"""
import csv, os, re
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
rows = list(csv.DictReader(open(os.path.join(D, "combined-top100.csv"))))
out = []
for r in rows:
    q, stack = r["site_quality_notes"], r["ops_stack_hint"]
    first = r["contact_name"].split()[0] if r["contact_name"] else ""
    greet = f"Hi {first}," if first else f"Hi {r['company_name']} team,"
    vendor = "vendor footprint" in q
    hooks, ev = [], []
    if "NO WEBSITE" in q:
        hooks.append("your Google profile doesn't link to a website, so every search click has nowhere to land except a phone call"); ev.append("GBP has no website field")
    else:
        if "no online booking" in q: hooks.append("I couldn't find a way to book or request a quote online on your site. After-hours visitors usually just leave"); ev.append("no booking/quote CTA on home/contact pages")
        if "no click-to-call" in q: hooks.append("on a phone, your number isn't tap-to-call"); ev.append("no tel: link on homepage")
        if "stale footer" in q: yr = re.search(r"©(\d{4})", q); hooks.append(f"the footer still says ©{yr.group(1) if yr else 'an old year'}, which customers read as 'is this company still around?'"); ev.append("copyright year")
        if "no mobile viewport" in q: hooks.append("the site doesn't scale on phones"); ev.append("no viewport meta")
    if "no FSM detected" in stack:
        hooks.append("I didn't see online scheduling tied to a dispatch system (ServiceTitan, FieldEdge, Housecall Pro), so I'm guessing calls, texts and the board are still stitched together by hand"); ev.append("no FSM widget/booking link found publicly")
    elif "FieldEdge" in stack:
        hooks.append("you're on FieldEdge, and most shops we see only use about half of it (booking, memberships, follow-ups)"); ev.append("FieldEdge fingerprint on site")
    hooks = hooks[:2]
    if vendor:
        offer = "We don't touch websites that another agency manages. What we do is the ops side: missed-call text-back, booking, and review follow-up, working alongside your current marketing."
    else:
        offer = "Master Plan runs books and advisory for trades, and now handles website Care and AI ops (missed-call text-back, booking, review follow-up) for the same shops."
    body = (f"{greet}\n\nI was looking at {r['company_name']} in {r['city']}."
            + (" Two things stood out: " + "; and ".join(hooks) + "." if hooks else "")
            + f"\n\n{offer}\n\nWorth a 15-minute look? I can send a one-page punch list for {r['company_name']} first. No charge, no obligation."
            + "\n\n[Master Plan rep sign-off: send from Master Plan domain, not as Jeff]\n[Physical address + opt-out line required before any send (CAN-SPAM)]")
    call = (f"\"Hi, is this {first or 'the owner'}? It's [name] with Master Plan in {'Kansas City' if r['metro']=='KC' else 'Dallas'}. We work with {r['vertical'].lower()} shops on the back office and the ops side. "
            + (f"Quick one: {hooks[0]}. " if hooks else "") + "Who handles your scheduling and missed calls?\"")
    out.append({"company_name": r["company_name"], "metro": r["metro"], "vertical": r["vertical"], "tier": r["tier"], "score": r["score"],
                "to_email": r["email"], "phone": r["phone"], "contact_name": r["contact_name"],
                "subject": f"{r['company_name']}: quick ops note", "email_draft": body, "call_opener": call,
                "hook_evidence": "; ".join(ev), "status": "DRAFT - not sent"})
with open(os.path.join(D, "first_touch_drafts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), "drafts -> first_touch_drafts.csv")
