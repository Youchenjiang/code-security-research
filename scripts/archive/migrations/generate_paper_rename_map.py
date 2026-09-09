import os
import glob
import re

paths = [
    ('Category_A', r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification'),
    ('Category_B', r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_B_sast_blindspot_exploration'),
    ('Legacy', r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\legacy_archive\papers')
]

papers = []

def clean_str(s):
    if not s: return ""
    s = s.replace('"', '').replace("'", "").strip()
    return s

def extract_heading1(content):
    # Match first # Heading
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('# **總頁數') and not line.startswith('# Page'):
            h = line[2:].strip()
            # remove leading numbers like "01 " or "31_Li_et_al.,_"
            h = re.sub(r'^\d+[\s_]+', '', h)
            h = re.sub(r'^[A-Za-z0-9_&.,]+_et_al[.,_]*', '', h)
            return h.strip(' _-')
    return ""

def extract_year(text, filename):
    m = re.search(r'\b(19\d\d|20[0-2]\d)\b', filename)
    if m: return m.group(1)
    m = re.search(r'\b(20[0-2]\d)\b', text[:3000])
    if m: return m.group(1)
    return "2024"

# Prominent tools and topics
KNOWN_TOOLS = [
    "IntelliDroid", "CAR", "A2", "Sapienz", "DroidBot", "Stoat", "EHBDroid",
    "Humanoid", "GPTDroid", "ScenGen", "GPT-Monkey", "ViaLin", "KeyDroid",
    "FANS", "DaVinci", "TIRO", "Chizpurfle", "InputBlaster", "TSDroid",
    "DroidScope", "CopperDroid", "Dynodroid", "TaintDroid", "CamDroid",
    "Wasserstein_GAN", "SSLTLS", "PendingIntent", "Clipboard", "Obfuscation",
    "DevSecOps", "CICD", "TrustZone", "BLE", "GATT", "NASS", "MALintent", "TEEzz"
]

def guess_tool_or_topic(filename, heading, source):
    combined = f"{filename} {heading} {source}"
    for t in KNOWN_TOOLS:
        if re.search(r'\b' + re.escape(t) + r'\b', combined, re.IGNORECASE):
            return t
    return None

for cat, p in paths:
    if not os.path.exists(p): continue
    for f in sorted(glob.glob(os.path.join(p, '*.md'))):
        fname = os.path.basename(f)
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read(6000)
        
        h1 = extract_heading1(content)
        
        source_m = re.search(r'source:\s*\"?([^\r\n\"]+)', content)
        source = clean_str(source_m.group(1)) if source_m else ""
        
        author_m = re.search(r'author:\s*\"?([^\r\n\"]+)', content)
        author = clean_str(author_m.group(1)) if author_m else ""
        
        first_author = ""
        if author:
            parts = author.split(',')[0].strip().split()
            if parts: first_author = parts[-1]
        if not first_author:
            m = re.search(r'\d+_([A-Za-z\-]+)', fname)
            if m: first_author = m.group(1)
        
        year = extract_year(content, source or fname)
        tool = guess_tool_or_topic(fname, h1, source)
        
        # Primary tag: Tool if exists, else Topic or Author
        primary_tag = tool if tool else first_author
        
        # Clean title for filename (shorten to ~6 words)
        short_title = h1 if h1 else fname.replace('.md', '')
        short_title = re.sub(r'[:/?*\"<>|\\.,_]+', ' ', short_title).strip()
        short_words = short_title.split()[:6]
        short_title_clean = "_".join(short_words)
        
        if primary_tag and not short_title_clean.lower().startswith(primary_tag.lower()):
            new_name = f"{primary_tag}_({year})_{short_title_clean}.md"
        else:
            new_name = f"{short_title_clean}_({year}).md" if not primary_tag else f"{primary_tag}_({year}).md"
            if len(short_words) > 1:
                new_name = f"{primary_tag}_({year})_{'_'.join(short_words[:5])}.md"
        
        papers.append({
            'cat': cat,
            'old': fname,
            'new': new_name,
            'tool': tool or '',
            'author': first_author,
            'year': year,
            'heading': h1[:60]
        })

out_md = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\paper_rename_table.md"
with open(out_md, 'w', encoding='utf-8') as fp:
    fp.write("# 論文命名正規化對照表 (Paper Renaming Proposal)\n\n")
    fp.write("| 類別 | 現有混亂檔名 | 建議規範檔名 (工具/主題導向) | 識別代表標籤 | 年份 |\n")
    fp.write("| :---: | :--- | :--- | :--- | :--- |\n")
    for p in papers:
        fp.write(f"| {p['cat']} | `{p['old']}` | **`{p['new']}`** | {p['tool'] or p['author']} | {p['year']} |\n")

print(f"Generated proposal table for {len(papers)} papers at {out_md}")
