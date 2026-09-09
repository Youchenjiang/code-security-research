import os
import sys
import re
import shutil
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
CHABLE_PAPERS = os.path.join(REPO, "chable", "new", "papers")
RAW_PAPERS = os.path.join(REPO, "raw-papers")
VAULT = os.path.join(REPO, "research-vault")

# Directory mappings for the 5 pillars
DEST_MAP = {
    # Pillar 4: Benchmarks
    "4.1": os.path.join("4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)", "4.1-靜態代碼與大模型安全評測 (Static Code & LLM Security Benchmarks)"),
    "4.2": os.path.join("4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)", "4.2-動態攻防與CTF實戰靶場 (Dynamic CTF & Exploit Gym)"),
    "4.3": os.path.join("4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)", "4.3-自主滲透測試與Agent評測 (Autonomous Agent & Pentest Benchmarks)"),
    "4.4": os.path.join("4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)", "4.4-漏洞修復與程序分析基準 (Vulnerability Repair & Analysis Benchmarks)"),
    
    # Pillar 3: APR & CRS
    "3C.3": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "3C.3-網路自主推理系統 (CRS) 與端到端閉環 (Cyber Reasoning Systems - CRS)"),
    "3C.2": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "3C.2-LLM與Agent驅動修復 (LLM & Agentic)"),
    "3A.2": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3A-定位與驗證基礎 (Localization & Validation)", "3A.2-安全補丁驗證與PCA (Validation & PCA)"),
    
    # Pillar 2: Dynamic
    "2A.4": os.path.join("2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.4-自主滲透測試代理與多Agent攻防編排 (Autonomous Pentest & Multi-Agent Orchestration)"),
    "2A.1": os.path.join("2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)"),
    "2B.1": os.path.join("2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)"),
    "2B.2": os.path.join("2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "2B.2-動態污點分析 (Dynamic Taint Analysis - DTA)"),
    "2D.5": os.path.join("2-動態分析 (Dynamic Analysis)", "2D-系統與特定領域測試 (System & Target-Specific)", "2D.5-自動漏洞利用生成 (Automated Exploit Generation - AEG)"),
    "2D.2": os.path.join("2-動態分析 (Dynamic Analysis)", "2D-系統與特定領域測試 (System & Target-Specific)", "2D.2-作業系統內核與虛擬化模糊測試 (Kernel & Hypervisor Fuzzing)"),
    
    # Pillar 1: Static
    "1D.6": os.path.join("1-靜態分析 (Static Analysis)", "1D-領域與智慧型靜態分析 (Domain-Specific & AI)", "1D.6-神經符號與安全規則自動生成 (Neuro-Symbolic & Rule Synthesis)"),
    "1D.1": os.path.join("1-靜態分析 (Static Analysis)", "1D-領域與智慧型靜態分析 (Domain-Specific & AI)", "1D.1-學習型靜態分析 (Learning-based Static)"),
    "1C.1": os.path.join("1-靜態分析 (Static Analysis)", "1C-逆向與相依性安全 (Reverse & Dependency)", "1C.1-二進位與逆向分析 (Binary & Reverse Engineering)"),
    "1B.1": os.path.join("1-靜態分析 (Static Analysis)", "1B-語意與資料流分析 (Semantics & Data Flow)", "1B.1-資料流分析 (Data Flow Analysis)")
}

