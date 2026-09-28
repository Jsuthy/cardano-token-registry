"""Pull active TDLR A/C + Electrical contractor licenses for DFW counties (public data.texas.gov feed).
Used to attach a public license-holder name (owner_name) to DFW HVAC / Electrical rows."""
import json, sys, requests
COUNTIES = ["DALLAS", "TARRANT", "COLLIN", "DENTON", "ROCKWALL", "ELLIS", "JOHNSON", "KAUFMAN", "PARKER"]
URL = "https://data.texas.gov/resource/7358-krk7.json"
rows = []
for lt in ("A/C Contractor", "Electrical Contractor"):
    for c in COUNTIES:
        off = 0
        while True:
            r = requests.get(URL, params={"license_type": lt, "business_county": c, "$limit": 5000, "$offset": off,
                                          "$select": "license_type,license_number,business_name,owner_name,business_county,license_expiration_date_mmddccyy,business_city_state_zip"}, timeout=60)
            r.raise_for_status(); batch = r.json(); rows += batch; off += len(batch)
            if len(batch) < 5000: break
out = sys.argv[1] if len(sys.argv) > 1 else "../data/tdlr_dfw_contractors.json"
json.dump(rows, open(out, "w"))
print(len(rows), "TDLR rows ->", out)
