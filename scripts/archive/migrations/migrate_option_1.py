import os
import re
import shutil
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VAULT_ROOT = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\research-vault"
PAPERS_DIR = os.path.join(VAULT_ROOT, "papers")

TARGETS = {
    "0_DESIGN": os.path.join(VAULT_ROOT, "0-設計安全與威脅分析 (Secure Design & Threat Analysis)"),
    "1A_SYNTAX": os.path.join(VAULT_ROOT, "1-靜態分析 (Static Analysis)", "1A-基礎與結構分析 (Foundational & Structural)"),
    "1B_DATAFLOW": os.path.join(VAULT_ROOT, "1-靜態分析 (Static Analysis)", "1B-語意與資料流分析 (Semantics & Data Flow)"),
    "1C_REVERSE": os.path.join(VAULT_ROOT, "1-靜態分析 (Static Analysis)", "1C-逆向與相依性安全 (Reverse & Dependency)"),
    "1D_AI_STATIC": os.path.join(VAULT_ROOT, "1-靜態分析 (Static Analysis)", "1D-領域與智慧型靜態分析 (Domain-Specific & AI)"),
    "2A_BLACKBOX": os.path.join(VAULT_ROOT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)"),
    "2B_FUZZ_ORACLE": os.path.join(VAULT_ROOT, "2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)"),
    "2C_INSTRUMENT": os.path.join(VAULT_ROOT, "2-動態分析 (Dynamic Analysis)", "2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)"),
    "2D_SYSTEM": os.path.join(VAULT_ROOT, "2-動態分析 (Dynamic Analysis)", "2D-系統與特定領域測試 (System & Target-Specific)"),
    "3A_VALIDATION": os.path.join(VAULT_ROOT, "3-自動修復 (Automated Program Repair - APR)", "3A-定位與驗證基礎 (Localization & Validation)"),
    "3B_CLASSIC_APR": os.path.join(VAULT_ROOT, "3-自動修復 (Automated Program Repair - APR)", "3B-經典語意修復 (Classical & Semantic Repair)"),
    "3C_LLM_APR": os.path.join(VAULT_ROOT, "3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)")
}

for t in TARGETS.values():
    os.makedirs(t, exist_ok=True)

def decide_target(fname, content):
    lower = f"{fname} {content[:2000]}".lower()
    
    # 3C: LLM & Agent
    if any(k in lower for k in ["gptdroid", "scengen", "agentic", "a2_", "llm-guided dynamic security"]):
        return TARGETS["3C_LLM_APR"]
        
    # 3A: DevSecOps, Validation, CI/CD
    if any(k in lower for k in ["devsecops", "cicd", "patch validation", "reassert"]):
        return TARGETS["3A_VALIDATION"]
        
    # 1C: Reverse, Obfuscation, Native binary
    if any(k in lower for k in ["obfuscation", "tiro", "brahmastra", "reverse engineering", "binary"]):
        return TARGETS["1C_REVERSE"]
        
    # 1B: Dataflow, PendingIntent, Taint static, Call graph
    if any(k in lower for k in ["pendingintent", "intellidroid", " car_", "appintent", "vetdroid", "call graph", "data flow"]):
        return TARGETS["1B_DATAFLOW"]
        
    # 1D: Benchmarks, Cryptography, Evaluation suites
    if any(k in lower for k in ["cyberseceval", "securityeval", "cweval", "secmutbench", "codeseceval"]):
        return TARGETS["1D_AI_STATIC"]
        
    # 2D: Kernel, Hypervisor, OS services, TEE, Micro-execution, Dynodroid, DroidScope, CopperDroid
    if any(k in lower for k in ["fans", "trustzone", "tee", "droidscope", "copperdroid", "tsdroid", "residual api", "dynodroid"]):
        return TARGETS["2D_SYSTEM"]
        
    # 2C: Hooking, Instrumentation, Clipboard, Concurrency
    if any(k in lower for k in ["davinci", "frida", "hooking", "clipboard", "instrumentation", "sanitizer"]):
        return TARGETS["2C_INSTRUMENT"]
        
    # 2B: Fuzzing, Test Oracle, Dynamic Taint (DroidBot, Stoat, Sapienz, TaintDroid, TOGA, AutoOracle)
    if any(k in lower for k in ["droidbot", "stoat", "sapienz", "taintdroid", "inputblaster", "gpt-monkey", "oracle", "assertion", "fuzzing", "ehbdroid", "camdroid", "vialin", "humanoid", "daikon", "evosuite", "athenatest", "teco", "toga", "togll", "chatassert", "mutat"]):
        return TARGETS["2B_FUZZ_ORACLE"]
        
    # 2A: Blackbox DAST, Penetration testing, Web/API scanning, Network SSL/TLS
    return TARGETS["2A_BLACKBOX"]

# Gather all papers and subfolders in PAPERS_DIR
migrated_count = 0
for root, dirs, files in os.walk(PAPERS_DIR):
    for f in files:
        if not f.endswith(".md") or f == "README.md":
            continue
        
        md_src = os.path.join(root, f)
        base = f[:-3]
        pdf_src = os.path.join(root, base + ".pdf")
        assets_src = os.path.join(root, base + "_assets")
        
        with open(md_src, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
            
        dest_folder = decide_target(f, content)
        dest_md = os.path.join(dest_folder, f)
        dest_pdf = os.path.join(dest_folder, base + ".pdf")
        dest_assets = os.path.join(dest_folder, base + "_assets")
        
        # Move assets if exists
        if os.path.exists(assets_src):
            if os.path.exists(dest_assets):
                shutil.rmtree(dest_assets)
            shutil.move(assets_src, dest_assets)
            
        # Move PDF if exists
        if os.path.exists(pdf_src):
            shutil.move(pdf_src, dest_pdf)
            
        # Move Markdown
        shutil.move(md_src, dest_md)
        migrated_count += 1
        print(f"[{os.path.basename(dest_folder)}] <- {f}")

print(f"\nSuccessfully migrated {migrated_count} papers into their respective genre directories!")

# Clean up empty PAPERS_DIR
if os.path.exists(PAPERS_DIR):
    shutil.rmtree(PAPERS_DIR)
    print("Removed obsolete 'papers/' directory completely!")

# Step 3: Update all genre markdown files to remove `from "papers"` in dataview queries
genre_files_updated = 0
for root, dirs, files in os.walk(VAULT_ROOT):
    for f in files:
        if not f.endswith(".md"):
            continue
        fpath = os.path.join(root, f)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
        
        if 'from "papers"' in c:
            new_c = c.replace('from "papers"\n', '')
            new_c = new_c.replace('from "papers"', '')
            with open(fpath, "w", encoding="utf-8") as fp:
                fp.write(new_c)
            genre_files_updated += 1

print(f"Updated Dataview queries in {genre_files_updated} genre overview files (now searching whole vault)!")
