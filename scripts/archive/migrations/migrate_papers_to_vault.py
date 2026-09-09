import os
import glob
import re
import shutil
import sys

# Force utf-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VAULT_PAPERS_DIR = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\research-vault\papers"
DEST_CAT_A = os.path.join(VAULT_PAPERS_DIR, "01_SAST導引驗證_Category_A")
DEST_CAT_B = os.path.join(VAULT_PAPERS_DIR, "02_SAST盲區突破_Category_B")
DEST_LEGACY = os.path.join(VAULT_PAPERS_DIR, "00_歷史經典論文_Legacy")
DEST_ORACLE = os.path.join(VAULT_PAPERS_DIR, "03_測試預言與斷言合成_Oracle")

for d in [DEST_CAT_A, DEST_CAT_B, DEST_LEGACY, DEST_ORACLE]:
    os.makedirs(d, exist_ok=True)

# Step 1: Move existing loose oracle markdown files in VAULT_PAPERS_DIR to DEST_ORACLE
loose_files = [f for f in os.listdir(VAULT_PAPERS_DIR) if os.path.isfile(os.path.join(VAULT_PAPERS_DIR, f)) and f.endswith(".md")]
print(f"Moving {len(loose_files)} existing Oracle papers to {DEST_ORACLE}...")
for f in loose_files:
    shutil.move(os.path.join(VAULT_PAPERS_DIR, f), os.path.join(DEST_ORACLE, f))

