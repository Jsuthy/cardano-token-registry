import json,glob,csv,re,os,collections,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from origin import origin
def normph(p):
  p=(p or '').strip(); m=re.match(r'^\+?1?[\s\.\-]*\(?(\d{3})\)?[\s\.\-]*(\d{3})[\s\.\-]*(\d{4})\s*(?:(ext\.?|x|extension)\s*(\d+))?$',p,re.I)
  return f'({m.group(1)}) {m.group(2)}-{m.group(3)}'+(f' ext. {m.group(5)}' if m.group(5) else '') if m else p
OUT=os.environ.get('OUT','..')
os.makedirs(OUT,exist_ok=True)
cands={c['ruling']:c for c in json.load(open('cands_f.json'))}
allc={c['ruling']:c for c in csv.DictReader(open('cands.csv'))}
excl=[]
if os.path.exists('exclude.csv'): excl=[r for r in csv.DictReader(open('exclude.csv'))]
def norm(s): return re.sub(r'[^a-z0-9]','',re.sub(r'\b(inc|llc|corp|corporation|co|ltd|company|the|usa|us|america|group|and)\b','',re.split(r'\b(dba|d/b/a)\b',(s or '').lower())[0].replace('&',' ')))
OVRALL=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'overrides.json'))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'overrides.json')) else {}
OVR=OVRALL.get('kill',{}); ORIG=OVRALL.get('origin',{})
res=[]
for f in sorted(glob.glob('results*/*.jsonl'),reverse=True):
  for line in open(f):
    line=line.strip()
    if not line: continue
    try: res.append(json.loads(line))
    except Exception: pass
# a keep from any pass wins over a kill; later passes override earlier kills
res.sort(key=lambda r: 0 if r.get('status')=='keep' else 1)
TOK=re.compile(r'owner|founder|president|\bceo\b|chief executive|\bcfo\b|chief financial|controller|\bcoo\b|chief operating|operations|import|logistics|supply chain|purchasing|procurement|trade compliance|customs compliance|managing member|principal|general manager',re.I)
keeps=[];kills=[];seen=set();seenphone=set()
PH=re.compile(r'^\(\d{3}\) \d{3}-\d{4}( (ext\.?|x) ?\d+)?$')
for r in res:
  key=norm(r.get('company'))
  if key in seen: continue
  seen.add(key)
  if r.get('status')=='keep':
    miss=[k for k in ['company','contact_name','title','phone','city','state','contact_source_url','evidence_url'] if not (r.get(k) or '').strip()]
    if key in OVR: kills.append((r['company'],OVR[key])); continue
    ck=(r.get('contact_name','').lower().strip(),r.get('state',''))
    if ck in seenphone: continue
    seenphone.add(ck)
    if miss or len(r['contact_name'].split())<2: kills.append((r.get('company'),'incomplete:'+','.join(miss) if miss else 'no-name')); continue
    if not TOK.search(r['title']) or re.search(r'vice president of (sales|marketing)|sales|marketing|product manager|engineer',r['title'],re.I) and not re.search(r'owner|president|ceo|founder',r['title'],re.I): kills.append((r['company'],'non-qualifying-title:'+r['title'])); continue
    r['phone']=normph(r['phone'])
    if not PH.match(r['phone'].strip()): kills.append((r['company'],'bad-phone-format:'+r['phone'])); continue
    if any(norm(e.get('Company') or e.get('company'))==key for e in excl): kills.append((r['company'],'excluded')); continue
    c,asia,ieepa=origin(r['ruling'])
    if not asia: kills.append((r['company'],f'non-asia-origin:{c}')); continue
    if c and c.endswith('?') and r['ruling'] not in ORIG: kills.append((r['company'],f'weak-import-evidence:origin unconfirmed ({c})')); continue
    r['_origin']=ORIG.get(r['ruling'],c.rstrip('?')); r['_ieepa']=ieepa
    keeps.append(r)
  else: kills.append((r.get('company') or r.get('ruling'),r.get('reason') or 'unspecified'))
for c in allc.values():
  if c['ruling'] not in cands and norm(c['company']) not in seen: kills.append((c['company'],'out-of-icp-size (prefilter: large/pharma/foreign parent)')); seen.add(norm(c['company']))
keeps=keeps[:300]
cols="Company,City/State,Phone,Segment,Est Refund Tier,Contact Name,Title,Email,Disposition,Callback Date/Time,Notes,Caller,Call Date".split(',')
with open(f'{OUT}/tariff-refund-prospects.csv','w',newline='') as fh:
  w=csv.writer(fh);w.writerow(cols)
  for r in keeps:
    src=r['contact_source_url']; ps=r.get('phone_source_url') or src
    srcs=src if ps==src else f"{src} ; phone: {ps}"
    ie='; ruling lists IEEPA 9903.01.xx duty' if r['_ieepa'] else ''
    notes=f"Import signal: {r.get('import_signal','').strip().rstrip('.')} (CBP ruling {r['ruling']}; origin {r['_origin']}{ie}). Call main line {r['phone']} and ask for {r['contact_name']} ({r['title']}). Evidence: {r['evidence_url']} ; contact: {srcs}"
    w.writerow([r['company'],f"{r['city']}, {r['state']}",r['phone'],'CAPE-IEEPA','unconfirmed',r['contact_name'],r['title'],r.get('email',''),'New','',notes,'',''])
with open(f'{OUT}/killed.csv','w',newline='') as fh:
  w=csv.writer(fh);w.writerow(['Company','reason']);w.writerows(kills)
cnt=collections.Counter(re.split(r'[:(]',k[1])[0].strip() for k in kills)
json.dump({'keeps':len(keeps),'kills':len(kills),'by_reason':cnt.most_common(),'results_rows':len(res),'cand_total':len(allc)},open('stats.json','w'),indent=1)
print(len(res),len(keeps),len(kills),cnt.most_common(12))
