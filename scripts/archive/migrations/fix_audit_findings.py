import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

def win_p(p):
    ap = os.path.abspath(p)
    return "\\\\?\\" + ap if not ap.startswith("\\\\?\\") else ap

# 1. Rename Stealthy paper to Kumar (2023)
old_stealthy_stem = "(2023) A Stealthy Dynamic Analysis Framework"
new_stealthy_stem = "Kumar (2023) InviSeal A Stealthy Dynamic Analysis Framework for Android Systems"
d2a_vault = os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)")
d2a_raw = os.path.join(RAW, "2-動態分析 (Dynamic Analysis)", "2A-黑箱與外圍掃描 (Black-box & Boundary)")

v_old = os.path.join(d2a_vault, f"{old_stealthy_stem}.md")
v_new = os.path.join(d2a_vault, f"{new_stealthy_stem}.md")
if os.path.exists(win_p(v_old)):
    with open(win_p(v_old), "r", encoding="utf-8") as fp:
        content = fp.read()
    content = content.replace(old_stealthy_stem, new_stealthy_stem)
    with open(win_p(v_new), "w", encoding="utf-8") as fp:
        fp.write(content)
    os.remove(win_p(v_old))
    print("Renamed Stealthy in Vault")

for ext in [".pdf", " (Raw).md"]:
    r_old = os.path.join(d2a_raw, f"{old_stealthy_stem}{ext}")
    r_new = os.path.join(d2a_raw, f"{new_stealthy_stem}{ext}")
    if os.path.exists(win_p(r_old)):
        os.rename(win_p(r_old), win_p(r_new))
        print(f"Renamed Stealthy raw {ext}")

# 2. Rename ASTER paper to Pan (2025)
old_aster_stem = "aster-natural-and-multi-language-unit-test-generation-with-llms-2025 (2025)"
new_aster_stem = "Pan (2025) ASTER Natural and Multi-Language Unit Test Generation with LLMs"
d2b_vault = os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)")
d2b_raw = os.path.join(RAW, "2-動態分析 (Dynamic Analysis)", "2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)")

va_old = os.path.join(d2b_vault, f"{old_aster_stem}.md")
va_new = os.path.join(d2b_vault, f"{new_aster_stem}.md")
if os.path.exists(win_p(va_old)):
    with open(win_p(va_old), "r", encoding="utf-8") as fp:
        c = fp.read()
    # clean internal broken wikilinks to raw pdf names
    c = c.replace("[[ASTER_Natural_and_Multi-Language_Unit_Test_Generation_with_LLMs.pdf]]", "`ASTER_Natural_and_Multi-Language_Unit_Test_Generation_with_LLMs.pdf`")
    c = c.replace("[[ASTER_Natural_and_Multi-Language_Unit_Test_Generation_with_LLMs_translated.pdf]]", "`ASTER_Natural_and_Multi-Language_Unit_Test_Generation_with_LLMs_translated.pdf`")
    c = c.replace(old_aster_stem, new_aster_stem)
    with open(win_p(va_new), "w", encoding="utf-8") as fp:
        fp.write(c)
    os.remove(win_p(va_old))
    print("Renamed ASTER in Vault")

for ext in [".pdf", " (Raw).md"]:
    ra_old = os.path.join(d2b_raw, f"{old_aster_stem}{ext}")
    ra_new = os.path.join(d2b_raw, f"{new_aster_stem}{ext}")
    if os.path.exists(win_p(ra_old)):
        os.rename(win_p(ra_old), win_p(ra_new))
        print(f"Renamed ASTER raw {ext}")

