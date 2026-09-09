import os
import sys
import re
import difflib

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

def clean_alphanum(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

def get_keywords(s):
    words = re.findall(r'[a-zA-Z0-9]+', s)
    return set(w.lower() for w in words if len(w) > 2 and not w.isdigit())

# Collect all raw pdfs and raw mds
raw_pdfs = []
raw_mds = []

for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        full_p = os.path.join(root, f)
        if f.endswith(".pdf"):
            raw_pdfs.append((full_p, f, f[:-4]))
        elif f.endswith(".md"):
            raw_mds.append((full_p, f, f[:-3]))

print(f"Found {len(raw_pdfs)} PDFs and {len(raw_mds)} Raw MDs in raw-papers.")

# Collect all vault paper notes
vault_notes = []
for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("00-") and not re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            vault_notes.append((os.path.join(root, f), f, f[:-3], root))

print(f"Found {len(vault_notes)} Vault notes to align.")

matches = []
unmatched = []

used_pdfs = set()

for v_path, v_file, v_base, v_root in vault_notes:
    with open(v_path, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
        
    rel_vault_dir = os.path.relpath(v_root, VAULT)
    expected_raw_dir = os.path.join(RAW, rel_vault_dir)
    
    # Candidate PDFs, prioritize those in expected_raw_dir
    local_pdfs = [p for p in raw_pdfs if os.path.dirname(p[0]) == expected_raw_dir and p[0] not in used_pdfs]
    other_pdfs = [p for p in raw_pdfs if os.path.dirname(p[0]) != expected_raw_dir and p[0] not in used_pdfs]
    
    matched_pdf = None
    
    # 1. Existing link in note
    m_link = re.search(r"\[PDF 原文\]\(<([^>]+)>\)", content)
    if m_link:
        target_p = os.path.normpath(os.path.join(v_root, m_link.group(1)))
        for p in raw_pdfs:
            if os.path.normpath(p[0]) == target_p:
                matched_pdf = p
                break
                
    # 2. Source in frontmatter
    if not matched_pdf:
        m_src = re.search(r"source:\s*[\"']?([^\"'\n\r]+)[\"']?", content)
        if m_src:
            src_name = m_src.group(1).strip()
            # Try to match src_name against local_pdfs then other_pdfs
            src_clean = clean_alphanum(src_name)
            for p in local_pdfs + other_pdfs:
                if clean_alphanum(p[1]) == src_clean or clean_alphanum(p[2]) == src_clean:
                    matched_pdf = p
                    break
                    
    # 3. Clean alphanum exact match on title
    if not matched_pdf:
        v_clean = clean_alphanum(v_base)
        for p in local_pdfs:
            if clean_alphanum(p[2]) == v_clean:
                matched_pdf = p
                break
                
    # 4. Keyword overlap
    if not matched_pdf:
        v_kw = get_keywords(v_base)
        best_score = 0
        best_p = None
        for p in local_pdfs:
            p_kw = get_keywords(p[2])
            overlap = len(v_kw & p_kw)
            if overlap > best_score and overlap >= 2:
                best_score = overlap
                best_p = p
        if best_p:
            matched_pdf = best_p
            
    # 5. Global search if still not found
    if not matched_pdf:
        v_kw = get_keywords(v_base)
        best_score = 0
        best_p = None
        for p in other_pdfs:
            p_kw = get_keywords(p[2])
            overlap = len(v_kw & p_kw)
            if overlap > best_score and overlap >= 3:
                best_score = overlap
                best_p = p
        if best_p:
            matched_pdf = best_p

    if matched_pdf:
        used_pdfs.add(matched_pdf[0])
        # Find matching raw md for this pdf
        # Raw md usually has same dirname and same base or base + ' raw' or base + ' (Raw)'
        pdf_dir = os.path.dirname(matched_pdf[0])
        pdf_stem = matched_pdf[2]
        
        matched_raw_md = None
        for m in raw_mds:
            if os.path.dirname(m[0]) == pdf_dir:
                m_stem = m[2]
                if m_stem == pdf_stem or m_stem == f"{pdf_stem} raw" or m_stem == f"{pdf_stem} (Raw)" or clean_alphanum(m_stem) == clean_alphanum(pdf_stem) or clean_alphanum(m_stem) == clean_alphanum(f"{pdf_stem}raw"):
                    matched_raw_md = m
                    break
        matches.append((v_path, v_base, v_root, matched_pdf, matched_raw_md))
    else:
        unmatched.append((v_path, v_base, rel_vault_dir))

print(f"\nSuccessfully matched: {len(matches)} / {len(vault_notes)}")
print(f"Unmatched notes: {len(unmatched)}")
if unmatched:
    print("Unmatched samples:")
    for u in unmatched[:10]:
        print(f"  {u[1]} (in {u[2]})")
