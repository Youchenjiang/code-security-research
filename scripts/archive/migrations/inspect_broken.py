import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
VAULT = os.path.join(REPO, "research-vault")
RAW = os.path.join(REPO, "raw-papers")

broken_notes = [
    "Dong Understanding Android Obfuscation (2025).md",
    "d'Amorim (2024) 32nd ACM International Conference on.md",
    "Labeda Sepczuk (2025).md",
    "Song EHBDroid (2025).md",
    "Dong (2024) Assessing Privacy Compliance of Android.md",
    "GPT-Monkey (2025) GPT-Monkey Enhancing Automated GUI Testing.md",
    "Iannillo (2024) Chizpurfle Gray-Box Android Fuzzer.md",
    "Liu (2023) Testing the Limits Unusual Text.md",
    "Mobile (2024) Mobile Payment Security A Critical.md",
    "New (2022) Approach to the Test Oracle Problem for Compilers.md",
    "Su (2017) Guided Stochastic Model-Based GUI Testing.md",
    "TEval+ (2023) Realistic Evaluation for Neural Test Oracle Generation Models.md",
    "Mao Sapienz (2025).md",
    "ScenGen (2025).md",
    "Druffel & Heid (2020) DaVinci Beyond Frida via Syscall.md",
    "Romdhana (2022) Assessing Inter-App Communications.md",
    "Systematic (2024) Systematic Study of Clipboard Usage.md",
    "Shakevsky (2022) Trust Dies in Darkness Samsung.md",
    "Automating (2024) Automating Security Testing in CICD.md",
    "DevSecOps (2024) Automated security testing in DevSecOps.md",
    "DevSecOps (2024) Evolution of DevSecOps and Its.md",
    "ReAssert (2020) Learning to Repair Broken Test Assertions.md",
    "Zhao (2024) Identifying Primary Dimensions of DevSecOps.md",
    "AugmenTest (2025) Enhancing Unit Tests with LLM-Driven Test Prefix & Assertion Generation.md",
    "Liu (2023) Make LLM a Testing Expert.md",
    "CyberGym E2E (2026).md"
]

for note_file in broken_notes:
    note_path = None
    for root, dirs, files in os.walk(VAULT):
        if note_file in files:
            note_path = os.path.join(root, note_file)
            break
    if not note_path:
        print(f"Note not found: {note_file}")
        continue
    rel = os.path.relpath(os.path.dirname(note_path), VAULT)
    raw_dir = os.path.join(RAW, rel)
    existing_raw_pdfs = [f for f in os.listdir(raw_dir) if f.endswith(".pdf")] if os.path.exists(raw_dir) else []
    print(f"{note_file:40} in {rel:40} | RAW PDFs: {existing_raw_pdfs[:3]}")
