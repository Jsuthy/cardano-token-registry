"""Fetch each company's public website (home + a contact/about page) and extract:
emails (on-page only), stack fingerprints (FSM / booking / CMS / SEO vendor), site-quality signals,
and explicitly-labelled owner names ("Owner: Jane Doe" style). Nothing is guessed or pattern-built."""
import json, re, sys, time, concurrent.futures as cf
from urllib.parse import urljoin, urlparse
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
FSM = {  # field-service / ops stack fingerprints (as seen in public HTML: widgets, booking links, scripts)
    "ServiceTitan": r"servicetitan|st-scheduler|scheduler\.servicetitan",
    "FieldEdge": r"fieldedge",
    "Housecall Pro": r"housecallpro|housecall\s?pro|hcp-widget",
    "Jobber": r"getjobber|jobber\.com|clienthub",
    "Service Fusion": r"servicefusion",
    "Successware": r"successware",
    "ServiceTrade": r"servicetrade",
    "Workiz": r"workiz",
    "JobNimbus": r"jobnimbus",
    "AccuLynx": r"acculynx",
    "Roofr": r"roofr\.com",
    "Buildertrend": r"buildertrend",
    "CoConstruct": r"coconstruct",
    "Schedule Engine": r"scheduleengine|schedule engine",
}
MKT = {
    "Podium": r"podium\.com|podium-widget", "Birdeye": r"birdeye", "NiceJob": r"nicejob", "Broadly": r"broadly\.com",
    "Hatch": r"usehatchapp|hatchapp", "CallRail": r"callrail", "HubSpot": r"hs-scripts|hubspot", "Angi/HomeAdvisor": r"homeadvisor|angi\.com",
    "Chat widget": r"livechat|tawk\.to|intercom|drift\.com|smith\.ai|ngagelive",
}
CMS = {"WordPress": r"wp-content|wp-includes", "Wix": r"wixstatic|wix\.com", "Squarespace": r"squarespace", "GoDaddy Builder": r"godaddy|img1\.wsimg",
       "Duda": r"dudaone|multiscreensite|duda", "Webflow": r"webflow", "Weebly": r"weebly", "Shopify": r"shopify"}
VENDOR = {  # SEO / web vendors known for trades; presence => likely active vendor => no dual-editing
    "Scorpion": r"scorpion\.co|scorpion", "Blue Corona": r"bluecorona", "Hook Agency": r"hookagency", "Contractor Commerce": r"contractorcommerce",
    "Market Hardware": r"markethardware", "SEO Werkz/Local": r"seowerkz", "CompletSEO": r"complet\s?seo|completseo", "Rival Digital": r"rivaldigital",
    "Search Engine Pros": r"searchenginepros", "Plumbing Webmasters": r"plumbingwebmasters", "Roofing Webmasters": r"roofingwebmasters",
    "Hibu": r"hibu", "Thryv": r"thryv", "Yodle/Web.com": r"yodle|web\.com", "LocaliQ": r"localiq", "Footbridge": r"footbridge",
    "Leap/Company Cam": r"leaptodigital", "Service Titan Marketing": r"titan.?marketing",
}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BAD_EMAIL = re.compile(r"(example\.|sentry|wixpress|domain\.com|email\.com|yourdomain|\.png|\.jpg|\.webp|\.gif|\.svg|godaddy|wordpress|schema\.org|@2x|mysite|test@|user@|name@)", re.I)
OWNER_RE = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-zA-Z'\-]+)\s*(?:,|-|–|—|\||is the|is our)?\s*(?:the\s)?(Owner|Co-Owner|Founder|Co-Founder|President|CEO|General Manager)\b")
OWNER_RE2 = re.compile(r"\b(Owner|Founder|President|CEO)\s*[:\-–—,]\s*([A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-zA-Z'\-]+)\b")
STOP = set("co vice master plumber about our we are meet team the spot install button his her and owner family local your new general senior license licensed us my i a an of by to with for from in on at is was call contact read learn view see this that company services service home air heating cooling plumbing electric electrical roofing construction hvac inc llc business proud proudly founding founded current previous".split())
def ok_name(n):
    ws = n.replace(".", "").split()
    return len(ws) >= 2 and not any(w.lower() in STOP or w.endswith("-") for w in ws) and n not in NOT_NAMES
NOT_NAMES = {"Kansas City", "Fort Worth", "Overland Park", "Air Conditioning", "Service Experts", "Home Services", "Our Team", "About Us", "Contact Us", "Read More", "Learn More", "General Contractor", "Family Owned", "Locally Owned", "Veteran Owned", "Woman Owned", "Proudly Owned", "Business Owner", "Home Owner"}

