import json,re,os
ASIA=['China','Vietnam','Viet Nam','Taiwan','India','Thailand','Malaysia','Indonesia','Cambodia','Korea','Philippines','Bangladesh','Pakistan','Sri Lanka','Hong Kong','Japan','Singapore','Burma','Myanmar','Laos']
A='|'.join(ASIA)
def origin(ruling):
  p=f'txt/{ruling}.json'
  if not os.path.exists(p):
    import urllib.request; d=json.load(urllib.request.urlopen(f'https://rulings.cbp.gov/api/ruling/{ruling}',timeout=60)); json.dump(d,open(p,'w'))
  d=json.load(open(p)); t=d['text']; subj=d.get('subject') or ''
  tariffs=d['tariffs'] if isinstance(d['tariffs'],str) else ';'.join(d['tariffs'] or [])
  ieepa=bool(re.search(r'9903\.01\.',tariffs+t))
  m=re.search(r'\bfrom (?:the )?([A-Z][a-zA-Z ]+?)(?:[\.;,]|$| and)',subj)
  c=None
  if m and not re.search(r'^(the )?(tariff|country)',m.group(1),re.I): c=m.group(1).strip()
  if not c:
    mm=re.search(r'(?:made|manufactured|produced|assembled|fabricated|sourced|imported|shipped|originat\w*|country of origin (?:is|of)|origin is)[^.]{0,120}?\b('+A+r')\b',t)
    if mm: c=mm.group(1)
  if not c:
    mm=re.search(r'\b('+A+r')\b',t)
    if mm: c=mm.group(1)+'?'
  asia=bool(c and re.search(r'\b('+A+r')\b',c))
  return c,asia,ieepa