# Genre link names for Dataview
GENRE_LINKS = {
    "4.1": "[[4.1-靜態代碼與大模型安全評測 (Static Code & LLM Security Benchmarks)]]",
    "4.2": "[[4.2-動態攻防與CTF實戰靶場 (Dynamic CTF & Exploit Gym)]]",
    "4.3": "[[4.3-自主滲透測試與Agent評測 (Autonomous Agent & Pentest Benchmarks)]]",
    "4.4": "[[4.4-漏洞修復與程序分析基準 (Vulnerability Repair & Analysis Benchmarks)]]",
    "3C.3": "[[3C.3-網路自主推理系統 (CRS) 與端到端閉環 (Cyber Reasoning Systems - CRS)]]",
    "3C.2": "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]",
    "3A.2": "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]",
    "2A.4": "[[2A.4-自主滲透測試代理與多Agent攻防編排 (Autonomous Pentest & Multi-Agent Orchestration)]]",
    "2A.1": "[[2A.1-Web與API動態漏洞掃描 (DAST)]]",
    "2B.1": "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]",
    "2B.2": "[[2B.2-動態污點分析 (Dynamic Taint Analysis - DTA)]]",
    "2D.5": "[[2D.5-自動漏洞利用生成 (Automated Exploit Generation - AEG)]]",
    "2D.2": "[[2D.2-作業系統內核與虛擬化模糊測試 (Kernel & Hypervisor Fuzzing)]]",
    "1D.6": "[[1D.6-神經符號與安全規則自動生成 (Neuro-Symbolic & Rule Synthesis)]]",
    "1D.1": "[[1D.1-學習型靜態分析 (Learning-based Static)]]",
    "1C.1": "[[1C.1-二進位與逆向分析 (Binary & Reverse Engineering)]]",
    "1B.1": "[[1B.1-資料流分析 (Data Flow Analysis)]]"
}

def classify_paper(filename, role, stages, title, contribution):
    text = f"{filename} {title} {contribution}".lower()
    
    # AIxCC & CRS
    if any(k in text for k in ["aixcc", "atlantis", "fuzzingbrain", "crs", "cyber reasoning system"]):
        return "3C.3"
        
    # Benchmarks
    if role == "B" or "bench" in text or "gym" in text:
        if any(k in text for k in ["cybench", "cybergym", "exploitgym", "exploitbench", "pacebench", "zerodaybench"]):
            return "4.2"
        if any(k in text for k in ["autopenbench", "mobilesafetybench", "agentscan", "androidarena"]):
            return "4.3"
        if any(k in text for k in ["cvebench", "vulr2", "morefixes", "swe-bench"]):
            return "4.4"
        return "4.1" # CWEval, SecurityEval, CodeSecEval, SecMutBench, CyberSecEval
        
    # Autonomous Pentest Agents & Orchestration
    if role == "O" or any(k in text for k in ["pentestgpt", "hptsa", "vulnbot", "aptagent", "xoffense", "autopentest", "rapipen", "agentflow", "autopengpt", "titanca", "cai", "pentestagent", "checkmate", "hacksynth", "curriculumpt"]):
        return "2A.4"
        
    # Exploit & PoC Generation
    if any(k in text for k in ["pocgen", "pagent", "faultline", "antiproof", "exploit generation"]):
        return "2D.5"
        
    # Patching & Repair
    if any(k in text for k in ["appatch", "repair", "patching"]):
        return "3C.2"
        
    # Neuro-Symbolic & Rule Synthesis
    if any(k in text for k in ["ruledroid", "rulepilot", "knighter", "llmxcpg", "qlpro", "persistentfeedback", "semgrep rule"]):
        return "1D.6"
        
    # Surveys
    if role == "S":
        if "pentest" in text or "agent" in text:
            return "2A.4"
        return "4.1"
        
    # Mobile GUI & Fuzzing
    if any(k in text for k in ["droidbot", "stoat", "sapienz", "bugscribe", "scengen", "gptdroid", "gui agent"]):
        return "2B.1"
        
    if "taint" in text:
        return "2B.2"
        
    if "kernel" in text or "fans" in text:
        return "2D.2"
        
    if "obfuscation" in text or "reverse" in text:
        return "1C.1"
        
    return "2A.1"

# Read metadata table
meta_path = os.path.join(CHABLE_PAPERS, "PAPERS_METADATA_TABLE.md")
with open(meta_path, "r", encoding="utf-8") as fp:
    lines = fp.readlines()

meta_dict = {}
for l in lines:
    if l.startswith("|") and not l.startswith("| #") and not l.startswith("|---"):
        parts = [p.strip() for p in l.split("|")[1:-1]]
        if len(parts) >= 10:
            pdf_key = parts[1].replace(".pdf", "").lower()
            meta_dict[pdf_key] = {
                "num": parts[0],
                "file_raw": parts[1],
                "primary": parts[2],
                "stages": parts[3],
                "role": parts[4],
                "android": parts[5],
                "llm": parts[6],
                "year": parts[7] if parts[7] else "2025",
                "venue": parts[8] if parts[8] else "Security",
                "contribution": parts[9]
            }

