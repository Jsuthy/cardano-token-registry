"""Public Google Maps search engine (plain HTTP, no login, no API key).
Uses the same /search?tbm=map request the Maps web client makes, captured once into maps_pb_template.txt.
Usage: python3 maps_engine.py queries.tsv out.jsonl [pages=2]
queries.tsv: metro<TAB>vertical<TAB>city<TAB>state<TAB>query"""
import json, sys, time, random, re, urllib.parse, datetime, os
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = open(os.path.join(HERE, "maps_pb_template.txt")).read().strip()
TQ = "plumber+Denton+TX"  # query baked into the template
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def g(o, *idx):
    for i in idx:
        if not isinstance(o, list) or i >= len(o) or o[i] is None: return None
        o = o[i]
    return o

def url_for(query, offset=0):
    q = urllib.parse.quote_plus(query)
    u = TEMPLATE.replace(TQ, q).replace(urllib.parse.quote(TQ.replace("+", " ")), urllib.parse.quote(query))
    if offset:
        u = u.replace("%217i20", f"%217i20%218i{offset}", 1)
    return u

def parse_place(r):
    booking = g(r, 75, 0, 0, 2, 0, 1, 2, 0)
    return {
        "name": g(r, 11) or "",
        "address_full": g(r, 39) or "",
        "street": g(r, 2, 0) or "",
        "city_state_zip": g(r, 2, 1) or "",
        "rating": g(r, 4, 7),
        "reviews": g(r, 4, 8) or g(r, 37, 1) or 0,
        "website": (g(r, 7, 0) or ""),
        "phone": (g(r, 178, 0, 1, 0, 0) or ""),
        "categories": g(r, 13) or [],
        "lat": g(r, 9, 2), "lng": g(r, 9, 3),
        "place_id": g(r, 78) or "",
        "cid_hex": g(r, 10) or "",
        "booking_link": booking or "",
        "hours_status": (g(r, 203, 1, 4, 0) or "") if isinstance(g(r, 203, 1, 4, 0), str) else "",
    }

def search(query, offset=0, tries=3):
    for a in range(tries):
        try:
            resp = requests.get(url_for(query, offset), headers=UA, timeout=40)
            t = resp.text
            if t.startswith(")]}'"): t = t[t.index("\n") + 1:]
            d = json.loads(t)
            res = g(d, 64) or []
            out = []
            for item in res:
                r = g(item, 1)
                if isinstance(r, list) and g(r, 11): out.append(parse_place(r))
            return out
        except Exception as e:
            time.sleep(3 + 3 * a)
    return []

if __name__ == "__main__":
    qfile, outfile = sys.argv[1], sys.argv[2]
    pages = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    done = set(open(outfile + ".done").read().split("\n")) if os.path.exists(outfile + ".done") else set()
    qs = [l.rstrip("\n").split("\t") for l in open(qfile) if l.strip() and not l.startswith("#")]
    total = 0
    for i, (metro, vertical, city, state, query) in enumerate(qs):
        if query in done: continue
        n = 0
        with open(outfile, "a") as f:
            for p in range(pages):
                rows = search(query, offset=20 * p)
                for r in rows:
                    r.update(metro=metro, vertical=vertical, query_city=city, query_state=state, query=query,
                             maps_url=f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}" if r["place_id"] else "",
                             scraped_at=datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z")
                    f.write(json.dumps(r) + "\n")
                n += len(rows)
                if len(rows) < 20: break
                time.sleep(random.uniform(1.0, 2.5))
        open(outfile + ".done", "a").write(query + "\n")
        total += n
        print(f"[{i+1}/{len(qs)}] {query}: {n} (total {total})", flush=True)
        time.sleep(random.uniform(1.0, 2.5))
