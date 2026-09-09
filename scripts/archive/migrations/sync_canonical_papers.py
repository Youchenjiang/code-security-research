import os
import sys
import re
import json

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

with open(os.path.join(RAW, "legacy_archive", "spaces_rename_log.json"), "r", encoding="utf-8") as fp:
    rename_log = json.load(fp)

raw_renames = rename_log.get("raw_renames", {})

# Specific manual overrides for corrupted/truncated names
MANUAL_OVERRIDES = {
    "(2018) How Android UI Security Undermined.md": {
        "title": "How Android's UI Security is Undermined by Accessibility APIs",
        "author": "Meli (2018)",
        "canonical": "Meli (2018) How Android UI Security Undermined by Accessibility",
        "raw_pdf_hint": "Meli"
    },
    "(2020) 1 En Print indd.md": {
        "title": "DaVinci: Beyond Frida via Syscall Interception",
        "author": "Druffel & Heid (2020)",
        "canonical": "Druffel & Heid (2020) DaVinci Beyond Frida via Syscall",
        "raw_pdf_hint": "Heid"
    },
    "Tam (2013) 4 1.md": {
        "title": "CopperDroid: Automatic Reconstruction of Android Malware Behaviors",
        "author": "Tam (2015)",
        "canonical": "Tam (2015) CopperDroid Automatic Reconstruction of Android Malware",
        "raw_pdf_hint": "Tam CopperDroid"
    },
    "Liu (2020) sec20-liu.md": {
        "title": "FANS: Fuzzing Android Native System Services via Multi-level Semantic Extraction",
        "author": "Liu (2020)",
        "canonical": "Liu (2020) FANS Fuzzing Android Native System Services",
        "raw_pdf_hint": "Liu FANS"
    },
    "Editor (2013) Peer reviewed Journal.md": {
        "title": "Framework for Enhancing Security Testing of Android Applications",
        "author": "Lamina (2013)",
        "canonical": "Lamina (2013) Framework for Enhancing Security Testing",
        "raw_pdf_hint": "Lamina"
    },
    "DevSecOps (2024) Identifying the primary dimensions of.md": {
        "title": "Identifying the Primary Dimensions of DevSecOps: A Multi-vocal Literature Review",
        "author": "Zhao (2024)",
        "canonical": "Zhao (2024) Identifying Primary Dimensions of DevSecOps",
        "raw_pdf_hint": "Zhao"
    },
    "CAR (2021) Driving Execution of Target Paths.md": {
        "title": "Driving Execution of Target Paths in Android Applications with (a) CAR",
        "author": "Wong (2022)",
        "canonical": "Wong (2022) Driving Execution of Target Paths with CAR",
        "raw_pdf_hint": "Wong CAR"
    },
    "Gervais (2017) Revive Rebalancing Off-Blockchain Payment Networks.md": {
        "title": "A Stitch in Time: Supporting Android Developers in Writing Secure Code",
        "author": "Nguyen (2017)",
        "canonical": "Nguyen (2017) Stitch in Time Supporting Secure Code",
        "raw_pdf_hint": "Nguyen"
    }
}

# Scan raw files
all_raw_files = [] # list of (full_path, dir_path, filename)
for root, dirs, files in os.walk(RAW):
    if "legacy_archive" in root:
        continue
    for f in files:
        all_raw_files.append((os.path.join(root, f), root, f))

def clean_toks(s):
    return set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', s) if len(w) > 2 and not w.isdigit())

# Process all vault notes
renamed_count = 0
links_updated = 0

