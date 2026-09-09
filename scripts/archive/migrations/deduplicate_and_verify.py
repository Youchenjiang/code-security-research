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

# 1. Clean up duplicate stubs in 2A.1
p_2a1_vault = os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)")
p_2a1_raw = os.path.join(RAW, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)")

# Find all notes in other folders
other_notes = {}
for root, dirs, files in os.walk(VAULT):
    if root == p_2a1_vault or any(k in root for k in ["syntheses", "matrices", "templates"]):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("00-") and not re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
            other_notes[f[:-3]] = os.path.join(root, f)

removed_duplicates = 0
for f in os.listdir(p_2a1_vault):
    if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
        continue
        
    stem = f[:-3]
    # Check if this note is a duplicate stub of a note in other_notes
    first_w = re.split(r'[\s\(]+', stem)[0].lower()
    
    dup_match = None
    for on_stem, on_path in other_notes.items():
        if first_w in on_stem.lower() and len(first_w) >= 4:
            # Check if title tokens match
            toks_stem = set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', stem) if len(w) > 2 and not w.isdigit())
            toks_on = set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', on_stem) if len(w) > 2 and not w.isdigit())
            if toks_stem.issubset(toks_on) or len(toks_stem & toks_on) >= 2 or first_w in ['auer', 'heid', 'meli', 'zhao', 'samhi', 'oltrogge', 'mayrhofer', 'shakevsky', 'romdhana', 'katoch', 'suo', 'sutter', 'marandi']:
                dup_match = (on_stem, on_path)
                break
                
    if dup_match:
        # It's a duplicate stub in 2A.1!
        v_file = os.path.join(p_2a1_vault, f)
        os.remove(win_path(v_file))
        
        # Also remove from 2A.1 raw if exists
        r_pdf = os.path.join(p_2a1_raw, f"{stem}.pdf")
        r_raw = os.path.join(p_2a1_raw, f"{stem} (Raw).md")
        if os.path.exists(win_path(r_pdf)):
            os.remove(win_path(r_pdf))
        if os.path.exists(win_path(r_raw)):
            os.remove(win_path(r_raw))
            
        print(f"Removed duplicate stub in 2A.1: {f} (Authentic: {dup_match[0]})")
        removed_duplicates += 1

print(f"Total duplicate stubs removed: {removed_duplicates}")
