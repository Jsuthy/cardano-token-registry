import json,os,re,csv
ST="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR".split()
BAD=re.compile(r"\b(LLP|L\.L\.P|law|attorney|legal|counsel|customs|broker|brokerage|forward|logistic|freight|shipping|expedit|trade (services|consult|advis)|consult|advisory|CHB|compliance group|compliance services|3PL|global trade|PLLC|P\.C\.|KPMG|Deloitte|Ernst|PwC|Pricewaterhouse|BDO|Grant Thornton|Livingston|Expeditors|Kuehne|DHL|UPS|FedEx|C\.H\. Robinson|Flexport|Geodis|Nippon Express|Mohawk Global|Sandler|Barnes Richardson|Tarter|Crowell|Baker|Akin|Kelley Drye|Hogan|Squire|Dentons|Thompson Hine|Neville Peterson|Grunfeld|deKieffer|Arent|Cozen|Mayer Brown)\b",re.I)
BIG=re.compile(r"\b(Walmart|Wal-Mart|Target|Amazon|Home Depot|Lowe's|Costco|Apple|Google|Microsoft|Ford|General Motors|Toyota|Honda|Samsung|LG |Sony|Nike|Adidas|Under Armour|Hasbro|Mattel|Dell|HP |Hewlett|IBM|Intel|Cisco|Tesla|Barnes and Noble|Best Buy|Kohl|Macy|Nordstrom|TJX|Ross Stores|Dollar|Williams-Sonoma|Wayfair|Bed Bath|Staples|Office Depot|Walgreens|CVS|Kroger|Tractor Supply|Harbor Freight|Stanley Black|3M|Honeywell|General Electric|Caterpillar|Deere|Whirlpool|Procter|Johnson & Johnson|Medtronic|Abbott|Boeing|Lockheed|Raytheon|Siemens|Bosch|Panasonic|Philips|Canon|Epson|Brother|Lenovo|Acer|Asus|Logitech|Garmin|Skechers|VF |PVH|Ralph Lauren|Levi|Gap Inc|Hanesbrands|Columbia Sportswear|Crocs|Deckers|Wolverine|Steve Madden|Lululemon|Victoria|Bath & Body|Newell|Spectrum Brands|Energizer|Kimberly|Colgate|Unilever|Nestle|PepsiCo|Coca|Tapestry|Capri|Fossil|Kontoor|Carter's|Oshkosh|Target Corp|Meta Platforms|Qualcomm|Nvidia|AMD|Micron|Texas Instruments|Broadcom|Pfizer|Merck|Bayer|BASF|Dow|DuPont|Exxon|Chevron|Shell)\b",re.I)
TITLE=re.compile(r"\b(President|CEO|Chief|Owner|Founder|CFO|Controller|Vice President|VP|Director|Manager|Supervisor|Specialist|Analyst|Coordinator|Counsel|Officer|Principal|Partner|Head|Lead|Associate|Buyer|Engineer|Administrator|Agent|Senior|Sr\.)\b")
rows=[]
for f in sorted(os.listdir('txt')):
  d=json.load(open('txt/'+f)); t=d['text']
  m=re.search(r'\bRE:\s*(.*?)Dear\s+(.*?):(.*)',t,re.S)
  if not m: continue
  subj,sal,rest=m.groups(); pre=t[:m.start()]
  hs=list(re.finditer(r'TARIFF NOS?\.?:?|CATEGORY:',pre))
  if not hs: continue
  block=pre[hs[-1].end():]
  block=re.sub(r'^[\s\d\.;,:/\-]*(?:and[\s\d\.;,]*)*','',block)
  block=re.sub(r'^(?:(?:Classification|Origin|Country of Origin|Marking|Trade|Carriers|Valuation|Other)[\s,;]*)+','',block)
  block=re.sub(r'^[\s\d\.;,:/\-]*(?:and[\s\d\.;,]*)*','',block)
  if re.search(r'TARIFF NO',block): continue
  para=rest[:900]
  if re.search(r'on behalf of|your client|behalf of your',para,re.I): continue
  parts=[p.strip() for p in re.split(r'\s{2,}|\n',block) if p.strip()]
  # find city,state zip
  loc=None
  for i,p in enumerate(parts):
    mm=re.search(r'([A-Za-z\.\' ]+),?\s+([A-Z]{2})\.?\s+(\d{5})',p)
    if mm and mm.group(2) in ST: loc=(i,mm.group(1).strip().rstrip(','),mm.group(2)); break
  if not loc: continue
  if len(parts)<3: continue
  name=re.sub(r'^(Mr\.|Ms\.|Mrs\.|Dr\.|Miss)\s*','',parts[0])
  title='';comp=''
  if len(parts)>1 and TITLE.search(parts[1]) and not re.search(r'\b(Inc|LLC|Corp|Co\.|Ltd|Company)\b',parts[1]): title=parts[1]; comp=parts[2] if len(parts)>2 else ''
  else: comp=parts[1]
  if ',' in name and TITLE.search(name.split(',',1)[1]): name,title=[x.strip() for x in name.split(',',1)]
  if BAD.search(comp) or BAD.search(title) or BIG.search(comp): continue
  if len(name.split())<2 or len(name.split())>4: continue
  rows.append(dict(ruling=d['rulingNumber'],date=d['rulingDate'][:10],name=name,title=title,company=comp,city=loc[1],state=loc[2],subject=re.sub(r'\s+',' ',subj)[:160],tariffs=d['tariffs'] if isinstance(d['tariffs'],str) else ';'.join(d['tariffs'] or []),url=f"https://rulings.cbp.gov/ruling/{d['rulingNumber']}"))
# dedupe by company
by={}
for r in sorted(rows,key=lambda r:r['date'],reverse=True):
  k=re.sub(r'[^a-z0-9]','',re.sub(r'\b(inc|llc|corp|corporation|co|ltd|company|the|usa|us|america)\b','',r['company'].lower()))
  by.setdefault(k,r)
w=csv.DictWriter(open('cands.csv','w'),fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(by.values())
print(len(rows),len(by))