for root, dirs, files in os.walk(VAULT):
    if any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    rel_vault_dir = os.path.relpath(root, VAULT)
    if rel_vault_dir == ".":
        continue
    expected_raw_dir = os.path.join(RAW, rel_vault_dir)
    os.makedirs(expected_raw_dir, exist_ok=True)
    
    for f in files:
        if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            continue
            
        v_path = os.path.join(root, f)
        v_base = f[:-3]
        
        with open(v_path, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            
        canonical_name = v_base
        if f in MANUAL_OVERRIDES:
            canonical_name = MANUAL_OVERRIDES[f]["canonical"]
            
        # Clean canonical_name if it has ugly prefixes
        canonical_name = re.sub(r'^\d+_', '', canonical_name)
        canonical_name = re.sub(r'^[A-Z0-9]+_[A-Z0-9]+_', '', canonical_name)
        
        # Find matching PDF and RAW MD in raw-papers
        matched_pdf = None
        matched_raw_md = None
        
        # 1. Check override hint
        if f in MANUAL_OVERRIDES:
            hint = MANUAL_OVERRIDES[f]["raw_pdf_hint"].lower()
            for full_p, d_path, r_name in all_raw_files:
                if r_name.endswith(".pdf") and hint in r_name.lower():
                    matched_pdf = full_p
                    break
                    
        # 2. Check source:
        if not matched_pdf:
            m_src = re.search(r"source:\s*[\"']?([^\"'\r\n]+)[\"']?", content)
            if m_src:
                src_val = m_src.group(1).strip()
                target_cand = raw_renames.get(src_val, src_val)
                for full_p, d_path, r_name in all_raw_files:
                    if r_name.endswith(".pdf") and (r_name == target_cand or clean_toks(r_name) == clean_toks(target_cand)):
                        matched_pdf = full_p
                        break
                        
        # 3. Check existing link
        if not matched_pdf:
            m_link = re.search(r"\[PDF 原文\]\(<([^>]+)>\)", content)
            if m_link:
                cand_p = os.path.normpath(os.path.join(root, m_link.group(1)))
                if os.path.exists(cand_p):
                    matched_pdf = cand_p
                    
        # 4. Check name tokens
        if not matched_pdf:
            v_toks = clean_toks(v_base)
            best_score = 0
            best_p = None
            for full_p, d_path, r_name in all_raw_files:
                if r_name.endswith(".pdf"):
                    r_toks = clean_toks(r_name)
                    overlap = len(v_toks & r_toks)
                    if overlap > best_score and overlap >= 2:
                        best_score = overlap
                        best_p = full_p
            if best_p:
                matched_pdf = best_p
                
        # 5. Check first author word
        if not matched_pdf:
            first_word = re.split(r'[\s\(]+', v_base)[0].lower()
            if len(first_word) >= 4:
                for full_p, d_path, r_name in all_raw_files:
                    if r_name.endswith(".pdf") and first_word in r_name.lower():
                        matched_pdf = full_p
                        break

        # If matched PDF, find its raw MD
        if matched_pdf:
            pdf_dir = os.path.dirname(matched_pdf)
            pdf_stem = os.path.basename(matched_pdf)[:-4]
            for full_p, d_path, r_name in all_raw_files:
                if d_path == pdf_dir and r_name.endswith(".md"):
                    r_stem = r_name[:-3]
                    if r_stem == pdf_stem or r_stem == f"{pdf_stem} raw" or r_stem == f"{pdf_stem} (Raw)" or clean_toks(r_stem) == clean_toks(pdf_stem):
                        matched_raw_md = full_p
                        break

        # RENAME PDF & RAW MD to canonical name in expected_raw_dir
        dest_pdf = os.path.join(expected_raw_dir, f"{canonical_name}.pdf")
        dest_raw_md = os.path.join(expected_raw_dir, f"{canonical_name} (Raw).md")
        
        if matched_pdf and os.path.exists(win_path(matched_pdf)):
            if os.path.normpath(matched_pdf) != os.path.normpath(dest_pdf):
                if os.path.exists(win_path(dest_pdf)):
                    os.remove(win_path(dest_pdf))
                os.rename(win_path(matched_pdf), win_path(dest_pdf))
                renamed_count += 1
                
        if matched_raw_md and os.path.exists(win_path(matched_raw_md)):
            if os.path.normpath(matched_raw_md) != os.path.normpath(dest_raw_md):
                if os.path.exists(win_path(dest_raw_md)):
                    os.remove(win_path(dest_raw_md))
                os.rename(win_path(matched_raw_md), win_path(dest_raw_md))
                renamed_count += 1

        # RENAME VAULT NOTE if canonical changed
        dest_vault_note = os.path.join(root, f"{canonical_name}.md")
        if os.path.normpath(v_path) != os.path.normpath(dest_vault_note):
            if os.path.exists(win_path(dest_vault_note)):
                os.remove(win_path(v_path))
            else:
                os.rename(win_path(v_path), win_path(dest_vault_note))
            v_path = dest_vault_note

        # UPDATE VAULT NOTE CONTENT
        depth = len(rel_vault_dir.split(os.sep))
        back_steps = "../" * (depth + 1)
        rel_pdf_path = f"{back_steps}raw-papers/{rel_vault_dir.replace(chr(92), '/')}/{canonical_name}.pdf"
        rel_raw_path = f"{back_steps}raw-papers/{rel_vault_dir.replace(chr(92), '/')}/{canonical_name} (Raw).md"
        
        has_dest_raw = os.path.exists(win_path(dest_raw_md))
        if has_dest_raw:
            archive_line = f"> **文獻存檔**：[PDF 原文](<{rel_pdf_path}>) | [Markdown 原文](<{rel_raw_path}>)"
        else:
            archive_line = f"> **文獻存檔**：[PDF 原文](<{rel_pdf_path}>)"
            
        with open(win_path(v_path), "r", encoding="utf-8", errors="ignore") as fp:
            n_content = fp.read()
            
        # Clean title header
        n_content = re.sub(r'# \d+_[^\n\r]+', f'# {canonical_name}', n_content)
        n_content = re.sub(r'# [0-9A-Za-z]+_[^\n\r]+', f'# {canonical_name}', n_content)
        
        # Replace or add archive line
        if "> **文獻存檔**" in n_content or "[PDF 原文]" in n_content:
            n_content = re.sub(r'> \*\*文獻存檔\*\*:[^\n\r]+', archive_line, n_content)
            n_content = re.sub(r'> \*\*文獻存檔\*\*：[^\n\r]+', archive_line, n_content)
        else:
            # Insert after the first blockquote block or after # Header
            m_h = re.search(r'(# [^\n\r]+\n\n)', n_content)
            if m_h:
                n_content = n_content[:m_h.end()] + f"{archive_line}\n\n" + n_content[m_h.end():]
                
        # Update source in frontmatter
        n_content = re.sub(r'source:\s*["\'][^"\'\r\n]+["\']', f'source: "{canonical_name}.pdf"', n_content)
        
        with open(win_path(v_path), "w", encoding="utf-8") as fp:
            fp.write(n_content)
        links_updated += 1

print(f"Alignment complete! Renamed {renamed_count} files and updated {links_updated} vault notes!")
