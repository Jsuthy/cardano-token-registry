"""Merge Maps rows + website enrichment + TDLR license holders -> scored Care / AI-Ops lead list.
Outputs (../data): leads_all_scored.csv, leads_scored.csv (the 40/60 KC/DFW cut), combined-top100.csv"""
import csv, json, math, re, sys, collections, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
TARGET_TOTAL, KC_SHARE = int(os.environ.get("TARGET_TOTAL", 500)), 0.40

SCHEMA = ["company_name","metro","vertical","city","state","website","phone","email","contact_name","contact_title",
          "employee_band","ops_stack_hint","site_quality_notes","score","tier","source_url","scraped_at","notes"]

VERT_CATS = [  # order matters: first match wins
    ("HVAC", r"hvac|air conditioning|heating contractor|furnace|heat pump"),
    ("Plumbing", r"plumb|drainage|water heater|septic"),
    ("Electrical", r"electrician|electrical"),
    ("Roofing", r"roof"),
    ("GC", r"general contractor|construction company|remodel|home builder|custom home|contractor$|building firm"),
]
CENTERS = {"KC": (39.0997, -94.5786, 40), "DFW": (32.85, -97.02, 45)}  # lat, lng, radius miles
FRANCHISE = r"one hour|benjamin franklin|mr\.? rooter|mister sparky|roto-rooter|service experts|aire serv|mr\.? electric|ars |rescue rooter|mr\.? handyman|home depot|lowe'?s|sears|len the plumber|horizon services|goettl|mighty dog|five star painting|dwyer|ace hardware|precision garage|window nation|leafguard|leaf filter|leaffilter|bath fitter|re-bath|power home|erie home|long roofing|pacific|sunrun|tesla|5 star"
BIG_BRANDS_NO = r"\b(lowe'?s|home depot|menards|ferguson|johnstone|winsupply|carrier enterprise)\b"

def miles(a, b, c, d):
    r = 3958.8; p1, p2 = math.radians(a), math.radians(c)
    dl = math.radians(d - b); dp = p2 - p1
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(h))

