import os
import sys
import re
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")
SYN = os.path.join(VAULT, "syntheses")

def win_path(p):
    ap = os.path.abspath(p)
    if not ap.startswith("\\\\?\\"):
        return "\\\\?\\" + ap
    return ap

# 1. Move 3 root review files into syntheses
for f in ["genre relations review.md", "SecVerify 研究流派對照指南.md", "SecVerify 第二年重新設計三大動態驗證方案評估.md"]:
    src = os.path.join(VAULT, f)
    dst = os.path.join(SYN, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved to syntheses: {f}")

# 2. Fix the 5 generic 2024/2025/2026 files to concise, clean names
FIX_PAPERS = [
    {
        "dir_rel": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "3C.3-網路自主推理系統 (CRS) 與端到端閉環 (Cyber Reasoning Systems - CRS)"),
        "proper_name": "ATLANTIS (2025) AIxCC Winner",
        "title": "ATLANTIS: AI-driven Threat Localization, Analysis, and Triage Intelligence System",
        "venue": "arXiv (Team Atlanta - AIxCC Winner)",
        "year": "2025",
        "role": "O",
        "stages": "V, E, X",
        "contrib": "🏆 AIxCC 冠軍 — 完整的 CRS 自主網路推理系統架構設計"
    },
    {
        "dir_rel": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "3C.2-LLM與Agent驅動修復 (LLM & Agentic)"),
        "proper_name": "APPATCH (2025) Automated Adaptive Prompting",
        "title": "APPATCH: Automated Adaptive Prompting Large Language Models for Software Vulnerability Patching",
        "venue": "USENIX Security 2025",
        "year": "2025",
        "role": "M",
        "stages": "V, E",
        "contrib": "Automated adaptive prompting for LLM vulnerability patching"
    },
    {
        "dir_rel": os.path.join("2-動態分析 (Dynamic Analysis)", "2D-系統與特定領域測試 (System & Target-Specific)", "2D.5-自動漏洞利用生成 (Automated Exploit Generation - AEG)"),
        "proper_name": "PAGENT (2026) Program Analysis Guided Agent",
        "title": "PAGENT: Program Analysis Guided LLM Agent for Proof-of-Concept Generation",
        "venue": "ISSTA 2026",
        "year": "2026",
        "role": "M",
        "stages": "V, E",
        "contrib": "Program analysis 引導 LLM agent 生成 PoC exploit"
    },
    {
        "dir_rel": os.path.join("2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.4-自主滲透測試代理與多Agent攻防編排 (Autonomous Pentest & Multi-Agent Orchestration)"),
        "proper_name": "HPTSA (2024) LLM Agents Zero-Day Exploit",
        "title": "HPTSA: Teams of LLM Agents can Exploit Zero-Day Vulnerabilities",
        "venue": "arXiv (UIUC)",
        "year": "2024",
        "role": "O",
        "stages": "A, V, E, X",
        "contrib": "UIUC 團隊 Multi-agent 系統利用 zero-day 漏洞（53% 成功率）"
    },
    {
        "dir_rel": os.path.join("2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)"),
        "proper_name": "LATTE (2023) LLM Binary Taint Analysis",
        "title": "LATTE: Harnessing the Power of LLM to Support Binary Taint Analysis",
        "venue": "ACM TOSEM / ASE 2025",
        "year": "2023",
        "role": "M",
        "stages": "V",
        "contrib": "First LLM-powered static binary taint analysis framework"
    }
]

