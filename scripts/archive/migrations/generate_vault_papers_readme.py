import os
import re

VAULT_PAPERS_DIR = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\research-vault\papers"

subdirs = [
    ("01_SAST導引驗證_Category_A", "📂 Category A：SAST 導引驗證與降低誤報", "接收 SAST 可疑候選座標，透過目標導向路徑驅動、LLM 智能導航或微執行，在實機上生成可重現的 PoV，過濾虛假警報。"),
    ("02_SAST盲區突破_Category_B", "📂 Category B：SAST 盲區突破與降低漏報", "針對靜態代碼無語法特徵的深水區（IPC Fuzzing、Syscall 繞過、加殼混淆、原生內存、TEE 韌體），抓出致命漏報。"),
    ("03_測試預言與斷言合成_Oracle", "📂 Testing Oracle & Assertion Synthesis：測試預言與斷言合成", "解決測試預言難題，聚焦於利用 LLM、NMT、變異分析自動合成單元測試斷言、不變量與安全 Oracle。"),
    ("00_歷史經典論文_Legacy", "📂 Legacy：歷史經典奠基文獻", "Dalvik/早期 Android 時代奠基論文（TaintDroid、DroidScope、CopperDroid 等經典架構）。")
]

readme_path = os.path.join(VAULT_PAPERS_DIR, "README.md")

with open(readme_path, "w", encoding="utf-8") as out:
    out.write("# 📚 程式碼安全學術論文總庫 (Code Security Papers Repository)\n\n")
    out.write("> 本論文總庫已全面整合進 Obsidian 雙向連結體系，並對齊 `[[00-研究流派圖主目錄]]`。\n")
    out.write("> 所有論文均已規範化命名，並依據研究任務劃分於四大專用子目錄中。\n\n---\n\n")
    
    for folder, title, desc in subdirs:
        folder_path = os.path.join(VAULT_PAPERS_DIR, folder)
        if not os.path.exists(folder_path):
            continue
        
        md_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".md") and f != "README.md"])
        out.write(f"## {title} ({len(md_files)} 篇)\n\n")
        out.write(f"> {desc}\n\n")
        out.write("| # | 規範論文筆記 (Markdown) | 年份 | 論文原始 PDF |\n")
        out.write("| :---: | :--- | :---: | :--- |\n")
        
        for idx, f in enumerate(md_files, 1):
            base = f[:-3]
            pdf_file = base + ".pdf"
            pdf_exists = os.path.exists(os.path.join(folder_path, pdf_file))
            
            # Extract year from filename
            year_m = re.search(r'\((\d{4})\)', f)
            year = year_m.group(1) if year_m else "-"
            
            pdf_link = f"[{pdf_file}](./{folder}/{pdf_file})" if pdf_exists else "*(無本地 PDF)*"
            out.write(f"| {idx} | [[{folder}/{f}|{base}]] | {year} | {pdf_link} |\n")
        out.write("\n---\n\n")

print("Generated master README at", readme_path)
