#!/usr/bin/env python3
"""Free public RSS monitor. No X live API; source timestamps may be delayed."""
import json, re, html, datetime, urllib.request, xml.etree.ElementTree as ET, pathlib
from email.utils import parsedate_to_datetime
SOURCES=[
 ("Cointelegraph","https://cointelegraph.com/rss"),
 ("Decrypt","https://decrypt.co/feed"),
 ("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),
 ("Google News - Pump.fun","https://news.google.com/rss/search?q=pump.fun+OR+memecoin&hl=en-US&gl=US&ceid=US:en"),
 ("Google News - Binance","https://news.google.com/rss/search?q=Binance+Alpha+OR+four.meme&hl=en-US&gl=US&ceid=US:en"),
 ("Google News - Celebrity memes","https://news.google.com/rss/search?q=%22Elon+Musk%22+memecoin+OR+%22Trump%22+memecoin&hl=en-US&gl=US&ceid=US:en")
]
TERMS={"pump.fun":5,"memecoin":4,"meme coin":4,"binance alpha":5,"four.meme":5,"solana":2,"viral":2,"elon musk":3,"trump":3,"kimchi":3,"launch":1,"listing":2,"celebrity":2,"dog":1,"cat":1}
def date(s):
 try:return parsedate_to_datetime(s).astimezone(datetime.timezone.utc).isoformat()
 except:return None
items=[]; failures=[]
for source,url in SOURCES:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 ZDMemeNewsRadar/1.0"})
  with urllib.request.urlopen(req,timeout=14) as response: raw=response.read(1000000)
  root=ET.fromstring(raw)
  entries=root.findall(".//item")
  for e in entries[:45]:
   title=html.unescape(" ".join((e.findtext("title") or "").split()))
   link=(e.findtext("link") or "").strip()
   description=re.sub("<[^>]+>"," ",e.findtext("description") or "")
   body=(title+" "+description).lower()
   score=sum(n for term,n in TERMS.items() if term in body)
   if score<3 or not link.startswith("https://"):continue
   items.append({"title":title[:220],"link":link,"source":source,"published":date(e.findtext("pubDate") or ""),"score":min(score,20)})
 except Exception as ex:failures.append(source+": "+str(ex)[:100])
unique={}
for i in items:
 key=re.sub(r"[^a-z0-9]+","",i["title"].lower())[:100]
 if key not in unique or i["score"]>unique[key]["score"]: unique[key]=i
news=sorted(unique.values(),key=lambda x:(x["published"] or "",x["score"]),reverse=True)[:120]
data={"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sourceStatus":{"successful":len(SOURCES)-len(failures),"failed":len(failures)},"disclaimer":"Public RSS / Google News only, not direct X posts. Delays vary. Rankings are keyword-based, not AI.", "items":news}
pathlib.Path("news.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("News:",len(news),"Failures:",failures)
