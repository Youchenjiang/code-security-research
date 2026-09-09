import os
import glob
import re
import json
import urllib.request
import urllib.parse
import pypdf

SAVE_DIR = r'c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\papers'

# Target 33 papers list with unique signatures for matching inside bibliographies
paper_catalog = [
    {"id": "01", "name": "Barr et al. Survey (2015)", "keywords": ["The oracle problem in software testing", "Barr", "Harman", "McMinn"]},
    {"id": "02", "name": "Avancini & Ceccato (2012)", "keywords": ["Security testing of web applications", "Avancini", "Ceccato", "cross-site scripting"]},
    {"id": "03", "name": "SOFIA (2016)", "keywords": ["Automated testing for SQL injection", "SOFIA", "Appelt", "input-driven approach"]},
    {"id": "04", "name": "Athena (2019)", "keywords": ["Athena: Dynamic extraction of security policies", "security policies from software artifacts"]},
    {"id": "05", "name": "TOGA (2022)", "keywords": ["TOGA: A Neural Method for Test Oracle Generation", "TOGA", "Dinella", "Neural Method for Test Oracle"]},
    {"id": "06", "name": "TOGLL (2024)", "keywords": ["Correct and Strong Test Oracle Generation with LLMs", "TOGLL", "OracleGuru", "Hossain"]},
    {"id": "07", "name": "ChatAssert (2025)", "keywords": ["ChatAssert", "Automated Test Assertion Generation with Large Language Models"]},
    {"id": "08", "name": "AugmenTest (2025)", "keywords": ["AugmenTest", "Enhancing Tests with LLM-Driven Oracles", "Khandaker"]},
    {"id": "09", "name": "AutoOracle (2026)", "keywords": ["AutoOracle", "High-Quality C++ Test Oracle Generation", "Suspicious Oracle Synthesis"]},
    {"id": "10", "name": "IEEE Computer (2026)", "keywords": ["LLM Invariant Synthesis", "Security Probes"]},
    {"id": "11", "name": "AutoSUIT Bench (2026)", "keywords": ["AutoSUIT", "Dual-track vulnerability vs fix contrastive benchmark"]},
    {"id": "12", "name": "SecMutBench (2026)", "keywords": ["SecMutBench", "Evaluating Security Test Oracles via CWE Mutation Operators"]},
    {"id": "13", "name": "CWEval (2025)", "keywords": ["CWEval", "Outcome-driven Evaluation on Functionality and Security"]},
    {"id": "14", "name": "Assertain (2026)", "keywords": ["Assertain", "SystemVerilog Security Assertions for RTL Designs"]},
    {"id": "15", "name": "SecAwareCoder (2026)", "keywords": ["Toward Secure Code Generation", "Task-Adaptive Vulnerability Modeling", "SecAwareCoder"]},
    {"id": "16", "name": "TECO (2023)", "keywords": ["Learning Deep Semantics for Test Completion", "TECO", "Nie"]},
    {"id": "17", "name": "TEval+ (2023)", "keywords": ["TEval+", "Realistic Evaluation for Neural Test Oracle Generation"]},
    {"id": "18", "name": "Neural Oracle Eval (2023)", "keywords": ["Neural-Based Test Oracle Generation: A Large-Scale Evaluation"]},
    {"id": "19", "name": "SecurityEval Dataset (2022)", "keywords": ["SecurityEval", "mining vulnerability examples for evaluating code generation"]},
    {"id": "20", "name": "LLM Oracle Roadmap (2025)", "keywords": ["Test Oracle Automation in the Era of LLMs"]},
    {"id": "21", "name": "ML Test Oracles Survey (2021)", "keywords": ["Using Machine Learning to Generate Test Oracles"]},
    {"id": "22", "name": "Atlas (2020)", "keywords": ["Learning to Generate Correct Assertions", "Atlas", "Watson"]},
    {"id": "23", "name": "AthenaTest (2020)", "keywords": ["Generate Test Cases using Pre-trained Transformers", "AthenaTest", "Tufano"]},
    {"id": "24", "name": "ReAssert (2020)", "keywords": ["ReAssert: Learning to Repair Broken Test Assertions", "ReAssert"]},
    {"id": "25", "name": "NUTS (2021)", "keywords": ["On Learning Meaningful Assert Statements for Unit Test Cases", "NUTS"]},
    {"id": "26", "name": "EDITAS (2023)", "keywords": ["Retrieve-and-Edit Assertion Generation", "EDITAS", "Yan"]},
    {"id": "27", "name": "Circe (2013)", "keywords": ["Grammar-Based Oracle for Web Application Security Testing", "Circe"]},
    {"id": "28", "name": "Metamorphic Sec Testing (2021)", "keywords": ["Metamorphic Security Testing for Web Systems", "Pastore", "TORACLE"]},
    {"id": "29", "name": "CodeSecEval (2024)", "keywords": ["Is Your AI-Generated Code Really Safe?", "CodeSecEval", "Wang"]},
    {"id": "30", "name": "Rigger (2022)", "keywords": ["Intramorphic Testing: A New Approach to the Test Oracle Problem", "Rigger", "A New Approach to the Test Oracle Problem"]},
    {"id": "31", "name": "Daikon (2007)", "keywords": ["The Daikon system for dynamic detection of likely invariants", "Daikon", "Ernst"]},
    {"id": "32", "name": "EvoSuite (2013)", "keywords": ["Whole Test Suite Generation", "EvoSuite", "Fraser", "Arcuri"]},
    {"id": "33", "name": "CyberSecEval (2023)", "keywords": ["CyberSecEval", "Purple Llama", "Bhatt"]}
]

