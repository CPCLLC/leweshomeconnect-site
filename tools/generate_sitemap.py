#!/usr/bin/env python3
import os, datetime, urllib.parse

# CONFIG
BASE_URL = os.getenv("SITE_URL", "https://leweshomeconnect.com").rstrip("/")
EXCLUDE_DIRS = {".git", ".github", "node_modules", "assets", "static", "public"}
EXCLUDE_FILES = {"404.html", "sitemap.xml", "robots.txt"}
HTML_EXTS = {".html", ".htm"}

def is_page(path):
    # Only include .html/.htm at repo root or subdirs (excluding excluded dirs/files)
    if not os.path.isfile(path): return False
    name = os.path.basename(path)
    if name in EXCLUDE_FILES: return False
    ext = os.path.splitext(name)[1].lower()
    if ext not in HTML_EXTS: return False
    parts = set(os.path.normpath(path).split(os.sep))
    if parts & EXCLUDE_DIRS: return False
    return True

def to_url(path):
    # Turn local file path into site URL
    rel = os.path.relpath(path, ".").replace(os.sep, "/")
    if rel.lower().endswith(("index.html","index.htm")):
        rel = rel.rsplit("/",1)[0] if "/" in rel else ""
    else:
        # drop .html/.htm but keep path segment
        rel = rel[:-5] if rel.lower().endswith(".html") else (rel[:-4] if rel.lower().endswith(".htm") else rel)
    return f"{BASE_URL}/" + urllib.parse.quote(rel, safe="/")

def lastmod_iso():
    # Current date (UTC) – simple, reliable
    return datetime.datetime.utcnow().date().isoformat()

pages = []
for root, dirs, files in os.walk("."):
    # prune excluded dirs early
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
    for f in files:
        fp = os.path.join(root, f)
        if is_page(fp):
            pages.append(fp)

# Always include homepage if index.html exists (or if you just want it anyway)
if "index.html" not in {os.path.basename(p) for p in pages} and os.path.exists("index.html"):
    pages.append("index.html")

pages = sorted(set(pages))

urls = []
for p in pages:
    urls.append({
        "loc": to_url(p).rstrip("/"),
        "lastmod": lastmod_iso(),
        "priority": "1.0" if os.path.basename(p).lower() in ("index.html","index.htm") else "0.8",
        "changefreq": "monthly"
    })

xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    xml.append("  <url>")
    xml.append(f"    <loc>{u['loc'] or BASE_URL}</loc>")
    xml.append(f"    <lastmod>{u['lastmod']}</lastmod>")
    xml.append(f"    <changefreq>{u['changefreq']}</changefreq>")
    xml.append(f"    <priority>{u['priority']}</priority>")
    xml.append("  </url>")
xml.append("</urlset>")

os.makedirs(".", exist_ok=True)
with open("sitemap.xml","w",encoding="utf-8") as f:
    f.write("\n".join(xml))
print(f"Generated sitemap.xml with {len(urls)} URLs.")
