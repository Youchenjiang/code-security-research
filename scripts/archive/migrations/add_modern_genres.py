import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

# Define target directories
P4_VAULT = os.path.join(VAULT, "4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)")
P4_RAW = os.path.join(RAW, "4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)")
D1_VAULT = os.path.join(VAULT, "1-靜態分析 (Static Analysis)", "1D-領域與智慧型靜態分析 (Domain-Specific & AI)")
A2_VAULT = os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)")
C3_VAULT = os.path.join(VAULT, "3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)")

for d in [P4_VAULT, P4_RAW, D1_VAULT, A2_VAULT, C3_VAULT]:
    os.makedirs(d, exist_ok=True)

GENRES = [
    {
        "dir": A2_VAULT,
        "filename": "2A.4-自主滲透測試代理與多Agent攻防編排 (Autonomous Pentest & Multi-Agent Orchestration).md",
        "title": "2A.4 自主滲透測試代理與多Agent攻防編排 (Autonomous Pentest & Multi-Agent Orchestration)",
        "concept": "利用大語言模型（LLM）驅動具備推理、規劃、環境交互與反饋循環能力的自主智慧代理（Autonomous Agents），模擬專業紅隊團隊協同執行目標枚舉、漏洞利用與多步橫向滲透。",
        "sub_genres": [
            {"name": "Multi-Agent Offensive Teams (多代理協同紅隊)", "desc": "模擬分工明確的滲透測試團隊（Recon Agent, Exploit Agent, Reporter）。代表系統：PentestGPT, VulnBot, xOffense。"},
            {"name": "Autonomous Exploitation & Planning (自主利用與決策規劃)", "desc": "結合經典規劃演算法與 LLM 反饋循環以克服長記憶丟失與幻覺。代表框架：HPTSA (UIUC), APTAgent, CHECKMATE, AutoPentest。"}
        ],
        "keywords": ["autonomous penetration testing", "LLM agent pentest", "multi-agent orchestration", "offensive AI agents", "automated red teaming", "PentestGPT"],
        "tools": ["PentestGPT", "HPTSA", "VulnBot", "APTAgent", "AutoPentest", "AgentFlow", "RapidPen"],
        "methodology": ["動態分析 - 自主滲透代理 (Dynamic - Autonomous Pentest Agent)"],
        "testing_level": ["系統與全棧級 (System & Full-stack)"],
        "target_domain": ["通用網路、API與端點 (Web, API & Endpoint)"],
        "powered_by": ["大語言模型與Agent (LLM & Autonomous Agent)"]
    },
    {
        "dir": D1_VAULT,
        "filename": "1D.6-神經符號與安全規則自動生成 (Neuro-Symbolic & Rule Synthesis).md",
        "title": "1D.6 神經符號與安全規則自動生成 (Neuro-Symbolic & Rule Synthesis)",
        "concept": "結合神經網路（LLM 的語意理解與少樣本歸納能力）與符號分析（Semgrep, CodeQL, CPG 的嚴謹匹配與無漏報保證），自動從 CVE 描述或代碼補丁中合成確定性靜態安全偵測規則。",
        "sub_genres": [
            {"name": "LLM-Guided Static Checker Synthesis (大模型導引靜態檢查器合成)", "desc": "讓 LLM 自動生成高精確度的 CodeQL 查詢或 Linux Kernel 靜態檢查器。代表系統：KNighter (SOSP '25), QLPro, PersistentFeedback。"},
            {"name": "Rule Mining for Mobile & System (行動與系統規則開採)", "desc": "自動生成 Android 與雲端環境之 Semgrep-compatible 安全偵測規則。代表工具：RuleDroid (IEEE TS '26), RulePilot (ICSE '26), LLMxCPG (USENIX '25)。"}
        ],
        "keywords": ["neuro-symbolic program analysis", "automated rule synthesis", "Semgrep rule generation", "CodeQL query synthesis", "LLMxCPG", "KNighter"],
        "tools": ["RuleDroid", "RulePilot", "KNighter", "LLMxCPG", "QLPro", "Semgrep", "CodeQL"],
        "methodology": ["神經符號靜態分析 (Neuro-Symbolic Static Analysis)"],
        "testing_level": ["函數與組件級 (Function & Component-level)"],
        "target_domain": ["跨平台原始碼 (Cross-Platform Source Code)"],
        "powered_by": ["大語言模型與符號邏輯 (LLM & Symbolic Program Analysis)"]
    },
    {
        "dir": C3_VAULT,
        "filename": "3C.3-網路自主推理系統 (CRS) 與端到端閉環 (Cyber Reasoning Systems - CRS).md",
        "title": "3C.3 網路自主推理系統 (CRS) 與端到端閉環 (Cyber Reasoning Systems - CRS)",
        "concept": "依據 DARPA AIxCC 規範構建之全自主閉環網路安全防禦系統。整合靜態分析、模糊測試、動態 PoC 漏洞利用合成、自動程式修復（APR）與補丁回歸驗收，實現零人工干預的漏洞自主閉環。",
        "sub_genres": [
            {"name": "AIxCC Autonomous CRS Architecture (AIxCC 自主網路推理架構)", "desc": "完整的自主分析-驗證-修復架構。代表系統：ATLANTIS (AIxCC 冠軍), FuzzingBrain V2 (AIxCC 決賽 90% 檢出), OSS-CRS。"},
            {"name": "Closed-Loop Patch Verification (閉環補丁驗證)", "desc": "使用 PoC 回歸測試、動態微執行與語意不變量確保修復不引入破壞性變更。代表研究：SoK AIxCC (USENIX '26), DevSecOps-SAFE。"}
        ],
        "keywords": ["Cyber Reasoning Systems", "CRS", "DARPA AIxCC", "closed-loop automated repair", "ATLANTIS", "FuzzingBrain", "end-to-end vulnerability lifecycle"],
        "tools": ["ATLANTIS", "FuzzingBrain", "OSS-CRS", "Mayhem", "SecVerify+SecRepair"],
        "methodology": ["自主網路推理與閉環修復 (Cyber Reasoning Systems - CRS)"],
        "testing_level": ["全棧系統級 (Full-stack System-level)"],
        "target_domain": ["通用開源軟體與現代系統 (C/C++, Java, Android, Rust)"],
        "powered_by": ["多代理協作、LLM與動態微執行 (Multi-Agent, LLM & Micro-execution)"]
    },
    {
        "dir": P4_VAULT,
        "filename": "4.1-靜態代碼與大模型安全評測 (Static Code & LLM Security Benchmarks).md",
        "title": "4.1 靜態代碼與大模型安全評測 (Static Code & LLM Security Benchmarks)",
        "concept": "專門評估大語言模型（LLM）在代碼生成、靜態漏洞識別、安全合規與安全對齊能力之標準化評測基準、Prompt 注入數據集與自動化評估管線。",
        "sub_genres": [
            {"name": "Code Generation Security Benchmarks (生成代碼安全性評測)", "desc": "評估 AI Copilot/大模型生成之程式碼是否自帶 CWE/CVE 缺陷。代表基準：SecurityEval, CyberSecEval (Meta), CodeSecEval。"},
            {"name": "Functional & Security Compliance (功能與安全合規基準)", "desc": "兼顧功能正確性與安全規範之評測。代表基準：CWEval, SecMutBench (CWE變異運算元)。"}
        ],
        "keywords": ["LLM code security benchmark", "SecurityEval", "CyberSecEval", "CWEval", "CodeSecEval", "vulnerable code generation evaluation"],
        "tools": ["CyberSecEval", "SecurityEval", "CWEval", "CodeSecEval", "SecMutBench"],
        "methodology": ["基準評測與大模型評估 (Benchmarks & LLM Evaluation)"],
        "testing_level": ["代碼級 (Code-level)"],
        "target_domain": ["AI 生成代碼與靜態分析模型 (AI Code Generation)"],
        "powered_by": ["自動化評測框架 (Automated Evaluation Harness)"]
    },
    {
        "dir": P4_VAULT,
        "filename": "4.2-動態攻防與CTF實戰靶場 (Dynamic CTF & Exploit Gym).md",
        "title": "4.2 動態攻防與CTF實戰靶場 (Dynamic CTF & Exploit Gym)",
        "concept": "提供具備可執行 Docker 容器、完整靶機狀態、漏洞復現環境與動態 Flag 驗收之實戰攻防模擬靶場，用於衡量 AI 代理與自動化工具的實戰端到端滲透能力。",
        "sub_genres": [
            {"name": "Large-Scale Real-World Cyber Gyms (大規模真實漏洞靶場)", "desc": "包含成百上千個真實 CVE 運行環境之端到端靶場。代表靶場：CyberGym (1,507 漏洞環境), CyberGym E2E, ZeroDayBench。"},
            {"name": "CTF-based Capability Evaluations (CTF 風格能力分級評測)", "desc": "以專業 CTF 題目量化評估 AI Exploit 成功率與能力階梯。代表基準：CyBench (40 專業級 CTF), ExploitGym, ExploitBench, PACEbench。"}
        ],
        "keywords": ["cybersecurity gym", "CTF benchmark", "CyBench", "CyberGym", "ExploitBench", "dynamic exploit environment", "Docker cyber range"],
        "tools": ["CyBench", "CyberGym", "ExploitGym", "ExploitBench", "ZeroDayBench", "PACEbench"],
        "methodology": ["動態靶場與環境交互 (Dynamic Cyber Range & Interaction)"],
        "testing_level": ["全系統與網路級 (Full System & Network-level)"],
        "target_domain": ["真實世界 CVE、Linux、Web 與 CTF 靶機"],
        "powered_by": ["Docker 容器化與自動化評測代理 (Containerized Sandboxes)"]
    },
    {
        "dir": P4_VAULT,
        "filename": "4.3-自主滲透測試與Agent評測 (Autonomous Agent & Pentest Benchmarks).md",
        "title": "4.3 自主滲透測試與Agent評測 (Autonomous Agent & Pentest Benchmarks)",
        "concept": "評估自主滲透測試代理（Autonomous Pentest Agents）與手機 GUI 測試代理（Mobile GUI Agents）在動態環境中規劃步數、策略多樣性、逃避偵測與安全性邊界的評測基準。",
        "sub_genres": [
            {"name": "Autonomous Pentest Benchmark (自主滲透基準)", "desc": "專門評估 AI Agent 於未知環境下之主動探索與多步利用能力。代表基準：AutoPenBench (EMNLP '25), AgentScan, RapidPen。"},
            {"name": "Mobile Agent Safety & GUI Exploration (行動代理安全與 GUI 探索基準)", "desc": "評估 Android 平台手機 Agent 探索覆蓋率與安全性。代表基準：MobileSafetyBench (AAAI '26), AndroidArena, NotAnA11y (Prompt Injection)。"}
        ],
        "keywords": ["autonomous agent benchmark", "AutoPenBench", "MobileSafetyBench", "AgentScan", "AndroidArena", "phone GUI agent evaluation"],
        "tools": ["AutoPenBench", "MobileSafetyBench", "AgentScan", "AndroidArena"],
        "methodology": ["自主代理能力基準評測 (Autonomous Agent Benchmark)"],
        "testing_level": ["多步規劃與環境導航 (Multi-step Planning & Navigation)"],
        "target_domain": ["行動端與端點自主代理 (Mobile & Autonomous Agents)"],
        "powered_by": ["多模態環境與動態模擬器 (Multimodal Simulators)"]
    },
    {
        "dir": P4_VAULT,
        "filename": "4.4-漏洞修復與程序分析基準 (Vulnerability Repair & Analysis Benchmarks).md",
        "title": "4.4 漏洞修復與程序分析基準 (Vulnerability Repair & Analysis Benchmarks)",
        "concept": "專門用於衡量自動程式修復（APR）、補丁品質、不變量生成與程序分析演算法效能的標準化基準數據集。",
        "sub_genres": [
            {"name": "Automated Vulnerability Patching Benchmarks (漏洞修補基準)", "desc": "真實安全漏洞補丁數據集。代表基準：CVEBench (ICML '25), MoreFixes, SWE-bench (Security tasks), Big-Vul。"},
            {"name": "Vulnerability Reproduction Benchmarks (漏洞復現基準)", "desc": "評估工具重現漏洞軌跡之基準。代表基準：VulR2 (ASE '25), CVEGenie (CCS '26)。"}
        ],
        "keywords": ["vulnerability repair benchmark", "CVEBench", "SWE-bench", "MoreFixes", "patch quality evaluation", "APR benchmark"],
        "tools": ["CVEBench", "SWE-bench", "MoreFixes", "Big-Vul", "Defects4J"],
        "methodology": ["程式修復與程式分析評測 (APR & Analysis Evaluation)"],
        "testing_level": ["模組與補丁級 (Module & Patch-level)"],
        "target_domain": ["通用程式庫與軟體儲存庫 (Open Source Repositories)"],
        "powered_by": ["測試套件與差異分析 (Test Suites & Diff Evaluation)"]
    }
]

