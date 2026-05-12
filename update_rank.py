import csv
import io
import json
import re
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

LIMIT = 116
TRANC0_ZIP_URL = "https://tranco-list.eu/top-1m.csv.zip"

country_by_tld = {
    "cn":"中国", "hk":"中国", "tw":"中国", "jp":"日本", "kr":"韩国", "ru":"俄罗斯",
    "uk":"英国", "de":"德国", "fr":"法国", "in":"印度", "au":"澳大利亚", "ca":"加拿大",
    "sg":"新加坡", "nl":"荷兰", "se":"瑞典", "br":"巴西", "it":"意大利", "es":"西班牙"
}

known = {
    "google.com": ("Google", "美国", "全球搜索与互联网服务入口"),
    "youtube.com": ("YouTube", "美国", "全球视频内容与创作者平台"),
    "facebook.com": ("Facebook", "美国", "Meta 旗下社交网络平台"),
    "instagram.com": ("Instagram", "美国", "图片、短视频与社交内容平台"),
    "x.com": ("X / Twitter", "美国", "实时新闻、观点与社交平台"),
    "twitter.com": ("X / Twitter", "美国", "实时新闻、观点与社交平台"),
    "tiktok.com": ("TikTok", "中国", "字节跳动旗下全球短视频平台"),
    "baidu.com": ("Baidu", "中国", "中文搜索、AI 与信息服务平台"),
    "wikipedia.org": ("Wikipedia", "全球", "全球协作百科知识库"),
    "reddit.com": ("Reddit", "美国", "大型社区论坛与话题讨论平台"),
    "amazon.com": ("Amazon", "美国", "全球电商与云计算服务平台"),
    "netflix.com": ("Netflix", "美国", "全球流媒体影视平台"),
    "microsoft.com": ("Microsoft", "美国", "软件、云计算与办公生态"),
    "linkedin.com": ("LinkedIn", "美国", "职业社交与招聘平台"),
    "apple.com": ("Apple", "美国", "消费电子与数字服务生态"),
    "bing.com": ("Microsoft Bing", "美国", "微软搜索与 Copilot 入口"),
    "openai.com": ("OpenAI", "美国", "AI 模型与应用服务平台"),
    "chatgpt.com": ("ChatGPT", "美国", "OpenAI AI 对话入口"),
    "github.com": ("GitHub", "美国", "代码托管与开发者协作平台"),
    "cloudflare.com": ("Cloudflare", "美国", "CDN、DNS 与网络安全服务"),
    "qq.com": ("Tencent", "中国", "腾讯门户、社交与内容服务"),
    "taobao.com": ("Taobao", "中国", "阿里巴巴 C2C 电商平台"),
    "tmall.com": ("Tmall", "中国", "品牌电商与 B2C 平台"),
    "jd.com": ("JD", "中国", "自营电商与物流服务平台"),
    "alibaba.com": ("Alibaba", "中国", "B2B 跨境贸易平台"),
    "aliexpress.com": ("AliExpress", "中国", "阿里巴巴跨境电商平台"),
}

def guess_country(domain: str) -> str:
    tld = domain.rsplit(".", 1)[-1].lower()
    return country_by_tld.get(tld, "美国")

def pretty_name(domain: str) -> str:
    d = domain.lower()
    if d.startswith("www."):
        d = d[4:]
    base = d.split(".")[0]
    return re.sub(r"[-_]+", " ", base).title()

def load_existing():
    p = Path("sites.json")
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        rows = data.get("sites", data if isinstance(data, list) else [])
        return {x.get("domain","").lower(): x for x in rows}
    except Exception:
        return {}

existing = load_existing()

print("Downloading Tranco Top 1M...")
req = urllib.request.Request(TRANC0_ZIP_URL, headers={"User-Agent": "116-nav-updater/1.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    raw = resp.read()

with zipfile.ZipFile(io.BytesIO(raw)) as z:
    name = z.namelist()[0]
    csv_text = z.read(name).decode("utf-8", errors="ignore")

sites = []
reader = csv.reader(io.StringIO(csv_text))
for row in reader:
    if len(row) < 2:
        continue
    try:
        rank = int(row[0])
    except ValueError:
        continue
    domain = row[1].strip().lower()
    if not domain:
        continue

    old = existing.get(domain, {})
    if domain in known:
        name, country, desc = known[domain]
    else:
        name = old.get("name") or pretty_name(domain)
        country = old.get("country") or guess_country(domain)
        desc = old.get("desc") or "全球高权重网站"

    sites.append({
        "rank": rank,
        "name": name,
        "domain": domain,
        "country": country,
        "desc": desc
    })
    if len(sites) >= LIMIT:
        break

out = {
    "updatedAt": date.today().isoformat(),
    "source": "tranco",
    "sites": sites
}
Path("sites.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated sites.json with {len(sites)} sites.")
