import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

def win_path(p):
    ap = os.path.abspath(p)
    if not ap.startswith("\\\\?\\"):
        return "\\\\?\\" + ap
    return ap

# 1. Remove duplicate stub notes in VAULT
stubs_to_remove = [
    os.path.join(VAULT, "1-靜態分析 (Static Analysis)", "1C-逆向與相依性安全 (Reverse & Dependency)", "1C.1-二進位與逆向分析 (Binary & Reverse Engineering)", "Dong Understanding Android Obfuscation (2025).md"),
    os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "d'Amorim (2024) 32nd ACM International Conference on.md"),
    os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)", "Labeda Sepczuk (2025).md"),
    os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)", "2A.1-Web與API動態漏洞掃描 (DAST)", "Song EHBDroid (2025).md"),
    os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)", "Mao Sapienz (2025).md"),
    os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)", "ScenGen (2025).md"),
    os.path.join(VAULT, "3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "AugmenTest (2025) Enhancing Unit Tests with LLM-Driven Test Prefix & Assertion Generation.md"),
    os.path.join(VAULT, "3-自動修復 (Automated Program Repair - APR)", "3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "Liu (2023) Make LLM a Testing Expert.md")
]

for p in stubs_to_remove:
    if os.path.exists(win_path(p)):
        os.remove(win_path(p))
        print(f"Removed stub note: {os.path.basename(p)}")

# 2. Specific file renames in RAW
renames = [
    # 3A
    ("3-自動修復 (Automated Program Repair - APR)/3A-定位與驗證基礎 (Localization & Validation)", "Automating Security Testing in CICD", "Automating (2024) Automating Security Testing in CICD"),
    ("3-自動修復 (Automated Program Repair - APR)/3A-定位與驗證基礎 (Localization & Validation)", "Evolution of DevSecOps", "DevSecOps (2024) Evolution of DevSecOps and Its"),
    ("3-自動修復 (Automated Program Repair - APR)/3A-定位與驗證基礎 (Localization & Validation)", "Automated Security Testing in DevSecOps AI", "DevSecOps (2024) Automated security testing in DevSecOps"),
    ("3-自動修復 (Automated Program Repair - APR)/3A-定位與驗證基礎 (Localization & Validation)", "Zhao", "Zhao (2024) Identifying Primary Dimensions of DevSecOps"),
    ("3-自動修復 (Automated Program Repair - APR)/3A-定位與驗證基礎 (Localization & Validation)", "Marandi", "ReAssert (2020) Learning to Repair Broken Test Assertions"),
    # 2C
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Heid", "Druffel & Heid (2020) DaVinci Beyond Frida via Syscall"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Romdhana", "Romdhana (2022) Assessing Inter-App Communications"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Systematic Study of Clipboard", "Systematic (2024) Systematic Study of Clipboard Usage"),
    # 2D
    ("2-動態分析 (Dynamic Analysis)/2D-系統與特定領域測試 (System & Target-Specific)", "Shakevsky", "Shakevsky (2022) Trust Dies in Darkness Samsung"),
    ("2-動態分析 (Dynamic Analysis)/2D-系統與特定領域測試 (System & Target-Specific)", "CamDroid", "SoWise (2025) CamDroid Context-Aware Model-Based GUI Testing"),
    # 4.2
    ("4-安全基準評測、數據集與靶場 (Benchmarks, Datasets & CyberGym)/4.2-動態攻防與CTF實戰靶場 (Dynamic CTF & Exploit Gym)", "CyberGym (2025)", "CyberGym E2E (2026)"),
    # 2B
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Iannillo Chizpurfle", "Iannillo (2024) Chizpurfle Gray-Box Android Fuzzer"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Liu InputBlaster", "Liu (2023) Testing the Limits Unusual Text"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Mobile Payment Security Critical Analysis", "Mobile (2024) Mobile Payment Security A Critical"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Rigger (2022) A New Approach to the Test Oracle Pro", "New (2022) Approach to the Test Oracle Problem for Compilers"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Su Stoat", "Su (2017) Guided Stochastic Model-Based GUI Testing"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "TEvalPlus (2023) TEval Realistic Evaluation for Neural", "TEval+ (2023) Realistic Evaluation for Neural Test Oracle Generation Models"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "GPT-Monkey", "GPT-Monkey (2025) GPT-Monkey Enhancing Automated GUI Testing"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Assessing Privacy Compliance", "Dong (2024) Assessing Privacy Compliance of Android")
]

for rel_dir, old_stem, new_stem in renames:
    d = os.path.join(RAW, rel_dir)
    old_pdf = os.path.join(d, f"{old_stem}.pdf")
    new_pdf = os.path.join(d, f"{new_stem}.pdf")
    old_raw = os.path.join(d, f"{old_stem} (Raw).md")
    new_raw = os.path.join(d, f"{new_stem} (Raw).md")
    
    if os.path.exists(win_path(old_pdf)):
        if os.path.exists(win_path(new_pdf)):
            os.remove(win_path(new_pdf))
        os.rename(win_path(old_pdf), win_path(new_pdf))
        print(f"Renamed PDF: {old_stem}.pdf -> {new_stem}.pdf")
        
    if os.path.exists(win_path(old_raw)):
        if os.path.exists(win_path(new_raw)):
            os.remove(win_path(new_raw))
        os.rename(win_path(old_raw), win_path(new_raw))
        print(f"Renamed Raw MD: {old_stem} (Raw).md -> {new_stem} (Raw).md")

print("Rename and deduplication pass complete!")
