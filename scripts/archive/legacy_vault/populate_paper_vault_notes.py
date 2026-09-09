import os
import re

paper_dir = 'paper_markdowns'
target_vault_papers = 'research-vault/papers'

os.makedirs(target_vault_papers, exist_ok=True)

# Mapping of Paper ID / prefix to Metadata and Genre Categories
paper_metadata = {
    "01": {
        "title": "The Oracle Problem in Software Testing: A Survey",
        "year": 2015,
        "venue": "IEEE TSE",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "02": {
        "title": "Security testing of Web applications: a search-based approach for XSS vulnerabilities",
        "year": 2012,
        "venue": "IEEE SEFM",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"]
    },
    "03": {
        "title": "SOFIA: Automated testing for SQL injection vulnerabilities in Web applications",
        "year": 2016,
        "venue": "ASE / ISSTA",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"]
    },
    "05": {
        "title": "TOGA: A Neural Method for Test Oracle Generation",
        "year": 2022,
        "venue": "ICSE 2022",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[1D.1-學習型靜態分析 (Learning-based Static)]]"]
    },
    "06": {
        "title": "TOGLL: Correct and Strong Test Oracle Generation with LLMs",
        "year": 2024,
        "venue": "ICSE 2024",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"]
    },
    "07": {
        "title": "ChatAssert: Automated Test Assertion Generation via Dynamic Feedback Loop with LLMs",
        "year": 2025,
        "venue": "IEEE TSE 2025",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"]
    },
    "08": {
        "title": "AugmenTest: Enhancing Unit Tests with LLM-Driven Test Prefix & Assertion Generation",
        "year": 2025,
        "venue": "ICST 2025",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "09": {
        "title": "AutoOracle: High-Quality C/C++ Test Oracle Generation with LLMs and Dynamic Filtering",
        "year": 2026,
        "venue": "ICSE 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2D.1-微執行與模擬測試 (Micro-execution & Emulation)]]"]
    },
    "10": {
        "title": "LLM Invariant Synthesis for Security Probes without Ground Truth",
        "year": 2026,
        "venue": "IEEE Computer 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[1D.3-形式化驗證與模型檢查 (Formal Verification & Model Checking)]]"]
    },
    "11": {
        "title": "AutoSUIT: Dual-Track Vulnerability vs. Fix Contrastive Test Generation",
        "year": 2026,
        "venue": "ACL Findings 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]"]
    },
    "12": {
        "title": "SecMutBench: Evaluating Security Test Oracles via CWE Mutation Operators",
        "year": 2026,
        "venue": "AIware 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2B.4-變異測試 (Mutation Testing)]]"]
    },
    "13": {
        "title": "CWEval: Outcome-Driven Evaluation on Functional and Security Compliance",
        "year": 2025,
        "venue": "ICSE 2025",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "14": {
        "title": "Assertain: Automated Generation of SystemVerilog Security Assertions (SVA)",
        "year": 2026,
        "venue": "arXiv 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "15": {
        "title": "SecAwareCoder: Toward Secure Code Generation with Task-Adaptive Threat Modeling",
        "year": 2026,
        "venue": "ISSTA 2026",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[3C.2-LLM與Agent驅動修復 (LLM & Agentic)]]"]
    },
    "16": {
        "title": "TECO: Deep Semantics Test Completion with Pretrained Code Models",
        "year": 2023,
        "venue": "ICSE 2023",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "17": {
        "title": "TEval+: Realistic Evaluation for Neural Test Oracle Generation Models",
        "year": 2023,
        "venue": "ISSTA 2023",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "18": {
        "title": "Neural-Based Test Oracle Generation: A Large-Scale Empirical Study",
        "year": 2023,
        "venue": "TSE 2023",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "19": {
        "title": "SecurityEval: A Benchmark Dataset for Vulnerability Detection",
        "year": 2022,
        "venue": "MSR 2022",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[1D.5-漏洞情報與軟體歷史庫挖掘 (Vulnerability Intelligence & Repository Mining)]]"]
    },
    "20": {
        "title": "Test Oracle Automation in the Era of LLMs: A Roadmap",
        "year": 2025,
        "venue": "ACM TOSEM 2025",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "21": {
        "title": "Using Machine Learning to Generate Test Oracles: A Systematic Mapping Study",
        "year": 2021,
        "venue": "JSS 2021",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "22": {
        "title": "Learning to Generate Correct Assertions for Unit Tests",
        "year": 2020,
        "venue": "ICSE 2020",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[1D.1-學習型靜態分析 (Learning-based Static)]]"]
    },
    "23": {
        "title": "AthenaTest: Generating Unit Tests using Pre-trained Transformer Models",
        "year": 2020,
        "venue": "ASE 2020",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "24": {
        "title": "ReAssert: Learning to Repair Broken Test Assertions",
        "year": 2020,
        "venue": "ICSE 2020",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[3A.2-安全補丁驗證與PCA (Validation & PCA)]]"]
    },
    "25": {
        "title": "NUTS: On Learning Meaningful Assert Statements for Unit Tests",
        "year": 2021,
        "venue": "ICST 2021",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "26": {
        "title": "EDITAS: Retrieve-and-Edit Assertion Generation for Unit Tests",
        "year": 2023,
        "venue": "ASE 2023",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "27": {
        "title": "Grammar-Based Oracle for Web Application Security Testing",
        "year": 2013,
        "venue": "ISSTA 2013",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2A.1-Web與API動態漏洞掃描 (DAST)]]"]
    },
    "28": {
        "title": "Metamorphic Security Testing for Web Systems",
        "year": 2021,
        "venue": "TSE 2021",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]"]
    },
    "29": {
        "title": "CodeSecEval: Is Your AI-Generated Code Really Safe?",
        "year": 2024,
        "venue": "NeurIPS 2024",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "30": {
        "title": "A New Approach to the Test Oracle Problem for Compilers",
        "year": 2022,
        "venue": "PLDI 2022",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2C.2-語意差異與並發偵測 (Differential & Concurrency)]]"]
    },
    "31": {
        "title": "The Daikon System for Dynamic Detection of Likely Invariants",
        "year": 2007,
        "venue": "Science of Computer Programming",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[1D.3-形式化驗證與模型檢查 (Formal Verification & Model Checking)]]"]
    },
    "32": {
        "title": "Whole Test Suite Generation with EvoSuite",
        "year": 2013,
        "venue": "IEEE TSE 2013",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]"]
    },
    "33": {
        "title": "CyberSecEval: A Wide-Ranging Cybersecurity Evaluation Suite",
        "year": 2023,
        "venue": "Meta AI 2023",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    },
    "34": {
        "title": "Generating Accurate Assert Statements via Pretrained BART Models",
        "year": 2022,
        "venue": "AST 2022",
        "categories": ["[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]"]
    }
}