# Step 2: Mapping dictionary for clean naming and genre assignment
KNOWN_TOOLS = {
    "IntelliDroid": ("IntelliDroid", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[1B.4-靜態污點分析 (Static Taint Analysis)]]"),
    "CAR": ("CAR", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[1B.1-資料流分析 (Data Flow Analysis)]]"),
    "A2": ("A2_Agent", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"),
    "Sapienz": ("Sapienz", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "DroidBot": ("DroidBot", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]"),
    "Stoat": ("Stoat", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "EHBDroid": ("EHBDroid", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "Humanoid": ("Humanoid", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3C.1-深度學習修復流派 (DL & NMT)]]"),
    "GPTDroid": ("GPTDroid", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"),
    "ScenGen": ("ScenGen", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"),
    "GPT-Monkey": ("GPT-Monkey", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"),
    "ViaLin": ("ViaLin", "[[2B.2-動態污點分析 (Dynamic Taint Analysis - DTA)]]", "[[1B.4-靜態污點分析 (Static Taint Analysis)]]"),
    "KeyDroid": ("KeyDroid", "[[1D.2-密碼學與協議安全審計 (Cryptographic & Protocol Security)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "FANS": ("FANS", "[[2D.2-作業系統內核與虛擬化模糊測試 (Kernel & Hypervisor Fuzzing)]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]"),
    "DaVinci": ("DaVinci", "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]", "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]"),
    "TIRO": ("TIRO", "[[1C.1-二進位與逆向分析 (Binary & Reverse Engineering)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "Chizpurfle": ("Chizpurfle", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[2D.2-作業系統內核與虛擬化模糊測試 (Kernel & Hypervisor Fuzzing)]]"),
    "InputBlaster": ("InputBlaster", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"),
    "TSDroid": ("TSDroid", "[[2B.2-動態污點分析 (Dynamic Taint Analysis - DTA)]]", "[[2D.4-微架構與側通道分析 (Microarchitectural & Side-Channel Analysis)]]"),
    "DroidScope": ("DroidScope", "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]", "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]"),
    "CopperDroid": ("CopperDroid", "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]", "[[2A.3-惡意程式沙盒與行為分析 (Malware Sandbox)]]"),
    "Dynodroid": ("Dynodroid", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "TaintDroid": ("TaintDroid", "[[2B.2-動態污點分析 (Dynamic Taint Analysis - DTA)]]", "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]"),
    "CamDroid": ("CamDroid", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]"),
    "Brahmastra": ("Brahmastra", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[1C.2-軟體組成與供應鏈安全 (Software Composition & Supply Chain SCA)]]"),
    "Obfuscation": ("Obfuscation", "[[1C.1-二進位與逆向分析 (Binary & Reverse Engineering)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "PendingIntent": ("PendingIntent", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[1B.1-資料流分析 (Data Flow Analysis)]]"),
    "Clipboard": ("Clipboard", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]"),
    "DevSecOps": ("DevSecOps", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]"),
    "CICD": ("CICD_DevSecOps", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]"),
    "SSLTLS": ("SSLTLS_Security", "[[1D.2-密碼學與協議安全審計 (Cryptographic & Protocol Security)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"),
    "TrustZone": ("TrustZone", "[[2D.4-微架構與側通道分析 (Microarchitectural & Side-Channel Analysis)]]", "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]"),
    "BLE": ("BLE_GATT", "[[2A.2-黑箱協定模糊測試 (Black-box Protocol Fuzzing)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]")
}

def clean_title(t):
    t = t.replace('\u2010', '-').replace('\u2013', '-').replace('\u2014', '-').replace("'", '')
    t = re.sub(r'^\d+[\s_]+', '', t)
    t = re.sub(r'^[A-Za-z0-9_&.,]+_et_al[.,_]*', '', t)
    t = re.sub(r'[:/?*\"<>|\\.,_]+', ' ', t).strip()
    words = t.split()[:5]
    return "_".join(words)

def process_dir(src_dir, dest_dir, cat_label):
    if not os.path.exists(src_dir):
        return
    md_files = [f for f in os.listdir(src_dir) if f.endswith(".md") and f != "README.md"]
    print(f"\nProcessing {len(md_files)} papers from {src_dir} -> {dest_dir}...")
    
    for md_name in md_files:
        md_path = os.path.join(src_dir, md_name)
        base_name = md_name[:-3]
        
        # Corresponding PDF and assets
        pdf_name = base_name + ".pdf"
        pdf_path = os.path.join(src_dir, pdf_name)
        assets_name = base_name + "_assets"
        assets_path = os.path.join(src_dir, assets_name)
        
        with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Parse title, year, heading
        h1 = ""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# ") and not line.startswith("# **") and not line.startswith("# Page"):
                h1 = line[2:].strip()
                break
                
        year_m = re.search(r'year:\s*(\d{4})', content)
        if not year_m:
            year_m = re.search(r'\b(20[0-2]\d|199\d)\b', content[:3000])
        year = year_m.group(1) if year_m else "2024"
        
        # Detect tool or topic
        matched_tool = None
        for k in KNOWN_TOOLS:
            if re.search(r'\b' + re.escape(k) + r'\b', f"{md_name} {h1}", re.IGNORECASE):
                matched_tool = k
                break
                
        if matched_tool:
            tool_prefix, g1, g2 = KNOWN_TOOLS[matched_tool]
            short_t = clean_title(h1) if h1 else tool_prefix
            new_base = f"{tool_prefix}_({year})_{short_t}"
            genres = [g1, g2]
        else:
            # Author fallback
            author_m = re.search(r'author:\s*\"?([^\r\n\"]+)', content)
            author = ""
            if author_m:
                parts = author_m.group(1).split(',')[0].strip().split()
                if parts: author = parts[-1]
            if not author:
                m = re.search(r'\d+_([A-Za-z\-]+)', md_name)
                if m: author = m.group(1)
            author = author or "Paper"
            short_t = clean_title(h1) if h1 else "Research"
            new_base = f"{author}_({year})_{short_t}"
            genres = ["[[2A.1-Web與API動態漏洞掃描 (DAST)]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]"]
            
        # Ensure unique and safe filename
        new_base = re.sub(r'[:/?*\"<>|\\.,_]+', '_', new_base).strip('_')
        new_md_name = new_base + ".md"
        new_pdf_name = new_base + ".pdf"
        new_assets_name = new_base + "_assets"
        
        # Update Frontmatter in markdown
        # Add categories if not present
        cat_block = "\n".join([f'  - "{g}"' for g in genres])
        if "categories:" not in content:
            fm_addon = f'secverify_category: "{cat_label}"\ncategories:\n{cat_block}\n'
            content = re.sub(r'^---\r?\n', f'---\n{fm_addon}', content, count=1)
        else:
            if "secverify_category:" not in content:
                content = re.sub(r'^---\r?\n', f'---\nsecverify_category: "{cat_label}"\n', content, count=1)
                
        # If assets folder exists, update link references inside content
        if os.path.exists(assets_path):
            dest_assets_path = os.path.join(dest_dir, new_assets_name)
            if os.path.exists(dest_assets_path):
                shutil.rmtree(dest_assets_path)
            shutil.move(assets_path, dest_assets_path)
            content = content.replace(f"./{assets_name}/", f"./{new_assets_name}/")
            content = content.replace(f"{assets_name}/", f"{new_assets_name}/")
            
        # Write new Markdown to destination
        dest_md_path = os.path.join(dest_dir, new_md_name)
        with open(dest_md_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [MD] {md_name} -> {new_md_name}")
        
        # Move PDF if exists
        if os.path.exists(pdf_path):
            dest_pdf_path = os.path.join(dest_dir, new_pdf_name)
            shutil.copy2(pdf_path, dest_pdf_path)
            print(f"  [PDF] {pdf_name} -> {new_pdf_name}")

process_dir(
    r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification",
    DEST_CAT_A,
    "Category A"
)

process_dir(
    r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_B_sast_blindspot_exploration",
    DEST_CAT_B,
    "Category B"
)

process_dir(
    r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\legacy_archive\papers",
    DEST_LEGACY,
    "Legacy"
)

print("\nAll papers migrated successfully!")
