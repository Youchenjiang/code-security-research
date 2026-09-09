import os
import re

vault_papers_dir = 'research-vault/papers'

# Complete multi-category mapping across Static (1), Dynamic (2), Repair (3), Threat (0)
exhaustive_paper_categories = {
    "01": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]"
    ],
    "02": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2A.1-Web與API動態漏洞掃描 (DAST)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "03": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2A.1-Web與API動態漏洞掃描 (DAST)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "05": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "06": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]",
        "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "07": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]",
        "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "08": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "09": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]",
        "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "10": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.3-形式化驗證與模型檢查 (Formal Verification & Model Checking)]]",
        "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "11": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "12": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2B.4-變異測試 (Mutation Testing)]]",
        "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]"
    ],
    "13": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "14": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.3-形式化驗證與模型檢查 (Formal Verification & Model Checking)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "15": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[0.1-威脅建模與攻擊面分析 (Threat Modeling & Attack Surface Analysis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "16": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "17": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]"
    ],
    "18": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "19": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]"
    ],
    "20": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "21": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "22": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "23": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "24": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]",
        "[[3C.1-深度學習修復流派 (DL & NMT)]]"
    ],
    "25": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]"
    ],
    "26": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]",
        "[[3C.1-深度學習修復流派 (DL & NMT)]]"
    ],
    "27": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2A.1-Web與API動態漏洞掃描 (DAST)]]",
        "[[1A.1-語法與結構分析 (Syntactic & AST)]]"
    ],
    "28": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]",
        "[[2A.1-Web與API動態漏洞掃描 (DAST)]]",
        "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]"
    ],
    "29": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]"
    ],
    "30": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]"
    ],
    "31": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.3-形式化驗證與模型檢查 (Formal Verification & Model Checking)]]",
        "[[2C.1-執行期插樁與監控 (Instrumentation & Sanitizers)]]"
    ],
    "32": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]",
        "[[2B.4-變異測試 (Mutation Testing)]]"
    ],
    "33": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"
    ],
    "34": [
        "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]",
        "[[1D.1-學習型靜態分析 (Learning-based Static)]]",
        "[[3C.1-深度學習修復流派 (DL & NMT)]]"
    ]
}

updated_count = 0
for fname in sorted(os.listdir(vault_papers_dir)):
    if not fname.endswith('.md'):
        continue
    prefix = fname[:2]
    if prefix in exhaustive_paper_categories:
        cats = exhaustive_paper_categories[prefix]
        fpath = os.path.join(vault_papers_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace categories section in frontmatter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
            
            # Rebuild categories list
            cats_formatted = "\n".join([f'  - "{c}"' for c in cats])
            
            # Substitute categories: [...] block
            new_fm = re.sub(r'categories:\n(\s*-\s*"\[\[.*?\]\]"\n?)+', f'categories:\n{cats_formatted}\n', fm)
            if 'categories:' not in new_fm:
                new_fm += f"\ncategories:\n{cats_formatted}\n"
            
            new_content = f"---{new_fm}---{body}"
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_count += 1
            print(f"Updated [{prefix}] with {len(cats)} categories: {fname}")

print(f"\nExhaustive multi-category audit complete! Updated {updated_count} files in {vault_papers_dir}.")