count = 0
for fname in sorted(os.listdir(paper_dir)):
    if not fname.endswith('.md'):
        continue
    prefix = fname[:2]
    if prefix in paper_metadata:
        meta = paper_metadata[prefix]
        src_path = os.path.join(paper_dir, fname)
        with open(src_path, 'r', encoding='utf-8', errors='ignore') as sf:
            body = sf.read()
        
        # Strip existing frontmatter if any
        if body.startswith('---'):
            parts = body.split('---', 2)
            if len(parts) >= 3:
                body = parts[2]
        
        cats_formatted = "\n".join([f'  - "{c}"' for c in meta['categories']])
        frontmatter = f"""---
title: "{meta['title']}"
year: {meta['year']}
venue: "{meta['venue']}"
categories:
{cats_formatted}
---

"""
        clean_title = meta['title'].replace(' ', '_').replace(':', '').replace('/', '_').replace('?', '')
        dest_filename = f"{prefix}_{clean_title}.md"
        dest_path = os.path.join(target_vault_papers, dest_filename)
        
        with open(dest_path, 'w', encoding='utf-8') as df:
            df.write(frontmatter + body.lstrip())
        
        count += 1
        print(f"Created paper note [{prefix}]: {dest_filename}")

print(f"Successfully populated {count} paper note files in {target_vault_papers}!")
