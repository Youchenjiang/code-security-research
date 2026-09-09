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

# 1. Any file ending with ' raw.md' in raw-papers, if not yet renamed, rename it to ' (Raw).md'
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        if f.endswith(" raw.md"):
            old_p = os.path.join(root, f)
            new_name = f[:-7] + " (Raw).md"
            new_p = os.path.join(root, new_name)
            if os.path.exists(win_path(new_p)):
                os.remove(win_path(old_p))
            else:
                os.rename(win_path(old_p), win_path(new_p))
            print(f"Renamed raw MD: {f} -> {new_name}")

# 2. Gather all current raw PDFs and raw (Raw).md
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

# 3. For every vault note, ensure matching PDF and (Raw).md in expected genre directory
aligned = 0
for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    rel_vault = os.path.relpath(root, VAULT)
    if rel_vault == ".":
        continue
    expected_raw_dir = os.path.join(RAW, rel_vault)
    os.makedirs(expected_raw_dir, exist_ok=True)
    
    for f in files:
        if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            continue
            
        v_base = f[:-3]
        target_pdf = os.path.join(expected_raw_dir, f"{v_base}.pdf")
        target_raw = os.path.join(expected_raw_dir, f"{v_base} (Raw).md")
        
        # Check if already perfectly aligned
        if not os.path.exists(win_path(target_pdf)):
            # Find candidate PDF in all_raw_pdfs
            # Try token overlap
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
                    
            if best_cand and os.path.exists(win_path(best_cand)):
                # Find matching raw md for best_cand
                cand_dir = os.path.dirname(best_cand)
                cand_stem = os.path.basename(best_cand)[:-4]
                cand_raw = os.path.join(cand_dir, f"{cand_stem} (Raw).md")
                
                # Move and rename PDF
                if os.path.exists(win_path(target_pdf)):
                    os.remove(win_path(target_pdf))
                os.rename(win_path(best_cand), win_path(target_pdf))
                all_raw_pdfs[f"{v_base}.pdf"] = target_pdf
                
                # Move and rename Raw MD
                if os.path.exists(win_path(cand_raw)):
                    if os.path.exists(win_path(target_raw)):
                        os.remove(win_path(target_raw))
                    os.rename(win_path(cand_raw), win_path(target_raw))
                    all_raw_mds[f"{v_base} (Raw).md"] = target_raw
                aligned += 1

# 4. Update all links in vault notes to point to their exact local raw-papers counterpart
print("\nUpdating all literature archive links in vault notes...")
links_updated = 0
for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    rel_vault = os.path.relpath(root, VAULT)
    if rel_vault == ".":
        continue
    depth = len(rel_vault.split(os.sep))
    back_steps = "../" * (depth + 1)
    raw_dir_rel = f"{back_steps}raw-papers/{rel_vault.replace(chr(92), '/')}"
    expected_raw_dir = os.path.join(RAW, rel_vault)
    
    for f in files:
        if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            continue
        v_base = f[:-3]
        v_path = os.path.join(root, f)
        
        pdf_rel = f"{raw_dir_rel}/{v_base}.pdf"
        raw_rel = f"{raw_dir_rel}/{v_base} (Raw).md"
        
        has_pdf = os.path.exists(win_path(os.path.join(expected_raw_dir, f"{v_base}.pdf")))
        has_raw = os.path.exists(win_path(os.path.join(expected_raw_dir, f"{v_base} (Raw).md")))
        
        if has_pdf and has_raw:
            archive_line = f"> **文獻存檔**：[PDF 原文](<{pdf_rel}>) | [Markdown 原文](<{raw_rel}>)"
        elif has_pdf:
            archive_line = f"> **文獻存檔**：[PDF 原文](<{pdf_rel}>)"
        elif has_raw:
            archive_line = f"> **文獻存檔**：[Markdown 原文](<{raw_rel}>)"
        else:
            archive_line = "> **文獻存檔**：*(本篇為重點文獻全文摘錄與分析筆記)*"
            
        with open(win_path(v_path), "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            
        if "> **文獻存檔**" in content or "[PDF 原文]" in content:
            content = re.sub(r'> \*\*文獻存檔\*\*:[^\n\r]+', archive_line, content)
            content = re.sub(r'> \*\*文獻存檔\*\*：[^\n\r]+', archive_line, content)
        else:
            m_h = re.search(r'(# [^\n\r]+\n\n)', content)
            if m_h:
                content = content[:m_h.end()] + f"{archive_line}\n\n" + content[m_h.end():]
                
        with open(win_path(v_path), "w", encoding="utf-8") as fp:
            fp.write(content)
        links_updated += 1

print(f"Final clean alignment complete! Updated {links_updated} notes.")
