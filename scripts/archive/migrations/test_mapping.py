import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

with open(os.path.join(RAW, "legacy_archive", "spaces_rename_log.json"), "r", encoding="utf-8") as fp:
    rename_log = json.load(fp)

raw_renames = rename_log.get("raw_renames", {})

all_raw_files = {}
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        all_raw_files[f] = os.path.join(root, f)

mapped = 0
unmapped = []

for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    rel_dir = os.path.relpath(root, VAULT)
    if rel_dir == ".":
        continue
    
    for f in files:
        if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            continue
        canonical_base = f[:-3]
        md_p = os.path.join(root, f)
        with open(md_p, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            
        matched_pdf = None
        # Check 1: existing PDF link in note
        m_link = re.search(r"\[PDF 原文\]\(<([^>]+)>\)", content)
        if m_link:
            target_pdf = os.path.normpath(os.path.join(root, m_link.group(1)))
            if os.path.exists(target_pdf):
                matched_pdf = target_pdf
                
        # Check 2: source: field in frontmatter
        if not matched_pdf:
            m_src = re.search(r"source:\s*[\"']?([^\"'\n\r]+)[\"']?", content)
            if m_src:
                src_orig = m_src.group(1).strip()
                if src_orig in raw_renames:
                    curr_cand = raw_renames[src_orig]
                    if curr_cand in all_raw_files:
                        matched_pdf = all_raw_files[curr_cand]
                if not matched_pdf:
                    if src_orig in all_raw_files:
                        matched_pdf = all_raw_files[src_orig]
                        
        # Check 3: exact or case-insensitive match anywhere
        if not matched_pdf:
            for rf, rpath in all_raw_files.items():
                if rf.endswith(".pdf"):
                    if rf[:-4].lower() == canonical_base.lower():
                        matched_pdf = rpath
                        break
                        
        # Check 4: tokens match
        if not matched_pdf:
            tokens = [t.lower() for t in re.split(r"[\s\(\)]+", canonical_base) if len(t) > 3]
            for rf, rpath in all_raw_files.items():
                if rf.endswith(".pdf"):
                    rf_lower = rf.lower()
                    if all(tok in rf_lower for tok in tokens[:2]) if len(tokens) >= 2 else (tokens[0] in rf_lower if tokens else False):
                        matched_pdf = rpath
                        break
                        
        if matched_pdf:
            mapped += 1
        else:
            unmapped.append((rel_dir, canonical_base))

print(f"Total notes: {mapped + len(unmapped)}")
print(f"Mapped: {mapped}")
print(f"Unmapped: {len(unmapped)}")
for r, cb in unmapped:
    print(f"  Unmapped: {cb} in {r}")