for pinfo in FIX_PAPERS:
    raw_dir = os.path.join(RAW, pinfo["dir_rel"])
    vault_dir = os.path.join(VAULT, pinfo["dir_rel"])
    
    # Identify old files in raw_dir
    if os.path.exists(win_path(raw_dir)):
        for f in os.listdir(win_path(raw_dir)):
            if f in ["(2025).pdf", "2025_(2025).pdf", "2026_(2025).pdf", "2024_(2025).pdf", "2023_(2025).pdf"]:
                old_pdf = win_path(os.path.join(raw_dir, f))
                new_pdf = win_path(os.path.join(raw_dir, f"{pinfo['proper_name']}.pdf"))
                if os.path.exists(old_pdf):
                    if os.path.exists(new_pdf):
                        os.remove(new_pdf)
                    os.rename(old_pdf, new_pdf)
                    print(f"Renamed PDF: {f} -> {pinfo['proper_name']}.pdf")
                
            if f in ["(2025) raw.md", "2025_(2025) raw.md", "2026_(2025) raw.md", "2024_(2025) raw.md", "2023_(2025) raw.md"]:
                old_raw = win_path(os.path.join(raw_dir, f))
                new_raw = win_path(os.path.join(raw_dir, f"{pinfo['proper_name']} raw.md"))
                if os.path.exists(old_raw):
                    if os.path.exists(new_raw):
                        os.remove(new_raw)
                    os.rename(old_raw, new_raw)
                    print(f"Renamed RAW MD: {f} -> {pinfo['proper_name']} raw.md")
                
    # Identify old notes in vault_dir
    if os.path.exists(win_path(vault_dir)):
        for f in os.listdir(win_path(vault_dir)):
            if f in ["(2025).md", "2025_(2025).md", "2026_(2025).md", "2024_(2025).md", "2023_(2025).md"]:
                old_note = win_path(os.path.join(vault_dir, f))
                new_note = win_path(os.path.join(vault_dir, f"{pinfo['proper_name']}.md"))
                if os.path.exists(old_note):
                    if os.path.exists(new_note):
                        os.remove(old_note)
                    else:
                        os.rename(old_note, new_note)
                    print(f"Renamed Vault Note: {f} -> {pinfo['proper_name']}.md")

# 3. Comprehensive Fix for PDF Links using Angle Brackets <...>
print("\nRebuilding all PDF links with angle brackets <...>...")
pdf_links_fixed = 0

for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        md_path = os.path.join(root, f)
        
        # Calculate matching PDF in raw-papers
        rel_to_vault = os.path.relpath(root, VAULT)
        if rel_to_vault == '.':
            continue
            
        raw_counterpart_dir = os.path.join(RAW, rel_to_vault)
        base_name = f[:-3] # without .md
        
        # Look for PDF matching base_name in raw_counterpart_dir
        matching_pdf = None
        if os.path.exists(raw_counterpart_dir):
            for raw_f in os.listdir(raw_counterpart_dir):
                if raw_f.endswith('.pdf'):
                    raw_base = raw_f[:-4]
                    if raw_base.lower() == base_name.lower():
                        matching_pdf = raw_f
                        break
                    # Try partial match if one has year and other doesn't
                    clean_rb = re.sub(r'\s*\(\d{4}\)', '', raw_base).strip().lower()
                    clean_bn = re.sub(r'\s*\(\d{4}\)', '', base_name).strip().lower()
                    if clean_rb == clean_bn or (len(clean_rb) > 5 and clean_rb in clean_bn) or (len(clean_bn) > 5 and clean_bn in clean_rb):
                        matching_pdf = raw_f
                        break
                        
        if matching_pdf:
            depth = len(rel_to_vault.split(os.sep))
            back_steps = "../" * (depth + 1)
            raw_rel_path = f"{back_steps}raw-papers/{rel_to_vault.replace(chr(92), '/')}/{matching_pdf}"
            new_link_line = f"> **文獻存檔**：[PDF 原文](<{raw_rel_path}>)"
            
            with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
                
            # Replace lines with 文獻存檔
            lines = content.splitlines()
            new_lines = []
            changed = False
            for line in lines:
                if "文獻存檔" in line or "[PDF 原文]" in line:
                    new_lines.append(new_link_line)
                    changed = True
                else:
                    new_lines.append(line)
                    
            if changed:
                with open(md_path, "w", encoding="utf-8") as fp:
                    fp.write("\n".join(new_lines) + "\n")
                pdf_links_fixed += 1

print(f"Fixed PDF links in {pdf_links_fixed} vault notes!")
print("Health check fixes completed successfully!")
