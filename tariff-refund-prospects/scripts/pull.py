import json,urllib.request,urllib.parse,time,sys,os
out={}
if os.path.exists('index.json'): out=json.load(open('index.json'))
for term in sys.argv[1:]:
  for p in range(1,40):
    u=f"https://rulings.cbp.gov/api/search?term={urllib.parse.quote(term)}&collection=NY&commodityGrouping=ALL&pageSize=100&page={p}&sortBy=DATE_DESC"
    for a in range(3):
      try: d=json.load(urllib.request.urlopen(u,timeout=60)); break
      except Exception as e: time.sleep(3)
    r=d['rulings']
    if not r: break
    for x in r: out[x['rulingNumber']]=x
    last=r[-1]['rulingDate']
    print(term,p,last,flush=True)
    if last<'2024-09-28': break
json.dump(out,open('index.json','w'))
print(len(out))
