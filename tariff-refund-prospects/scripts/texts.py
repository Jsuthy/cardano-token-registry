import json,urllib.request,os,concurrent.futures as cf
idx=json.load(open('index.json'))
ids=[k for k,v in idx.items() if v['rulingDate']>='2024-09-28']
os.makedirs('txt',exist_ok=True)
def f(k):
  p=f'txt/{k}.json'
  if os.path.exists(p): return
  for a in range(3):
    try:
      d=json.load(urllib.request.urlopen(f'https://rulings.cbp.gov/api/ruling/{k}',timeout=60)); json.dump(d,open(p,'w')); return
    except Exception: pass
with cf.ThreadPoolExecutor(6) as ex: list(ex.map(f,ids))
print(len(ids),len(os.listdir('txt')))
