import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

print("=== 1. CHECKING PDF & RAW MARKDOWN LINKS INSIDE VAULT NOTES ===")
vault_notes_checked = 0
broken_pdf_links = []
broken_raw_links = []

for root, dirs, files in os.walk(VAULT):
    for f in files:
        if f.endswith('.md') and not f.startswith('00-'):
            vault_notes_checked += 1
            md_path = os.path.join(root, f)
            with open(md_path, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read()
            pdf_matches = re.findall(r'\[PDF 原文\]\(<([^>]+)>\)', c)
            for target in pdf_matches:
                resolved_pdf = os.path.normpath(os.path.join(root, target))
                if not os.path.exists(resolved_pdf):
                    broken_pdf_links.append((f, target, resolved_pdf))
            raw_matches = re.findall(r'\[Markdown 原文\]\(<([^>]+)>\)', c)
            for target in raw_matches:
                resolved_raw = os.path.normpath(os.path.join(root, target))
                if not os.path.exists(resolved_raw):
                    broken_raw_links.append((f, target, resolved_raw))

print(f"Checked {vault_notes_checked} markdown notes in vault.")
if broken_pdf_links:
    print(f"❌ Found {len(broken_pdf_links)} broken PDF links!")
    for bf in broken_pdf_links[:5]:
        print(f"  {bf[0]}: {bf[1]}")
else:
    print("✅ 100% of [PDF 原文] links point to verified, existing PDFs!")

if broken_raw_links:
    print(f"❌ Found {len(broken_raw_links)} broken Markdown 原文 links!")
    for br in broken_raw_links[:5]:
        print(f"  {br[0]}: {br[1]}")
else:
    print("✅ 100% of [Markdown 原文] links point to verified, existing Raw Markdown files!")

print("\n=== 2. CHECKING RESIDUAL raw.md IN RAW-PAPERS ===")
weird_raw = []
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        if f.endswith(" raw.md"):
            weird_raw.append(f)

if weird_raw:
    print(f"⚠️ Found {len(weird_raw)} raw files with ' raw.md':")
    for w in weird_raw[:5]:
        print(" ", w)
else:
    print("✅ 0 files contain ' raw.md'! All raw markdowns properly use ' (Raw).md'!")