for g in GENRES:
    target_file = os.path.join(g["dir"], g["filename"])
    sub_genres_str = ""
    for sg in g["sub_genres"]:
        sub_genres_str += f"### {sg['name']}\n- **簡介**: {sg['desc']}\n\n"
        
    keywords_str = ", ".join([f"`{k}`" for k in g["keywords"]])
    tools_str = ", ".join([f"`{t}`" for t in g["tools"]])
    clean_base = g["filename"][:-3]
    
    content = f"""---
title: "{g['title']}"
type: research-genre
parent: "[[00-研究流派圖主目錄]]"
methodology:
  - "{g['methodology'][0]}"
testing_level:
  - "{g['testing_level'][0]}"
target_domain:
  - "{g['target_domain'][0]}"
powered_by:
  - "{g['powered_by'][0]}"
---

# {g['title']}

## 📌 核心精神 (Core Concept)
{g['concept']}

## 🔍 子技術流派 (Sub-Genres)
{sub_genres_str}
## 🏷️ 學術常用關鍵字 (Keywords)
{keywords_str}

## 🛠️ 代表性工具 / 框架 (Representative Tools)
{tools_str}

---

## 📚 相關論文 (Papers List)

<!-- 
Obsidian Dataview 自動動態列出標記有此流派的所有論文
-->

```dataview
table title as "標題", year as "年份", venue as "發表會/期刊"
where contains(categories, [[{clean_base}]])
sort year desc
```

---
返回 [[00-研究流派圖主目錄|研究流派圖主目錄]]
"""
    with open(target_file, "w", encoding="utf-8") as fp:
        fp.write(content)
    print(f"Generated genre file: {g['filename']}")

print("\nAll 7 modern frontier genre notes successfully created!")
