#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Paper Downloader & Resolver
=====================================
Supports downloading academic papers from:
- Direct PDF URLs
- ArXiv (via ArXiv API query by title/DOI/ID)
- OpenAccess / Unpaywall resolvers
- Local PDF validation (%PDF- header check, minimum size check)
"""

import os
import sys
import re
import argparse
import requests
from urllib.parse import quote

# UTF-8 for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def is_valid_pdf(fpath: str) -> bool:
    """Validate that the downloaded file is a valid PDF (>15KB and begins with %PDF-)."""
    if not os.path.exists(fpath):
        return False
    if os.path.getsize(fpath) < 15000:
        return False
    try:
        with open(fpath, 'rb') as f:
            header = f.read(5)
            return header.startswith(b'%PDF-')
    except Exception:
        return False


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip()[:150]


def download_url(url: str, out_path: str, referer: str = None, timeout: int = 30) -> bool:
    """Download a file with streaming and validate PDF format."""
    if not url:
        return False
    h = dict(HEADERS)
    if referer:
        h['Referer'] = referer

    tmp_path = out_path + ".downloading"
    try:
        r = requests.get(url, headers=h, timeout=timeout, allow_redirects=True, stream=True)
        if r.status_code == 200:
            with open(tmp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            if is_valid_pdf(tmp_path):
                if os.path.exists(out_path):
                    os.remove(out_path)
                os.rename(tmp_path, out_path)
                return True
    except Exception as e:
        print(f"  ❌ 下載失敗 ({url}): {e}")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    return False


def download_from_arxiv(title: str, out_path: str) -> bool:
    """Query ArXiv API by title words and download matching PDF."""
    clean_t = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).strip()
    words = [w for w in clean_t.split() if len(w) > 3][:6]
    if not words:
        return False

    query = " AND ".join([f'ti:"{w}"' for w in words])
    api_url = f"http://export.arxiv.org/api/query?search_query={quote(query)}&max_results=3"

    try:
        r = requests.get(api_url, timeout=15)
        if r.status_code == 200:
            # Extract pdf url from xml
            m = re.search(r'<link[^>]+title="pdf"[^>]+href="([^"]+)"', r.text)
            if m:
                pdf_url = m.group(1)
                if not pdf_url.endswith('.pdf'):
                    pdf_url += '.pdf'
                print(f"  🔍 發現 ArXiv 來源: {pdf_url}")
                return download_url(pdf_url, out_path)
    except Exception as e:
        print(f"  ❌ ArXiv 檢索出錯: {e}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Universal Academic Paper Downloader")
    parser.add_argument("--url", help="Direct PDF URL")
    parser.add_argument("--title", help="Paper title for ArXiv / Semantic Scholar search")
    parser.add_argument("--out", required=True, help="Output file path (.pdf)")
    parser.add_argument("--referer", help="Optional HTTP referer")
    args = parser.parse_args()

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)

    if args.url:
        print(f"🚀 嘗試從 URL 下載: {args.url}")
        if download_url(args.url, args.out, referer=args.referer):
            print(f"✅ 下載成功: {args.out}")
            return 0

    if args.title:
        print(f"🚀 嘗試從 ArXiv 搜尋論文標題: {args.title}")
        if download_from_arxiv(args.title, args.out):
            print(f"✅ ArXiv 下載成功: {args.out}")
            return 0

    print(f"❌ 無法成功下載論文。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
