import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

def win_path(p):
    ap = os.path.abspath(p)
    if not ap.startswith("\\\\?\\"):
        return "\\\\?\\" + ap
    return ap

def clean_toks(s):
    return set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', s) if len(w) > 2 and not w.isdigit())

# Collect all existing raw PDFs and raw MDs
all_raw_pdfs = {}
all_raw_mds = {}

for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        full_p = os.path.join(root, f)
        if f.endswith(".pdf"):
            all_raw_pdfs[f] = full_p
        elif f.endswith(" (Raw).md"):
            all_raw_mds[f] = full_p

# Inspect each note in vault
fixed = 0
for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    rel_vault = os.path.relpath(root, VAULT)
    if rel_vault == ".":
        continue
    expected_raw_dir = os.path.join(RAW, rel_vault)
    depth = len(rel_vault.split(os.sep))
    back_steps = "../" * (depth + 1)
    
    for f in files:
        if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            continue
            
        v_base = f[:-3]
        v_path = os.path.join(root, f)
        
        with open(win_path(v_path), "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            
        m_link = re.search(r"\[PDF 原文\]\(<([^>]+)>\)", content)
        if m_link:
            cand_p = os.path.normpath(os.path.join(root, m_link.group(1)))
            if os.path.exists(win_path(cand_p)):
                continue # valid link!
                
        # Needs fixing!
        # Find best matching PDF in all_raw_pdfs
        v_toks = clean_toks(v_base)
        first_w = re.split(r'[\s\(]+', v_base)[0].lower()
        
        best_cand = None
        best_score = 0
        for r_name, r_path in all_raw_pdfs.items():
            r_toks = clean_toks(r_name)
            overlap = len(v_toks & r_toks)
            if first_w in r_name.lower():
                overlap += 2
            if overlap > best_score and overlap >= 2:
                best_score = overlap
                best_cand = r_path
                
        if best_cand:
            # We found the real PDF!
            # Move/copy it into expected_raw_dir if not there, or point to it
            dest_pdf = os.path.join(expected_raw_dir, f"{v_base}.pdf")
            dest_raw = os.path.join(expected_raw_dir, f"{v_base} (Raw).md")
            
            # Find candidate's raw MD
            cand_stem = os.path.basename(best_cand)[:-4]
            cand_dir = os.path.dirname(best_cand)
            cand_raw = os.path.join(cand_dir, f"{cand_stem} (Raw).md")
            
            # If best_cand is not dest_pdf, rename/move it
            if os.path.normpath(best_cand) != os.path.normpath(dest_pdf):
                if not os.path.exists(win_path(dest_pdf)):
                    os.rename(win_path(best_cand), win_path(dest_pdf))
                if os.path.exists(win_path(cand_raw)) and not os.path.exists(win_path(dest_raw)):
                    os.rename(win_path(cand_raw), win_path(dest_raw))
                    
            # Build proper link
            rel_pdf = f"{back_steps}raw-papers/{rel_vault.replace(chr(92), '/')}/{v_base}.pdf"
            rel_raw = f"{back_steps}raw-papers/{rel_vault.replace(chr(92), '/')}/{v_base} (Raw).md"
            
            if os.path.exists(win_path(dest_raw)):
                archive_line = f"> **文獻存檔**：[PDF 原文](<{rel_pdf}>) | [Markdown 原文](<{rel_raw}>)"
            else:
                archive_line = f"> **文獻存檔**：[PDF 原文](<{rel_pdf}>)"
                
            if "> **文獻存檔**" in content or "[PDF 原文]" in content:
                content = re.sub(r'> \*\*文獻存檔\*\*:[^\n\r]+', archive_line, content)
                content = re.sub(r'> \*\*文獻存檔\*\*：[^\n\r]+', archive_line, content)
            else:
                m_h = re.search(r'(# [^\n\r]+\n\n)', content)
                if m_h:
                    content = content[:m_h.end()] + f"{archive_line}\n\n" + content[m_h.end():]
                    
            with open(win_path(v_path), "w", encoding="utf-8") as fp:
                fp.write(content)
            fixed += 1

print(f"Fixed {fixed} broken links!")
