#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, io, json, os, re, zipfile, urllib.request
from datetime import date
from pathlib import Path
LIMIT = 116
TRANKO_URL = "https://tranco-list.eu/top-1m.csv.zip"
BLOCK_KEYWORDS = ["porn","sex","xxx","xvideos","xnxx","onlyfans","chaturbate","bet","casino","gambling","poker","torrent","piratebay"]
COUNTRY_BY_TLD = {"cn":"中国","hk":"中国","tw":"中国","jp":"日本","kr":"韩国","ru":"俄罗斯","uk":"英国","de":"德国","fr":"法国","in":"印度","au":"澳大利亚","ca":"加拿大","sg":"新加坡","nl":"荷兰","se":"瑞典","br":"巴西","it":"意大利","es":"西班牙"}
CATEGORY_RULES = {
    "ai":["AI"], "openai":["AI"], "chatgpt":["AI"], "huggingface":["AI","开发者"],
    "github":["开发者"], "stackoverflow":["开发者"], "cloudflare":["开发者","工具"], "vercel":["开发者"],
    "facebook":["社交"], "instagram":["社交"], "x.com":["社交","新闻"], "twitter":["社交","新闻"], "reddit":["社交"], "tiktok":["社交","视频"], "youtube":["视频","社交"],
    "amazon":["电商","跨境电商"], "alibaba":["电商","跨境电商"], "aliexpress":["电商","跨境电商"], "shopify":["电商","跨境电商"], "ebay":["电商","跨境电商"],
    "bbc":["新闻"], "cnn":["新闻"], "reuters":["新闻"], "bloomberg":["新闻"], "nytimes":["新闻"],
    "coursera":["教育"], "edx":["教育"], "khanacademy":["教育"], "duolingo":["教育"], "leetcode":["教育","开发者"]
}
def clean_domain(d):
    d=d.strip().lower(); d=re.sub(r"^https?://","",d).split('/')[0]; return d

def is_safe(domain):
    low=domain.lower(); return not any(k in low for k in BLOCK_KEYWORDS)

def guess_country(domain):
    return COUNTRY_BY_TLD.get(domain.split('.')[-1].lower(), '美国')

def guess_categories(domain):
    cats=[]
    for key, vals in CATEGORY_RULES.items():
        if key in domain:
            cats.extend(vals)
    if domain.endswith('.cn') or any(x in domain for x in ['baidu','taobao','tmall','jd.com','qq.com','weibo','zhihu','bilibili','douyin','alipay','aliyun']): cats.append('中国')
    return list(dict.fromkeys(cats))

def fetch_tranco():
    req=urllib.request.Request(TRANKO_URL,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=60) as r: data=r.read()
    z=zipfile.ZipFile(io.BytesIO(data)); name=z.namelist()[0]
    domains=[]
    with z.open(name) as f:
        text=io.TextIOWrapper(f,encoding='utf-8')
        for row in csv.reader(text):
            if len(row)<2: continue
            d=clean_domain(row[1])
            if d and is_safe(d): domains.append(d)
            if len(domains)>=LIMIT: break
    return domains

def load_old():
    if not os.path.exists('sites.json'): return {}
    with open('sites.json','r',encoding='utf-8') as f:
        return {x['domain'].lower():x for x in json.load(f)}

def build_sitemap():
    today=date.today().isoformat()
    pages=['index.html','top-websites.html','ai-tools.html','social-media.html','cross-border.html','ecommerce.html','developer-tools.html','news-media.html','free-images.html','education.html','china-websites.html','tech-tools.html','en/index.html']
    smap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        loc='https://116.ccwu.cc/' if p=='index.html' else 'https://116.ccwu.cc/'+p
        pr='1.0' if p=='index.html' else '0.8'
        smap+=f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>{pr}</priority></url>\n'
    smap+='</urlset>\n'; Path('sitemap.xml').write_text(smap,encoding='utf-8')

def main():
    old=load_old()
    try:
        domains=fetch_tranco(); print('Fetched Tranco safe list:',len(domains))
    except Exception as e:
        print('Fetch failed, keeping current sites.json:',e)
        with open('sites.json','r',encoding='utf-8') as f: sites=json.load(f)[:LIMIT]
        build_sitemap(); return
    sites=[]
    for i,d in enumerate(domains,1):
        o=old.get(d,{})
        old_rank=o.get('rank')
        change=(old_rank-i) if isinstance(old_rank,int) else None
        sites.append({
            'rank':i,
            'prev_rank':old_rank,
            'change':change,
            'name':o.get('name') or d.split('.')[0].replace('-',' ').title(),
            'domain':d,
            'country':o.get('country') or guess_country(d),
            'desc':o.get('desc') or '全球高权重网站',
            'categories':o.get('categories') or guess_categories(d)
        })
    Path('sites.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2),encoding='utf-8')
    build_sitemap()
if __name__=='__main__': main()
