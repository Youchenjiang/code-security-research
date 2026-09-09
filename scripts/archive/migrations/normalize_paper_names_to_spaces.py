import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")
LEGACY = os.path.join(RAW, "legacy_archive")

os.makedirs(LEGACY, exist_ok=True)

def extract_year_from_content(md_path):
    if not os.path.exists(md_path):
        return None
    try:
        with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
            for _ in range(25):
                line = fp.readline()
                if not line:
                    break
                m = re.search(r"^year:\s*(\d{4})", line.strip())
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None

def clean_paper_title(name, year_hint=None):
    base, ext = os.path.splitext(name)
    is_raw = base.endswith('_raw') or base.endswith(' raw')
    if is_raw:
        base = re.sub(r'(_raw| raw)$', '', base)
        
    # Strip leading serial numbers: e.g. 01_, 81_, A01_, B12_
    base = re.sub(r'^(\d+|[A-Z]\d+)_\s*', '', base)
    
    # Strip stage/role prefixes like O_M_, A_M_, B_, E_M_, V_M_, S_S\d+_
    base = re.sub(r'^[A-Z]_[A-Z0-9]+_\s*', '', base)
    base = re.sub(r'^[A-Z]_\s*', '', base)
    
    # Remove et_al., et al.
    base = re.sub(r'et_al\.,?', '', base, flags=re.IGNORECASE)
    base = re.sub(r'et\s+al\.,?', '', base, flags=re.IGNORECASE)
    
    # Fix double year artifact: Title_2026_(2025) -> Title (2026)
    m = re.search(r'(\d{4})_\((\d{4})\)', base)
    if m:
        base = base.replace(m.group(0), f'({m.group(1)})')
        
    # Fix Year in Barr2015_Title -> Barr (2015) Title
    base = re.sub(r'([A-Za-z]+)(\d{4})_', r'\1 (\2) ', base)
    
    # Standardize _(Year)_ to (Year)
    base = re.sub(r'_\((\d{4})\)_', r' (\1) ', base)
    base = re.sub(r'_\((\d{4})\)', r' (\1)', base)
    
    # Replace remaining underscores with single space
    base = base.replace('_', ' ')
    
    # Format trailing year: e.g. PentestGPT 2024 -> PentestGPT (2024)
    base = re.sub(r'\s+(\d{4})$', r' (\1)', base)
    
    # If no year in parentheses and year_hint available, insert year after first word
    if not re.search(r'\(\d{4}\)', base) and year_hint:
        parts = base.split(' ', 1)
        if len(parts) == 2:
            base = f"{parts[0]} ({year_hint}) {parts[1]}"
        else:
            base = f"{base} ({year_hint})"
            
    # Clean multiple spaces and trailing commas
    base = re.sub(r'[,\s]+', ' ', base).strip()
    
    if is_raw:
        return f'{base} raw{ext}'
    return f'{base}{ext}'

# 1. Rename files in research-vault
vault_renames = {}
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        # Skip genre notes, indexes, templates, matrices, syntheses
        if f.startswith('00-') or re.match(r'^[0-9A-Z]+\.[0-9A-Za-z]+-', f) or 'Template' in f or 'matrices' in root or 'syntheses' in root or 'legacy' in root:
            continue
            
        old_path = os.path.join(root, f)
        year_hint = extract_year_from_content(old_path)
        new_filename = clean_paper_title(f, year_hint)
        
        if new_filename != f:
            new_path = os.path.join(root, new_filename)
            vault_renames[old_path] = (new_path, f, new_filename)

print(f"Renaming {len(vault_renames)} paper notes in research-vault...")
for old_path, (new_path, old_name, new_name) in vault_renames.items():
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)

# 2. Rename files in raw-papers
raw_renames = {}
for root, dirs, files in os.walk(RAW):
    if 'legacy_archive' in root:
        continue
    for f in files:
        if not (f.endswith('.pdf') or f.endswith('.md')):
            continue
        old_path = os.path.join(root, f)
        new_filename = clean_paper_title(f)
        if new_filename != f:
            new_path = os.path.join(root, new_filename)
            raw_renames[old_path] = (new_path, f, new_filename)

print(f"Renaming {len(raw_renames)} files in raw-papers...")
for old_path, (new_path, old_name, new_name) in raw_renames.items():
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)

# 3. Update links inside research-vault notes to point to new PDF names
print("Updating PDF link references in vault notes...")
updated_links_count = 0
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        md_path = os.path.join(root, f)
        try:
            with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
                
            # Find and replace PDF links
            def replace_pdf_link(match):
                prefix = match.group(1)
                pdf_target = match.group(2)
                # clean target name
                dir_part, file_part = os.path.split(pdf_target)
                clean_file_part = clean_paper_title(file_part)
                new_target = os.path.join(dir_part, clean_file_part).replace('\\', '/')
                return f"{prefix}{new_target})"
                
            new_content = re.sub(r'(\[PDF 原文\]\()([^)]+)(\))', replace_pdf_link, content)
            if new_content != content:
                with open(md_path, "w", encoding="utf-8") as fp:
                    fp.write(new_content)
                updated_links_count += 1
        except Exception:
            pass

print(f"Updated PDF links in {updated_links_count} notes!")

# Save log
log_data = {
    "vault_renames": {v[1]: v[2] for v in vault_renames.values()},
    "raw_renames": {v[1]: v[2] for v in raw_renames.values()}
}
log_path = os.path.join(LEGACY, "spaces_rename_log.json")
with open(log_path, "w", encoding="utf-8") as fp:
    json.dump(log_data, fp, ensure_ascii=False, indent=2)

print("Normalization to natural spaces completed successfully!")