# 3. Fix broken wikilinks in 00-多維正交分類法藍圖.md
bp_file = os.path.join(VAULT, "00-多維正交分類法藍圖.md")
if os.path.exists(win_p(bp_file)):
    with open(win_p(bp_file), "r", encoding="utf-8") as fp:
        c = fp.read()
    c = c.replace("[[2B.5-自動化測試生成]]", "[[2B.5-測試預言與斷言合成 (Test Oracle & Assertion Synthesis)]]")
    c = c.replace("[[2D.3-智能合約與 Web3 安全]]", "[[2D.3-智能合約與 Web3 安全 (Smart Contract & Web3 Security)]]")
    c = c.replace("[[2B.1-反饋引導式模糊測試]]", "[[2B.1-反饋引導式模糊測試 (Feedback-directed Fuzzing)]]")
    with open(win_p(bp_file), "w", encoding="utf-8") as fp:
        fp.write(c)
    print("Fixed 00-多維正交分類法藍圖.md wikilinks")

# 4. Fix math interval syntax in Druffel & Heid
dh_file = os.path.join(VAULT, "2-動態分析 (Dynamic Analysis)", "2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Druffel & Heid (2020) DaVinci Beyond Frida via Syscall.md")
if os.path.exists(win_p(dh_file)):
    with open(win_p(dh_file), "r", encoding="utf-8") as fp:
        c = fp.read()
    c = c.replace("[[0 , 9]]", "[0, 9]")
    c = c.replace("[[1 , K]]", "[1, K]")
    c = c.replace("[[0 , 1]]", "[0, 1]")
    with open(win_p(dh_file), "w", encoding="utf-8") as fp:
        fp.write(c)
    print("Fixed math intervals in Druffel & Heid")

# 5. Fix citation numbers in SecVerify 研究流派對照指南.md
sv_file = os.path.join(VAULT, "syntheses", "SecVerify 研究流派對照指南.md")
if os.path.exists(win_p(sv_file)):
    with open(win_p(sv_file), "r", encoding="utf-8") as fp:
        c = fp.read()
    c = re.sub(r'\[\[(\d+)\]\]', r'[\1]', c)
    with open(win_p(sv_file), "w", encoding="utf-8") as fp:
        fp.write(c)
    print("Fixed citation numbers in SecVerify 指南")

# 6. Archive unreferenced leftover files in raw-papers
archive_dir = os.path.join(RAW, "legacy_archive", "unreferenced_leftovers")
os.makedirs(win_p(archive_dir), exist_ok=True)

unreferenced_files = [
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Allen.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Allen (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Lan Statistical Analysis.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Lan Statistical Analysis (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Suo.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Suo (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Sutter.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Sutter (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Understanding Reproducibility.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Understanding Reproducibility (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "2512.12551v1.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "preprints202312.1009.v1.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2A-黑箱與外圍掃描 (Black-box & Boundary)", "Roshanaei download.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Auer.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Auer (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Li Humanoid.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2B-反饋模糊測試與污點分析 (Feedback Fuzzing & Taint)", "Li Humanoid (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Li DroidBot.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Li DroidBot (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Mao Sapienz.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2C-插樁、監控與防禦強化 (Instrumentation, Monitor & Hardening)", "Mao Sapienz (Raw).md"),
    ("2-動態分析 (Dynamic Analysis)/2D-系統與特定領域測試 (System & Target-Specific)", "Song EHBDroid.pdf"),
    ("2-動態分析 (Dynamic Analysis)/2D-系統與特定領域測試 (System & Target-Specific)", "Song EHBDroid (Raw).md"),
    ("3-自動修復 (Automated Program Repair - APR)/3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "Labeda & Sepczuk.pdf"),
    ("3-自動修復 (Automated Program Repair - APR)/3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "Labeda & Sepczuk (Raw).md"),
    ("3-自動修復 (Automated Program Repair - APR)/3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "Liu GPTDroid.pdf"),
    ("3-自動修復 (Automated Program Repair - APR)/3C-深度學習與大模型修復 (Deep Learning & LLM Repair)", "Liu GPTDroid (Raw).md"),
]

for d, f in unreferenced_files:
    src = os.path.join(RAW, d, f)
    dst = os.path.join(archive_dir, f)
    if os.path.exists(win_p(src)):
        if os.path.exists(win_p(dst)):
            os.remove(win_p(dst))
        os.rename(win_p(src), win_p(dst))
        print(f"Archived leftover: {f}")

print("Audit fixes completed successfully!")