def norm(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"\b(llc|l\.l\.c|inc|co|corp|corporation|company|ltd|lp|pllc|dba|the)\b\.?", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

BIZ = r"\b(llc|inc|ltd|l\.?p|co|corp|company|electric\w*|plumb\w*|roof\w*|air|heating|cooling|mechanical|services?|construction|systems?|solutions|group|enterprises?|contractors?|hvac|gaf|design|lighting|builders?|homes?)\b"
def title_name(n):  # TDLR "SMITH JR, JOHN A" -> "John A Smith Jr"; returns "" for business entities
    if "," not in n or re.search(BIZ, n, re.I): return ""
    last, first = [x.strip() for x in n.split(",", 1)]
    suf = ""
    m = re.match(r"(.+?)\s+(JR|SR|II|III|IV)\.?$", last, re.I)
    if m: last, suf = m.group(1), m.group(2)
    m2 = re.match(r"(.+?)\s+(JR|SR|II|III|IV)\.?$", first, re.I)
    if m2: first, suf = m2.group(1), m2.group(2)
    full = " ".join(x for x in (first, last, suf) if x)
    return " ".join(w.capitalize() if len(w) > 1 and w.upper() not in ("II", "III", "IV") else w for w in full.split())

NAME_STOP = set("""manager marine veteran executive officer any questions army navy force military retired licensed certified master
journeyman owner operator lead senior chief general project office service sales field customer our meet team welcome dear hello
thank thanks call today free quote estimate founder president ceo proud family local texas dallas kansas city fort worth missouri
experience inspection trident benjamin moore sherwin williams carrier trane lennox rheem about contact read more learn click here home page best top quality trusted residential commercial emergency repair install""".split())
FREEMAIL = r"@(gmail|yahoo|outlook|hotmail|aol|att|sbcglobal|icloud|me|msn|live|comcast|kc\.rr|swbell|verizon|charter|cox|earthlink)\."
def good_name(n):
    ws = n.replace(".", "").split()
    return 2 <= len(ws) <= 4 and all(w[0].isupper() for w in ws) and not any(w.lower() in NAME_STOP for w in ws) and not re.search(BIZ, n, re.I)
def good_email(e, site, company):
    dom = e.split("@")[-1].lower()
    sdom = re.sub(r"^https?://(www\.)?", "", site.lower()).split("/")[0]
    if sdom and (dom == sdom or dom.endswith("." + sdom) or sdom.endswith(dom)): return True
    if re.search(FREEMAIL, e, re.I): return True
    toks = [t for t in norm(company).split() if len(t) > 3]
    return any(t in dom for t in toks)

def band(rev):
    if rev < 15: return "1-4 (hyp.)"
    if rev < 60: return "3-10 (hyp.)"
    if rev < 400: return "5-25 (hyp.)"
    if rev < 1500: return "15-60 (hyp.)"
    return "50+ (hyp.)"

def main():
    raw = [json.loads(l) for l in open(os.path.join(D, "maps_raw.jsonl")) if l.strip()]
    enr = {}
    ep = os.path.join(D, "site_enrichment.jsonl")
    if os.path.exists(ep):
        for l in open(ep):
            e = json.loads(l); enr[e["website"]] = e
    tdlr = json.load(open(os.path.join(D, "tdlr_dfw_contractors.json"))) if os.path.exists(os.path.join(D, "tdlr_dfw_contractors.json")) else []
    tdlr_idx = collections.defaultdict(list)
    for t in tdlr:
        if t.get("business_name"): tdlr_idx[norm(t["business_name"])].append(t)

    seen, rows = {}, []
    for r in raw:
        key = r.get("place_id") or (r["name"], r.get("phone"))
        if key in seen:
            continue
        seen[key] = 1
        cats = " | ".join(r.get("categories") or [])
        vert = next((v for v, p in VERT_CATS if re.search(p, cats, re.I)), None)
        if not vert or re.search(BIG_BRANDS_NO, r["name"], re.I):
            continue
        m = re.match(r"(.+?),\s*([A-Z]{2})\s*(\d{5})?", r.get("city_state_zip") or "")
        city, state = (m.group(1), m.group(2)) if m else (r["query_city"], r["query_state"])
        lat, lng, rad = CENTERS[r["metro"]]
        if r.get("lat") is None or miles(lat, lng, r["lat"], r["lng"]) > rad:
            continue
        if r["metro"] == "DFW" and state != "TX": continue
        if r["metro"] == "KC" and state not in ("MO", "KS"): continue
        site = (r.get("website") or "").split("?")[0]
        e = enr.get(site, {})
        notes = []
        # contact name: TDLR license holder (DFW HVAC/Electrical) or explicitly labelled on company site
        contact_name = contact_title = ""
        if r["metro"] == "DFW" and vert in ("HVAC", "Electrical"):
            hits = tdlr_idx.get(norm(r["name"]), [])
            want = "A/C Contractor" if vert == "HVAC" else "Electrical Contractor"
            hits = [h for h in hits if h["license_type"] == want] or hits
            if hits and hits[0].get("owner_name") and title_name(hits[0]["owner_name"]):
                contact_name = title_name(hits[0]["owner_name"])
                contact_title = f"License holder, TDLR {hits[0]['license_type']} #{hits[0]['license_number']}"
                notes.append("contact=TDLR public license record")
        if not contact_name:
            om = [(n, t) for n, t in (e.get("owner_mentions") or []) if good_name(n)]
            if om:
                contact_name, contact_title = om[0][0], om[0][1] + " (per company website)"
                notes.append("contact=named on company website")
        emails = [m.group(0).lower() for m in (re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}", x, re.I) for x in (e.get("emails") or [])) if m]
        emails = [x for x in dict.fromkeys(emails) if good_email(x, site, r["name"])]
        emails.sort(key=lambda x: bool(re.match(r"(careers?|jobs?|hr|hiring|webmaster|no-?reply|privacy|accounting|billing|ap|invoices?)@", x)))
        email = emails[0] if emails else ""
        if email: notes.append("email=published on company website")
        fsm = e.get("fsm") or []
        bl = r.get("booking_link") or ""
        bl_fsm = [k for k, p in [("ServiceTitan", "servicetitan"), ("Housecall Pro", "housecallpro"), ("Jobber", "jobber"), ("FieldEdge", "fieldedge"), ("Schedule Engine", "scheduleengine")] if p in bl.lower()]
        fsm = sorted(set(fsm + bl_fsm))
        stack = []
        if fsm: stack.append("FSM: " + "/".join(fsm))
        else: stack.append("no FSM detected publicly")
        if bl: stack.append("GBP booking link")
        if e.get("mkt"): stack.append("mkt: " + "/".join(e["mkt"]))
        if e.get("cms"): stack.append("CMS: " + "/".join(e["cms"]))
        vendor = e.get("vendor") or []
        q = list(e.get("quality_notes") or [])
        if not site: q = ["NO WEBSITE on Google profile"]
        elif e.get("fetch_status") == "bot-wall": q = ["site behind bot-wall (not assessed)"]
        elif e and not e.get("fetch_ok"): q = [f"site unreachable ({e.get('fetch_status')})"]
        elif not e: q = ["site not yet assessed"]
        if vendor:
            q.append("SEO/web vendor footprint: " + "/".join(vendor) + " -> ops-first pitch, NO site edits while vendor active")
        rev, rating = int(r.get("reviews") or 0), r.get("rating")
        franchise = bool(re.search(FRANCHISE, r["name"], re.I))
        # ---- score (0-100) ----
        size = 30 if 100 <= rev <= 1200 else 22 if 40 <= rev < 100 else 18 if 1200 < rev <= 2500 else 12 if 15 <= rev < 40 else 5
        if not site: care = 14
        elif e.get("fetch_ok"): care = round((10 - e.get("site_score", 5)) * 2.5)
        else: care = 10
        if not fsm: ops = 20
        elif "FieldEdge" in fsm: ops = 18
        elif "ServiceTitan" in fsm: ops = 6
        else: ops = 12
        contact = (5 if r.get("phone") else 0) + (5 if email else 0) + (5 if contact_name else 0)
        rep = 10 if (rating or 0) >= 4.5 else 7 if (rating or 0) >= 4.0 else 4
        score = size + care + ops + contact + rep
        if franchise: score -= 15; notes.append("franchise/brand: corporate site, franchisee-level ops pitch only")
        if vendor: score -= 5
        score = max(0, min(100, score))
        tier = "A" if score >= 80 else "B" if score >= 68 else "C"
        notes.append(f"rating {rating} / {rev} reviews; GBP categories: {cats}")
        rows.append({
            "company_name": r["name"], "metro": r["metro"], "vertical": vert, "city": city, "state": state,
            "website": site, "phone": r.get("phone", ""), "email": email, "contact_name": contact_name, "contact_title": contact_title,
            "employee_band": band(rev), "ops_stack_hint": "; ".join(stack), "site_quality_notes": "; ".join(q),
            "score": score, "tier": tier, "source_url": r.get("maps_url", ""), "scraped_at": r.get("scraped_at", ""),
            "notes": "; ".join(notes),
        })
    rows.sort(key=lambda x: -x["score"])
    def w(name, rs):
        with open(os.path.join(D, name), "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=SCHEMA); wr.writeheader(); wr.writerows(rs)
    w("leads_all_scored.csv", rows)
    # ICP cut: drop obvious non-ICP (tiny w/o site AND no reviews; 50+ big brands) before the 40/60 cut
    icp = [x for x in rows if not x["employee_band"].startswith("1-4") and "franchise" not in x["notes"]]
    kc = [x for x in icp if x["metro"] == "KC"]; dfw = [x for x in icp if x["metro"] == "DFW"]
    def balanced(rs, n):  # round-robin across verticals so no single trade dominates a metro
        by = collections.defaultdict(list)
        for x in rs: by[x["vertical"]].append(x)
        out, i = [], 0
        while len(out) < n and any(by.values()):
            for v in sorted(by):
                if by[v] and len(out) < n: out.append(by[v].pop(0))
        return out
    n_kc = min(len(kc), round(TARGET_TOTAL * KC_SHARE)); n_dfw = min(len(dfw), TARGET_TOTAL - n_kc)
    kc_cut, dfw_cut = balanced(kc, n_kc), balanced(dfw, n_dfw)
    cut = sorted(kc_cut + dfw_cut, key=lambda x: -x["score"])
    w("leads_scored.csv", cut)
    top = sorted(balanced(kc, 40) + balanced(dfw, 60), key=lambda x: -x["score"])
    w("combined-top100.csv", top)
    c = collections.Counter((x["metro"], x["vertical"]) for x in cut)
    print(f"raw={len(raw)} unique_in_scope={len(rows)} icp={len(icp)} cut={len(cut)} (KC {n_kc} / DFW {n_dfw}) top100={len(top)}")
    print("tiers:", collections.Counter(x["tier"] for x in cut))
    print("by metro/vertical:", dict(sorted(c.items())))
    print("with email:", sum(1 for x in cut if x["email"]), "with contact_name:", sum(1 for x in cut if x["contact_name"]), "with phone:", sum(1 for x in cut if x["phone"]))

if __name__ == "__main__":
    main()