def get(url):
    try:
        r = requests.get(url, headers=UA, timeout=15, allow_redirects=True)
        if r.status_code >= 400 or "text/html" not in r.headers.get("content-type", "text/html"):
            return None, r.status_code, url
        return r.text[:1_500_000], r.status_code, r.url
    except Exception as e:
        return None, type(e).__name__, url

def text_of(html):
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)

def find(patterns, blob):
    return [k for k, p in patterns.items() if re.search(p, blob, re.I)]

def enrich(site):
    site = site.split("?")[0]
    res = {"website": site, "fetch_ok": False}
    if not site: return res
    html, status, final = get(site)
    if not html:
        res["fetch_status"] = status; return res
    if len(html) < 3000 or re.search(r"sgcaptcha|cf-challenge|Just a moment\.\.\.|Attention Required|captcha", html[:5000], re.I):
        res["fetch_status"] = "bot-wall"; res["final_url"] = final; return res
    res["fetch_ok"] = True; res["final_url"] = final
    dom = urlparse(final).netloc.lower().removeprefix("www.")
    pages = [html]
    links = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    extra = []
    for l in links:
        if re.search(r"contact|about|team|our-story|who-we-are", l, re.I):
            u = urljoin(final, l)
            if urlparse(u).netloc.lower().removeprefix("www.") == dom and u not in extra:
                extra.append(u)
    for u in extra[:2]:
        h, _, _ = get(u)
        if h: pages.append(h)
    blob = "\n".join(pages)
    txt = text_of(blob)
    emails = set()
    for m in re.findall(r"mailto:([^\"'?>\s]+)", blob, re.I):
        emails.add(m.strip().lower())
    for m in EMAIL_RE.findall(txt):
        emails.add(m.lower())
    emails = [e for e in emails if "@" in e and "." in e.split("@")[-1] and not BAD_EMAIL.search(e) and len(e) < 60]
    on_dom = [e for e in emails if e.split("@")[1].removeprefix("www.") == dom]
    res["emails"] = sorted(on_dom) + sorted(set(emails) - set(on_dom))
    owners = []
    for m in OWNER_RE.finditer(txt):
        n = m.group(1)
        if ok_name(n) and not re.search(r"Heating|Cooling|Plumbing|Electric|Roofing|Construction|Services|Company|Air|Home", n):
            owners.append((n, m.group(2)))
    for m in OWNER_RE2.finditer(txt):
        n = m.group(2)
        if ok_name(n) and not re.search(r"Heating|Cooling|Plumbing|Electric|Roofing|Construction|Services|Company|Air|Home", n):
            owners.append((n, m.group(1)))
    res["owner_mentions"] = owners[:3]
    res["fsm"] = find(FSM, blob)
    res["mkt"] = find(MKT, blob)
    res["cms"] = find(CMS, html)
    res["vendor"] = find(VENDOR, html)
    # quality signals from homepage
    notes = []
    if not final.startswith("https"): notes.append("no HTTPS")
    if not re.search(r'name=["\']viewport', html, re.I): notes.append("no mobile viewport")
    if not re.search(r'href=["\']tel:', html, re.I): notes.append("no click-to-call")
    if "application/ld+json" not in html: notes.append("no schema markup")
    title = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if not title or len(title.group(1).strip()) < 15: notes.append("weak/missing title")
    if not re.search(r'name=["\']description', html, re.I): notes.append("no meta description")
    yrs = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20\d\d)", html, re.I)]
    if yrs and max(yrs) < 2025: notes.append(f"stale footer ©{max(yrs)}")
    if not re.search(r"book|schedule|request (?:service|an appointment|a quote)|get a quote|free estimate", txt, re.I): notes.append("no online booking/quote CTA")
    if len(html) > 900_000: notes.append("heavy page")
    res["quality_notes"] = notes
    res["site_score"] = max(0, 10 - 1.4 * len([n for n in notes]))  # 10 = strong site
    return res

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    sites = sorted({json.loads(l).get("website", "").split("?")[0] for l in open(src) if l.strip()} - {""})
    done = {}
    try:
        for l in open(dst): d = json.loads(l); done[d["website"]] = d
    except FileNotFoundError: pass
    todo = [s for s in sites if s not in done]
    print(len(sites), "sites,", len(todo), "to fetch", flush=True)
    with open(dst, "a") as f, cf.ThreadPoolExecutor(16) as ex:
        for i, r in enumerate(ex.map(enrich, todo)):
            f.write(json.dumps(r) + "\n")
            if i % 50 == 0: print(i, flush=True)