# Map PDF files to paper catalog ID
pdf_files = glob.glob(os.path.join(SAVE_DIR, '*.pdf'))
pdf_text_map = {}

print(f"Parsing {len(pdf_files)} PDF files...")
for pdf_path in pdf_files:
    fname = os.path.basename(pdf_path)
    pid = fname.split('_')[0]
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
        pdf_text_map[pid] = {
            "filename": fname,
            "text": full_text
        }
        print(f"[PARSED] {pid}: {fname} ({len(reader.pages)} pages, {len(full_text)} chars)")
    except Exception as e:
        print(f"[ERROR] Parsing {fname}: {e}")

# Build Citation Matrix: Does Paper X cite Paper Y?
citation_matrix = {}
for src in paper_catalog:
    src_id = src['id']
    citation_matrix[src_id] = {}
    src_data = pdf_text_map.get(src_id)
    if not src_data:
        for tgt in paper_catalog:
            citation_matrix[src_id][tgt['id']] = "PDF_Missing"
        continue

    text = src_data['text']
    # Focus on reference section if possible, or full text
    ref_start = text.lower().rfind("references")
    ref_text = text[ref_start:] if ref_start != -1 else text

    for tgt in paper_catalog:
        tgt_id = tgt['id']
        if src_id == tgt_id:
            citation_matrix[src_id][tgt_id] = "Self"
            continue
        
        # Check matching keywords
        cited = False
        for kw in tgt['keywords']:
            if len(kw) > 3 and kw.lower() in ref_text.lower():
                cited = True
                break
        
        citation_matrix[src_id][tgt_id] = True if cited else False

# Write audit results
with open(os.path.join(SAVE_DIR, 'citation_matrix_result.json'), 'w', encoding='utf-8') as f:
    json.dump({
        "catalog": paper_catalog,
        "matrix": citation_matrix
    }, f, ensure_ascii=False, indent=2)

print("\n--- Empirical Citation Verification Matrix ---")
print("Format: [Source Paper ID] -> Citations Found:")
for src in paper_catalog:
    src_id = src['id']
    cited_list = [tgt_id for tgt_id, val in citation_matrix[src_id].items() if val is True]
    print(f"Paper {src_id} ({src['name']}): Cites -> {cited_list if cited_list else 'None found in PDF'}")