disk_files = os.listdir(CHABLE_PAPERS)
disk_pdfs = [f for f in disk_files if f.endswith(".pdf")]

ingested_count = 0
for pdf in disk_pdfs:
    base = pdf[:-4]
    md_name = base + ".md"
    pdf_path = os.path.join(CHABLE_PAPERS, pdf)
    md_path = os.path.join(CHABLE_PAPERS, md_name)
    
    # Try finding metadata
    meta = None
    for k, v in meta_dict.items():
        if k in pdf.lower() or base.lower() in k or pdf.lower().split("_")[-1] in k:
            meta = v
            break
            
    role = meta["role"] if meta else "M"
    stages = meta["stages"] if meta else "V"
    year = meta["year"] if meta and meta["year"] else "2025"
    venue = meta["venue"] if meta and meta["venue"] else "Preprint"
    contrib = meta["contribution"] if meta else ""
    
    # Clean clean name
    clean_title = re.sub(r"^[A-Z0-9]+_[A-Z0-9]+_", "", base)
    clean_title = re.sub(r"^[A-Z0-9]+_", "", clean_title)
    std_name = f"{clean_title}_({year})"
    
    genre_key = classify_paper(base, role, stages, clean_title, contrib)
    sub_folder = DEST_MAP[genre_key]
    genre_link = GENRE_LINKS[genre_key]
    
    # Raw paths
    raw_dest_dir = os.path.join(RAW_PAPERS, sub_folder)
    os.makedirs(raw_dest_dir, exist_ok=True)
    raw_dest_pdf = os.path.join(raw_dest_dir, f"{std_name}.pdf")
    raw_dest_md = os.path.join(raw_dest_dir, f"{std_name}_raw.md")
    
    # Vault paths
    vault_dest_dir = os.path.join(VAULT, sub_folder)
    os.makedirs(vault_dest_dir, exist_ok=True)
    vault_dest_md = os.path.join(vault_dest_dir, f"{std_name}.md")
    
    # Copy PDF & Raw MD to raw-papers
    if not os.path.exists(raw_dest_pdf):
        shutil.copy2(pdf_path, raw_dest_pdf)
    if os.path.exists(md_path) and not os.path.exists(raw_dest_md):
        shutil.copy2(md_path, raw_dest_md)
        
    # Create Curated note in vault
    raw_content = ""
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
            raw_content = fp.read()[:3000]
            
    vault_note_content = f"""---
title: "{clean_title.replace('_', ' ')}"
year: {year}
venue: "{venue}"
categories:
  - "{genre_link}"
secverify_role: "{role}"
secverify_stages: "{stages}"
---

# {clean_title.replace('_', ' ')} ({year})

> **發表會/期刊**：{venue} ({year})  
> **研究流派**：{genre_link}  
> **Pipeline 角色**：Role `{role}` | Stages `{stages}`  
> **核心貢獻**：{contrib}  
> **文獻存檔**：[PDF 原文](../../../raw-papers/{sub_folder.replace(chr(92), '/')}/{std_name}.pdf)

---

## 📌 論文核心精要 (Executive Summary)
{contrib if contrib else "本論文提出針對現代軟體系統與大模型環境之創新安全測試或修復方法。"}

---

## 🔍 方法論與技術亮點 (Methodology Highlights)
- **主要階段**：`{stages}`
- **模型與架構**：本研究探討以 LLM / Agent 驅動之安全攻防技術。

---
返回 [[00-研究流派圖主目錄|研究流派圖主目錄]]
"""
    if not os.path.exists(vault_dest_md):
        with open(vault_dest_md, "w", encoding="utf-8") as fp:
            fp.write(vault_note_content)
            
    ingested_count += 1

print(f"Successfully processed and ingested {ingested_count} papers from chable/new/papers!")

# Copy indexes into syntheses
for f in ["TAXONOMY.md", "PAPERS_METADATA_TABLE.md", "ALL_PAPERS_APP_SETUP_GUIDE.md"]:
    src = os.path.join(CHABLE_PAPERS, f)
    if os.path.exists(src):
        dst = os.path.join(VAULT, "syntheses", f)
        shutil.copy2(src, dst)
        print(f"Copied {f} to research-vault/syntheses/")

print("\nIngestion and index sync completed successfully!")
