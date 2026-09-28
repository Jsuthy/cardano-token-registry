# Build the secondary candidate pool: importer names quoted in broker/attorney-filed rulings
# ("... on behalf of your client, X Inc."). Run after parse.py; writes pool2.json.
import json,os,re,csv
exec(open('parse.py').read().split('rows=[]')[0])  # reuse BAD / BIG regexes
done={re.sub(r'[^a-z0-9]','',c['company'].lower()) for c in csv.DictReader(open('cands.csv'))}
SKIP_SUBJ=re.compile(r'tablet|capsule|injection|pharmac|API\b|drug|vaccine|frozen|fresh|shrimp|seafood|tea\b|coffee|juice|sauce|noodle|rice\b|beverage|wine|beer|spirits|liquor|candy|chocolate|cookie|snack|egg|meat|fish|fruit|vegetable|spice|dosage|oral|ophthalmic|supplement|vitamin|powder for|cannabi|hemp|tobacco|cigar|vape|vaporizer|e-cigarette|nicotine',re.I)
SKIP_CO=re.compile(r'Pharma|Laborator|Therapeut|Bio|Foods?\b|Trading Co\.|Import Export|Seafood|Beverage|Health Sciences|Co\., Ltd|Limited|GmbH|S\.A\.|Pte|Pvt|Shenzhen|Ningbo|Guangzhou|Zhejiang|Jiangsu|Xiamen|Shanghai|Hong Kong',re.I)
out={}
for f in os.listdir('txt'):
  d=json.load(open('txt/'+f));t=d['text']
  m=re.search(r'on behalf of\s+(?:your clients?,?\s*)?([A-Z][A-Za-z0-9&\.,\'\- ]{2,70}?(?:Inc\.?|LLC|L\.L\.C\.|Corp(?:oration)?\.?|Co\.|Company|Ltd\.?|LP|L\.P\.|Incorporated))[\s,\.\(]',t)
  if not m: continue
  comp=re.sub(r'([a-z])([A-Z])',r'\1 \2',re.sub(r'\s+',' ',m.group(1).strip().rstrip(',')))
  subj=re.search(r'RE:\s*(.*?)Dear',t,re.S); subj=re.sub(r'\s+',' ',subj.group(1))[:160] if subj else ''
  if BAD.search(comp) or BIG.search(comp) or SKIP_CO.search(comp) or SKIP_SUBJ.search(subj): continue
  k=re.sub(r'[^a-z0-9]','',comp.lower())
  if k in done or k in out: continue
  out[k]=dict(ruling=d['rulingNumber'],date=d['rulingDate'][:10],name='',company=comp,city='',state='',subject=subj,tariffs=d['tariffs'] if isinstance(d['tariffs'],str) else ';'.join(d['tariffs'] or []),url=f"https://rulings.cbp.gov/ruling/{d['rulingNumber']}")
json.dump(sorted(out.values(),key=lambda x:x['date'],reverse=True),open('pool2.json','w'))
print(len(out))
