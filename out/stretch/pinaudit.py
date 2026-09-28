"""PinAudit v0: one-page Google Business Profile audit from PUBLIC Maps data only.
Usage: python3 pinaudit.py "<company name substring>" [out_dir]
Reads ../data/maps_raw.jsonl (+ site_enrichment.jsonl). Writes <slug>.html; render_pdf.js turns it into a PDF."""
import json, os, re, sys, statistics, html, datetime
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
raw = [json.loads(l) for l in open(os.path.join(D, "maps_raw.jsonl"))]
enr = {}
if os.path.exists(os.path.join(D, "site_enrichment.jsonl")):
    for l in open(os.path.join(D, "site_enrichment.jsonl")):
        e = json.loads(l); enr[e["website"]] = e
# position of each listing inside each query's result order
pos, byq = {}, {}
for r in raw:
    byq.setdefault(r["query"], []).append(r)
for q, rs in byq.items():
    for i, r in enumerate(rs):
        pos.setdefault(r["place_id"], []).append((q, i + 1))

def audit(target):
    t = next(r for r in raw if target.lower() in r["name"].lower())
    q, rank = sorted(pos[t["place_id"]], key=lambda x: x[1])[0]
    comps = [r for r in byq[q] if r["place_id"] != t["place_id"]][:10]
    med_rev = statistics.median([c["reviews"] or 0 for c in comps]) if comps else 0
    med_rat = statistics.median([c["rating"] or 0 for c in comps if c["rating"]]) if comps else 0
    site = (t.get("website") or "").split("?")[0]; e = enr.get(site, {}); site = site.split("#")[0]
    checks = []  # (label, status, detail, fix)
    def add(l, ok, d, fix): checks.append((l, "PASS" if ok is True else "FIX" if ok is False else "CHECK", d, fix))
    add("Map-pack position", rank <= 3, f"#{rank} for \"{q}\"", "Top-3 is where the calls are. Work reviews, categories and landing-page relevance.")
    add("Review volume vs local top 10", (t["reviews"] or 0) >= med_rev, f"{t['reviews']} vs median {med_rev:.0f}", "Automate review requests after every closed job (text, 2h after invoice).")
    add("Star rating vs local top 10", (t["rating"] or 0) >= med_rat, f"{t['rating']} vs median {med_rat}", "Respond to every review under 4 stars within 48h; fix the recurring complaint.")
    add("Website linked on profile", bool(site), site or "none", "Link a real landing page (not a Facebook page).")
    add("Online booking link on profile", bool(t.get("booking_link")), t.get("booking_link") or "none", "Add a booking / 'request service' link. It shows as a button on Maps.")
    add("Categories", len(t.get("categories") or []) >= 3, ", ".join(t.get("categories") or []), "Primary category plus 3–6 true secondary categories for services you actually sell.")
    add("Phone on profile", bool(t.get("phone")), t.get("phone") or "none", "A local number that rings live or text-backs.")
    if e.get("fetch_ok"):
        q_notes = e.get("quality_notes", [])
        add("Landing page: click-to-call", "no click-to-call" not in q_notes, "tel: link " + ("missing" if "no click-to-call" in q_notes else "present"), "Wrap every phone number in a tel: link.")
        add("Landing page: booking / quote CTA", "no online booking/quote CTA" not in q_notes, "CTA " + ("missing" if "no online booking/quote CTA" in q_notes else "present"), "Put a 'Book service' button above the fold.")
        add("Landing page: LocalBusiness schema", "no schema markup" not in q_notes, "JSON-LD " + ("missing" if "no schema markup" in q_notes else "present"), "Add LocalBusiness/HVACBusiness schema with the same name, address and phone as the profile.")
        add("Landing page: mobile-ready", "no mobile viewport" not in q_notes, "viewport " + ("missing" if "no mobile viewport" in q_notes else "present"), "Mobile-first template.")
    elif site:
        add("Landing page", None, "couldn't be fetched automatically (bot-wall or error)", "Manual check.")
    fixes = sum(1 for c in checks if c[1] == "FIX")
    grade = round(100 * sum(1 for c in checks if c[1] == "PASS") / len(checks))
    rows = "".join(f"<tr class='{s.lower()}'><td>{html.escape(l)}</td><td><b>{s}</b></td><td>{html.escape(str(d))}</td><td>{html.escape(f) if s!='PASS' else ''}</td></tr>" for l, s, d, f in checks)
    comp_rows = "".join(f"<tr><td>{i+1}</td><td>{html.escape(c['name'])}</td><td>{c['rating']}</td><td>{c['reviews']}</td></tr>" for i, c in enumerate(byq[q][:6]))
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>GBP Audit: {html.escape(t['name'])}</title>
<style>body{{font-family:Helvetica,Arial,sans-serif;margin:28px;color:#1b1b1b;font-size:12px}}h1{{font-size:20px;margin:0}}.sub{{color:#555}}
.grade{{float:right;font-size:34px;font-weight:700;border:3px solid #1b1b1b;border-radius:8px;padding:4px 14px}}
table{{border-collapse:collapse;width:100%;margin-top:10px}}td,th{{border-bottom:1px solid #ddd;padding:5px;text-align:left;vertical-align:top}}
tr.fix td:nth-child(2){{color:#b3261e}}tr.pass td:nth-child(2){{color:#1e7b34}}tr.check td:nth-child(2){{color:#8a6d00}}
.foot{{margin-top:14px;color:#666;font-size:10px}}.cta{{margin-top:12px;padding:10px;background:#f3f3f3;border-radius:6px}}</style></head><body>
<div class="grade">{grade}<span style="font-size:14px">/100</span></div><h1>Google Business Profile Audit</h1>
<div class="sub">{html.escape(t['name'])} · {html.escape(t.get('address_full',''))} · generated {datetime.date.today()}</div>
<h3>Scorecard ({fixes} fixes found)</h3><table><tr><th>Check</th><th>Status</th><th>What we saw</th><th>Fix</th></tr>{rows}</table>
<h3>Who's beating you for "{html.escape(q)}"</h3><table><tr><th>#</th><th>Business</th><th>Rating</th><th>Reviews</th></tr>{comp_rows}</table>
<div class="cta"><b>Done-for-you fix: $197 [PRICE STUB, HYPOTHESIS].</b> We fix the profile items above within 7 days. The $197 is credited toward Master Plan Website Care if you continue.</div>
<div class="foot">Source: public Google Maps search results and the public homepage only, collected {t['scraped_at'][:10]}. Rankings vary by searcher location and time. This is a snapshot, not a guarantee.</div>
</body></html>"""
    slug = re.sub(r"[^a-z0-9]+", "-", t["name"].lower()).strip("-")[:50]
    od = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(od, f"audit-{slug}.html"); open(p, "w").write(doc)
    return p, fixes, rank, q

if __name__ == "__main__":
    print(audit(sys.argv[1]))
