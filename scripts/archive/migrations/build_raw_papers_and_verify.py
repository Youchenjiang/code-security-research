import os
import re
import shutil
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
RAW_PAPERS_DIR = os.path.join(REPO_ROOT, "raw-papers")
VAULT_DIR = os.path.join(REPO_ROOT, "research-vault")

# Target genre folders in raw-papers
GENRE_MAP = {
    "0_DESIGN": "0-設計安全與威脅分析 (Secure Design & Threat Analysis)",
    "1A_SYNTAX": os.path.join("1-靜態分析 (Static Analysis)", "1A-基礎與結構分析 (Foundational & Structural)"),
    "1B_DATAFLOW": os.path.join("1-靜態分析 (Static Analysis)", "1B-語意與資料流分析 (Semantics & Data Flow)"),
    "1C_REVERSE": os.path.join("1-靜態分析 (Static Analysis)", "1C-逆向與相依性安全 (Reverse & Dependency)"),
    "1D_AI_STATIC": os.path.join("1-靜態分析 (Static Analysis)", "1D-領域與智慧型靜態分析 (Domain-Specific & AI)"),
    "2A_BLACKBOX": os.path.join("2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)"),
    "2B_FUZZ_ORACLE": os.path.join("2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)"),
    "2C_INSTRUMENT": os.path.join("2-動態分析 (Dynamic Analysis)", "2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)"),
    "2D_SYSTEM": os.path.join("2-動態分析 (Dynamic Analysis)", "2D-系統與特定領域測試 (System & Target-Specific)"),
    "3A_VALIDATION": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3A-定位與驗證基礎 (Localization & Validation)"),
    "3B_CLASSIC_APR": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3B-經典語意修復 (Classical & Semantic Repair)"),
    "3C_LLM_APR": os.path.join("3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)")
}

for g in GENRE_MAP.values():
    os.makedirs(os.path.join(RAW_PAPERS_DIR, g), exist_ok=True)
    os.makedirs(os.path.join(VAULT_DIR, g), exist_ok=True)

def decide_genre(fname, content):
    lower = f"{fname} {content[:2000]}".lower()
    if any(k in lower for k in ["gptdroid", "scengen", "agentic", "a2_", "llm-guided dynamic security"]):
        return GENRE_MAP["3C_LLM_APR"]
    if any(k in lower for k in ["devsecops", "cicd", "patch validation", "reassert"]):
        return GENRE_MAP["3A_VALIDATION"]
    if any(k in lower for k in ["obfuscation", "tiro", "brahmastra", "reverse engineering", "binary"]):
        return GENRE_MAP["1C_REVERSE"]
    if any(k in lower for k in ["pendingintent", "intellidroid", " car_", "appintent", "vetdroid", "call graph", "data flow"]):
        return GENRE_MAP["1B_DATAFLOW"]
    if any(k in lower for k in ["cyberseceval", "securityeval", "cweval", "secmutbench", "codeseceval"]):
        return GENRE_MAP["1D_AI_STATIC"]
    if any(k in lower for k in ["fans", "trustzone", "tee", "droidscope", "copperdroid", "tsdroid", "residual api", "dynodroid"]):
        return GENRE_MAP["2D_SYSTEM"]
    if any(k in lower for k in ["davinci", "frida", "hooking", "clipboard", "instrumentation", "sanitizer"]):
        return GENRE_MAP["2C_INSTRUMENT"]
    if any(k in lower for k in ["droidbot", "stoat", "sapienz", "taintdroid", "inputblaster", "gpt-monkey", "oracle", "assertion", "fuzzing", "ehbdroid", "camdroid", "vialin", "humanoid", "daikon", "evosuite", "athenatest", "teco", "toga", "togll", "chatassert", "mutat"]):
        return GENRE_MAP["2B_FUZZ_ORACLE"]
    return GENRE_MAP["2A_BLACKBOX"]

manifest = []

# Part 1: Process Batch 1 (Oracle papers in papers/ & paper_markdowns/)
old_papers_dir = os.path.join(REPO_ROOT, "papers")
old_md_dir = os.path.join(REPO_ROOT, "paper_markdowns")

