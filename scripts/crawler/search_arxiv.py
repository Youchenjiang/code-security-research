#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArXiv Academic Search Tool
==========================
Batch search and query ArXiv for papers by title keywords.
"""

import re
import sys
import argparse
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def search_arxiv(query_text: str, max_results: int = 5):
    clean_t = re.sub(r'[^a-zA-Z0-9\s]', ' ', query_text).strip()
    words = [w for w in clean_t.split() if len(w) > 2][:8]
    query = " AND ".join([f'all:"{w}"' for w in words])
    api_url = f"http://export.arxiv.org/api/query?search_query={quote(query)}&max_results={max_results}"

    print(f"🔍 搜尋關鍵詞: {' '.join(words)}")
    try:
        r = requests.get(api_url, timeout=15)
        if r.status_code != 200:
            print(f"❌ ArXiv 回應錯誤: HTTP {r.status_code}")
            return []

        root = ET.fromstring(r.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        results = []

        for e in entries:
            title = e.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = e.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = e.find('atom:published', ns).text[:10]
            pdf_link = None
            for link in e.findall('atom:link', ns):
                if link.attrib.get('title') == 'pdf':
                    pdf_link = link.attrib.get('href')
                    if not pdf_link.endswith('.pdf'):
                        pdf_link += '.pdf'

            results.append({
                'title': title,
                'date': published,
                'pdf': pdf_link,
                'summary': summary[:150] + '...'
            })

        return results
    except Exception as err:
        print(f"❌ 查詢失敗: {err}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Search ArXiv for Academic Papers")
    parser.add_argument("query", help="Search query or paper title")
    parser.add_argument("--max", type=int, default=5, help="Maximum results to return")
    args = parser.parse_args()

    results = search_arxiv(args.query, args.max)
    if not results:
        print("未找到相符論文。")
        return 0

    print(f"\n找到 {len(results)} 篇相關論文:")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['title']} ({r['date']})")
        print(f"    PDF: {r['pdf']}")
        print(f"    摘要: {r['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
