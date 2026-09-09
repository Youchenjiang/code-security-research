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

# Gather all raw pdfs
raw_pdfs = {} # filename -> full_path
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        if f.endswith(".pdf"):
            raw_pdfs[f] = os.path.join(root, f)

# Gather all raw mds
raw_mds = {} # filename -> full_path
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            raw_mds[f] = os.path.join(root, f)

def clean_toks(s):
    return set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', s) if len(w) > 2 and not w.isdigit())

vault_notes = []
for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("00-") and not re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            vault_notes.append((os.path.join(root, f), f[:-3], os.path.relpath(root, VAULT)))

print(f"Total vault notes: {len(vault_notes)}")
print(f"Total raw PDFs: {len(raw_pdfs)}")

matched = []
unmatched = []

for v_path, v_base, rel_genre in vault_notes:
    with open(v_path, "r", encoding="utf-8", errors="ignore") as fp:
        c = fp.read()
        
    found_pdf = None
    
    # 1. Existing link
    m_link = re.search(r"\[PDF 原文\]\(<([^>]+)>\)", c)
    if m_link:
        p = os.path.normpath(os.path.join(os.path.dirname(v_path), m_link.group(1)))
        if os.path.exists(p):
            found_pdf = p
            
    # 2. Source in frontmatter
    if not found_pdf:
        m_src = re.search(r"source:\s*[\"']?([^\"'\n\r]+)[\"']?", c)
        if m_src:
            src = m_src.group(1).strip()
            if src in raw_pdfs:
                found_pdf = raw_pdfs[src]
            elif src in raw_renames and raw_renames[src] in raw_pdfs:
                found_pdf = raw_pdfs[raw_renames[src]]
            else:
                # search by stem
                src_stem = re.sub(r'^\d+_', '', src.replace('.pdf', ''))
                src_toks = clean_toks(src_stem)
                for rf, rpath in raw_pdfs.items():
                    if clean_toks(rf) == src_toks or (len(src_toks) >= 2 and src_toks.issubset(clean_toks(rf))):
                        found_pdf = rpath
                        break
                        
    # 3. Exact stem match
    if not found_pdf:
        for rf, rpath in raw_pdfs.items():
            if rf[:-4].lower() == v_base.lower():
                found_pdf = rpath
                break
                
    # 4. Token match against v_base and title in content
    if not found_pdf:
        m_title = re.search(r"title:\s*[\"']?([^\"'\n\r]+)[\"']?", c)
        full_text = v_base + " " + (m_title.group(1) if m_title else "")
        v_toks = clean_toks(full_text)
        best_score = 0
        best_p = None
        for rf, rpath in raw_pdfs.items():
            r_toks = clean_toks(rf)
            overlap = len(v_toks & r_toks)
            if overlap > best_score and overlap >= 2:
                best_score = overlap
                best_p = rpath
        if best_p:
            found_pdf = best_p
            
    if found_pdf:
        matched.append((v_path, v_base, rel_genre, found_pdf))
    else:
        unmatched.append((v_path, v_base, rel_genre))

print(f"Matched: {len(matched)} / {len(vault_notes)}")
print(f"Unmatched: {len(unmatched)}")
for u in unmatched:
    print(f"  Unmatched: {u[1]} in {u[2]}")
