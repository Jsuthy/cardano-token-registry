"""Pick 10 PinAudit prospects (5 KC / 5 DFW): in-ICP shops with a weak public profile (not top-3 in their
own search, below-median reviews, no GBP booking link) that still have a phone. Writes pinaudit_prospects.csv and audits."""
import csv, json, os, statistics, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinaudit as pa
D = pa.D
leads = {r["source_url"]: r for r in csv.DictReader(open(os.path.join(D, "leads_scored.csv")))}
cands = []
for r in pa.raw:
    url = f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}"
    if url not in leads or r.get("booking_link") or not r.get("phone"): continue
    q, rank = sorted(pa.pos[r["place_id"]], key=lambda x: x[1])[0]
    med = statistics.median([c["reviews"] or 0 for c in pa.byq[q][:10]])
    if rank > 3 and (r["reviews"] or 0) < med:
        cands.append((leads[url], r, q, rank, med))
seen, pick = set(), []
for metro in ("KC", "DFW"):
    n = 0
    for L, r, q, rank, med in sorted(cands, key=lambda x: -int(x[0]["score"])):
        if L["metro"] != metro or r["place_id"] in seen or n >= 5: continue
        if any(p[0]["vertical"] == L["vertical"] and p[0]["metro"] == metro for p in pick): continue  # one per vertical
        seen.add(r["place_id"]); pick.append((L, r, q, rank, med)); n += 1
out = []
for L, r, q, rank, med in pick:
    path, fixes, rank2, q2 = pa.audit(r["name"])
    pdf = path.replace(".html", ".pdf")
    subprocess.run(["node", os.path.join(os.path.dirname(path), "render_pdf.js"), path, pdf], check=True)
    out.append({"company_name": L["company_name"], "metro": L["metro"], "vertical": L["vertical"], "city": L["city"], "phone": L["phone"],
                "email": L["email"], "contact_name": L["contact_name"], "map_rank": rank, "query": q, "reviews": r["reviews"],
                "local_median_reviews": med, "fixes_found": fixes, "audit_pdf": os.path.basename(pdf), "source_url": L["source_url"],
                "offer": "$197 DFY profile fix (stub), credited to Care", "status": "PROSPECT - not contacted"})
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pinaudit_prospects.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), "prospects;", [(o["company_name"], o["map_rank"], o["fixes_found"]) for o in out])