if os.path.exists(old_papers_dir) and os.path.exists(old_md_dir):
    for f in os.listdir(old_papers_dir):
        if not f.endswith(".pdf"): continue
        base = f[:-4]
        md_name = base + ".md"
        pdf_path = os.path.join(old_papers_dir, f)
        md_path = os.path.join(old_md_dir, md_name)
        
        md_content = ""
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
                md_content = fp.read()
                
        genre_sub = decide_genre(f, md_content)
        
        # Raw destinations
        dest_pdf = os.path.join(RAW_PAPERS_DIR, genre_sub, f)
        dest_raw_md = os.path.join(RAW_PAPERS_DIR, genre_sub, base + "_raw.md")
        
        shutil.copy2(pdf_path, dest_pdf)
        if os.path.exists(md_path):
            shutil.copy2(md_path, dest_raw_md)
            
        manifest.append({
            "source_type": "Oracle_Batch",
            "source_pdf": pdf_path,
            "source_md": md_path if os.path.exists(md_path) else None,
            "raw_dest_pdf": dest_pdf,
            "raw_dest_md": dest_raw_md if os.path.exists(md_path) else None,
            "genre": genre_sub,
            "pdf_size": os.path.getsize(dest_pdf),
            "md_size": os.path.getsize(dest_raw_md) if os.path.exists(dest_raw_md) else 0
        })

# Part 2: Process Batch 2 (Android papers in new/papers/ and new/legacy_archive/papers/)
android_sources = [
    os.path.join(REPO_ROOT, "new", "papers", "category_A_sast_guided_verification"),
    os.path.join(REPO_ROOT, "new", "papers", "category_B_sast_blindspot_exploration"),
    os.path.join(REPO_ROOT, "new", "papers", "supplementary"),
    os.path.join(REPO_ROOT, "new", "legacy_archive", "papers")
]

for sdir in android_sources:
    if not os.path.exists(sdir): continue
    for f in os.listdir(sdir):
        if not f.endswith(".pdf"): continue
        base = f[:-4]
        md_name = base + ".md"
        pdf_path = os.path.join(sdir, f)
        md_path = os.path.join(sdir, md_name)
        assets_dir = os.path.join(sdir, base + "_assets")
        
        md_content = ""
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
                md_content = fp.read()
                
        genre_sub = decide_genre(f, md_content)
        
        dest_pdf = os.path.join(RAW_PAPERS_DIR, genre_sub, f)
        dest_raw_md = os.path.join(RAW_PAPERS_DIR, genre_sub, base + "_raw.md")
        dest_assets = os.path.join(RAW_PAPERS_DIR, genre_sub, base + "_assets")
        
        shutil.copy2(pdf_path, dest_pdf)
        if os.path.exists(md_path):
            shutil.copy2(md_path, dest_raw_md)
        if os.path.exists(assets_dir):
            if os.path.exists(dest_assets):
                shutil.rmtree(dest_assets)
            shutil.copytree(assets_dir, dest_assets)
            
        manifest.append({
            "source_type": "Android_Batch",
            "source_pdf": pdf_path,
            "source_md": md_path if os.path.exists(md_path) else None,
            "raw_dest_pdf": dest_pdf,
            "raw_dest_md": dest_raw_md if os.path.exists(md_path) else None,
            "genre": genre_sub,
            "pdf_size": os.path.getsize(dest_pdf),
            "md_size": os.path.getsize(dest_raw_md) if os.path.exists(dest_raw_md) else 0
        })

print(f"Collected and populated raw-papers with {len(manifest)} papers!")

# Part 3: Verify 100% integrity of raw-papers
all_passed = True
missing_count = 0
for item in manifest:
    if not os.path.exists(item["raw_dest_pdf"]) or os.path.getsize(item["raw_dest_pdf"]) == 0:
        print(f"VERIFICATION ERROR: PDF missing or empty -> {item['raw_dest_pdf']}")
        all_passed = False
        missing_count += 1
    if item["source_md"] and (not os.path.exists(item["raw_dest_md"]) or os.path.getsize(item["raw_dest_md"]) == 0):
        print(f"VERIFICATION ERROR: Raw MD missing or empty -> {item['raw_dest_md']}")
        all_passed = False
        missing_count += 1

verification_report = {
    "total_papers_tracked": len(manifest),
    "all_passed": all_passed,
    "missing_count": missing_count,
    "items": manifest
}

report_json_path = os.path.join(REPO_ROOT, "paper_migration_verification.json")
with open(report_json_path, "w", encoding="utf-8") as fp:
    json.dump(verification_report, fp, ensure_ascii=False, indent=2)

print(f"Verification completed. All Passed: {all_passed}, Missing: {missing_count}")
print(f"Detailed manifest saved to {report_json_path}")
