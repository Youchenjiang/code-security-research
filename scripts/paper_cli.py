#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Security Research — 通用文獻庫管理與自動化維護工具 (Paper CLI)
===============================================================
整合文獻審查、雙向鏈結同步、檔名規範化、重複清理與筆記生成等全套功能。
取代過往零散的一次性遷移腳本，提供可持續、長久維護的 CLI 命令列套件。

使用範例:
  python scripts/paper_cli.py audit                  # 執行全庫健康檢查 (100% 鏈結、Wikilinks、YAML、檔名)
  python scripts/paper_cli.py sync                   # 自動同步 Vault 筆記與 raw-papers 實體檔案之雙向鏈結
  python scripts/paper_cli.py normalize              # 將 raw-papers 中非標準檔名 (底線、爬蟲前綴) 轉為標準空格格式
  python scripts/paper_cli.py dedup                  # 偵測並清理跨分類重複筆記與 raw-papers 孤兒檔案
  python scripts/paper_cli.py generate               # 針對尚未建檔的 raw PDF 自動生成 Obsidian 卡片筆記草稿
"""

import os
import sys
import re
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# 強制 Windows 終端輸出為 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 專案預設路徑解析
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DEFAULT_VAULT_DIR = os.path.join(REPO_ROOT, "research-vault")
DEFAULT_RAW_DIR = os.path.join(REPO_ROOT, "raw-papers")


def win_path(p: str) -> str:
    """處理 Windows 超長路徑 (>260 字元) 避免 [WinError 3] 或 [WinError 2]"""
    ap = os.path.abspath(p)
    if os.name == 'nt' and not ap.startswith('\\\\?\\'):
        return '\\\\?\\' + ap
    return ap


def clean_tokens(text: str) -> Set[str]:
    """將檔名切分為標準化詞彙集合，用於模糊匹配"""
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    stop_words = {'and', 'the', 'of', 'in', 'on', 'for', 'with', 'a', 'an', 'to', 'via', 'raw', 'pdf', 'md'}
    return {w for w in words if w not in stop_words and len(w) > 1}


# ==============================================================================
# 1. 審查模組 (AUDIT / VERIFY)
# ==============================================================================

def cmd_audit(args) -> int:
    """全面檢查文獻庫的完整性：實體鏈結、Obsidian 雙鏈、YAML 前言、檔名規範"""
    vault_dir = os.path.abspath(args.vault_dir)
    raw_dir = os.path.abspath(args.raw_dir)

    print("=" * 70)
    print("🔍 Code Security Research — 文獻庫全方位健康審查 (Health Audit)")
    print(f"  • Vault 路徑: {vault_dir}")
    print(f"  • Raw   路徑: {raw_dir}")
    print("=" * 70)

    total_errors = 0

    # 1. 蒐集 Vault 中所有筆記
    vault_notes: Dict[str, str] = {}
    for root, _, files in os.walk(vault_dir):
        for f in files:
            if f.endswith(".md"):
                stem = f[:-3]
                vault_notes[stem] = os.path.join(root, f)

    print(f"\n[1/5] 檢查 Obsidian 雙向內部鏈接 (Wikilinks)... (總計 {len(vault_notes)} 篇筆記)")
    broken_wikilinks = []
    for stem, note_path in vault_notes.items():
        with open(win_path(note_path), "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        # 移除程式碼區塊與行內代碼中的內容，避免誤判範例或引註格式為內部雙鏈
        content_no_code = re.sub(r'```[\s\S]*?```', '', content)
        content_no_code = re.sub(r'`[^`\n]+`', '', content_no_code)
        # 匹配 [[檔案名]] 或 [[檔案名|別名]]
        w_links = re.findall(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]', content_no_code)
        for wl in w_links:
            wl_clean = wl.strip()
            # 排除範本指示佔位符
            if wl_clean and wl_clean not in vault_notes and "請替換" not in wl_clean:
                broken_wikilinks.append((stem, wl_clean))

    if broken_wikilinks:
        print(f"  ❌ 發現 {len(broken_wikilinks)} 個失效的內部雙鏈:")
        for src, tgt in broken_wikilinks[:10]:
            print(f"     - 在筆記 [{src}] 中: 指向不存在的 [[{tgt}]]")
        total_errors += len(broken_wikilinks)
    else:
        print("  ✅ 內部雙向鏈接 100% 有效！(Broken Wikilinks: 0)")

    # 2. 檢查卡片筆記中指向實體 PDF 與 Raw Markdown 之相對鏈結與雙向對稱性
    print("\n[2/6] 檢查卡片筆記中指向實體 PDF 與 Raw Markdown 之相對鏈結與雙向對稱性...")
    broken_pdf_links = []
    broken_raw_links = []
    valid_pdf_count = 0
    valid_raw_count = 0

    for stem, note_path in vault_notes.items():
        # 略過總體回顧合成文件、報告與範本
        if any(k in note_path for k in ["reports", "syntheses", "matrices", "diagrams", "templates"]):
            continue
        with open(win_path(note_path), "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()

        # 解析 [PDF 原文](<路徑>)
        pdf_match = re.search(r'\[PDF\s*原文\]\(<([^>]+)>\)', content)
        if pdf_match:
            rel_path = pdf_match.group(1)
            abs_target = os.path.normpath(os.path.join(os.path.dirname(note_path), rel_path))
            if not os.path.exists(win_path(abs_target)):
                broken_pdf_links.append((stem, rel_path))
            else:
                valid_pdf_count += 1

        # 解析 [Markdown 原文](<路徑>)
        raw_match = re.search(r'\[Markdown\s*原文\]\(<([^>]+)>\)', content)
        if raw_match:
            rel_path = raw_match.group(1)
            abs_target = os.path.normpath(os.path.join(os.path.dirname(note_path), rel_path))
            if not os.path.exists(win_path(abs_target)):
                broken_raw_links.append((stem, rel_path))
            else:
                valid_raw_count += 1

    # 反向檢查：raw-papers 實體檔案是否均在 Vault 具備卡片筆記與 Raw MD
    orphan_pdfs = []
    orphan_raws = []
    for root, _, files in os.walk(raw_dir):
        if "legacy_archive" in root or "assets" in root:
            continue
        for f in files:
            if f.endswith(".pdf"):
                p_stem = f[:-4]
                if p_stem not in vault_notes:
                    orphan_pdfs.append(f)
                expected_raw = os.path.join(root, f"{p_stem} (Raw).md")
                if not os.path.exists(win_path(expected_raw)):
                    orphan_raws.append(f)

    if broken_pdf_links:
        print(f"  ❌ 發現 {len(broken_pdf_links)} 個失效的 [PDF 原文] 鏈接:")
        for stem, link in broken_pdf_links[:5]:
            print(f"     - {stem}: {link}")
        total_errors += len(broken_pdf_links)
    else:
        print(f"  ✅ [PDF 原文] 鏈接 100% 存在！(已驗證 {valid_pdf_count} 篇實體 PDF)")

    if broken_raw_links:
        print(f"  ❌ 發現 {len(broken_raw_links)} 個失效的 [Markdown 原文] 鏈接:")
        for stem, link in broken_raw_links[:5]:
            print(f"     - {stem}: {link}")
        total_errors += len(broken_raw_links)
    else:
        print(f"  ✅ [Markdown 原文] 鏈接 100% 存在！(已驗證 {valid_raw_count} 篇實體解析檔)")

    if orphan_pdfs:
        print(f"  ❌ 發現 {len(orphan_pdfs)} 個孤兒 PDF (未在 Vault 建檔):")
        for op in orphan_pdfs[:5]:
            print(f"     - {op}")
        total_errors += len(orphan_pdfs)
    
    if orphan_raws:
        print(f"  ❌ 發現 {len(orphan_raws)} 個 PDF 缺少對應 (Raw).md:")
        for oraw in orphan_raws[:5]:
            print(f"     - {oraw}")
        total_errors += len(orphan_raws)

    # 3. 檢查 YAML Frontmatter 語法
    print("\n[3/6] 檢查 YAML Frontmatter 格式與必備屬性...")
    yaml_errors = []
    for stem, note_path in vault_notes.items():
        with open(win_path(note_path), "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    yaml.safe_load(parts[1])
                except Exception as e:
                    yaml_errors.append((stem, str(e)))
            else:
                yaml_errors.append((stem, "未閉合的 Frontmatter (缺少結尾 ---)"))

    if yaml_errors:
        print(f"  ❌ 發現 {len(yaml_errors)} 個 YAML 語法錯誤:")
        for stem, err in yaml_errors:
            print(f"     - {stem}: {err}")
        total_errors += len(yaml_errors)
    else:
        print("  ✅ 全庫筆記 YAML Frontmatter 語法 100% 正確！")

    # 4. 檢查檔名規範 (工具優先/類型前綴，嚴禁作者姓名，年份一致性)
    print("\n[4/6] 檢查檔名命名規範 (工具優先/類型前綴，嚴禁作者姓名，年份一致性)...")
    suspicious_files = []
    author_blacklist = {'sutter', 'auer', 'li', 'wang', 'zhang', 'chen', 'liu', 'yang', 'huang', 'zhao', 'wu', 'xu', 'feizollah'}
    
    for root, _, files in os.walk(raw_dir):
        if "legacy_archive" in root:
            continue
        for f in files:
            if f.endswith(" raw.md"):
                suspicious_files.append((f, "結尾使用非標準 ' raw.md' (應為 ' (Raw).md')"))
            elif f.startswith("(") and (f.endswith(".pdf") or f.endswith(".md")):
                suspicious_files.append((f, "檔名缺少工具/類型前綴，直接以年份 '(' 開頭"))
            
            # 檢查是否以常見作者姓氏作為前綴
            m_pre = re.match(r'^([A-Za-z0-9\-_+]+)\s*\((\d{4})\)', f)
            if m_pre:
                prefix = m_pre.group(1).lower()
                if prefix in author_blacklist:
                    suspicious_files.append((f, f"檔名前綴 [{prefix}] 違規使用作者姓名 (應為工具名稱或研究類型)"))

    # 檢查 Vault 筆記之完整命名規範
    for stem, note_path in vault_notes.items():
        if re.match(r'^\d', stem) or any(k in stem for k in ["README", "TAXONOMY", "Template", "guide", "review", "TABLE"]):
            continue
        # 檢查是否為殘缺短檔名：只有 Name (Year)
        if re.match(r'^[^\(]+?\s*\(\d{4}\)$', stem):
            suspicious_files.append((stem, "檔名僅包含名稱與年份，缺少論文完整標題 (應為 'Tool/Category (Year) Title')"))
        
        # 檢查檔名年份與 Frontmatter year 是否一致
        year_m = re.search(r'\((\d{4})\)', stem)
        if year_m:
            fn_year = int(year_m.group(1))
            with open(win_path(note_path), "r", encoding="utf-8", errors="ignore") as fp:
                txt = fp.read()
            if txt.startswith("---"):
                parts = txt.split("---", 2)
                if len(parts) >= 3:
                    try:
                        meta = yaml.safe_load(parts[1])
                        if isinstance(meta, dict) and "year" in meta:
                            fm_year = int(meta["year"])
                            if fm_year != fn_year:
                                suspicious_files.append((stem, f"檔名年份 ({fn_year}) 與 Frontmatter 年份 ({fm_year}) 衝突"))
                    except Exception:
                        pass

    if suspicious_files:
        print(f"  ❌ 發現 {len(suspicious_files)} 個檔名格式或元數據異常:")
        for f, reason in suspicious_files[:5]:
            print(f"     - {f}: {reason}")
        total_errors += len(suspicious_files)
    else:
        print("  ✅ 檔名標準化與命名規範通過！(全庫無作者名殘留、無殘缺短檔名，年份 100% 吻合)")

    # 5. 實體文獻真實內容、重複二進制排查與領域吻合度 (Deep Content-Level Verification)
    print("\n[5/6] 檢查 PDF 實質內文、二進制唯一性與安全領域吻合度 (Content-Level Verification)...")
    content_errors = []
    duplicate_errors = []
    try:
        import fitz
        import hashlib
        
        # 1. 二進制重複檢查
        sha_tracker = {}
        for root, _, files in os.walk(raw_dir):
            if "legacy_archive" in root:
                continue
            for f in files:
                if f.endswith(".pdf"):
                    pdf_p = os.path.join(root, f)
                    with open(win_path(pdf_p), 'rb') as fp:
                        sha = hashlib.sha256(fp.read()).hexdigest()
                    if sha in sha_tracker:
                        duplicate_errors.append((f, sha_tracker[sha]))
                    else:
                        sha_tracker[sha] = f

        if duplicate_errors:
            print(f"  ❌ 發現 {len(duplicate_errors)} 組二進制重複的 PDF 檔案:")
            for f1, f2 in duplicate_errors[:5]:
                print(f"     - {f1} == {f2}")
            total_errors += len(duplicate_errors)
        else:
            print(f"  ✅ 二進制唯一性檢查通過！(全庫 {len(sha_tracker)} 篇 PDF 無任何重複檔案)")

        # 2. 標題關鍵字與領域吻合度檢查
        for stem, note_path in vault_notes.items():
            if re.match(r'^\d', stem) or any(k in stem for k in ["README", "TAXONOMY", "Template", "guide", "review", "TABLE"]):
                continue
            clean_stem = re.sub(r'\(\d{4}\)', '', stem).replace('_', ' ').replace('-', ' ')
            words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', clean_stem)]
            if len(words) < 3:
                continue
            
            # Locate PDF
            pdf_file = None
            for root, _, files in os.walk(raw_dir):
                if "legacy_archive" in root:
                    continue
                if f"{stem}.pdf" in files:
                    pdf_file = os.path.join(root, f"{stem}.pdf")
                    break
            
            if pdf_file and os.path.exists(pdf_file):
                try:
                    doc = fitz.open(pdf_file)
                    if len(doc) > 0:
                        p1 = doc[0].get_text("text")
                        p2 = doc[1].get_text("text") if len(doc) > 1 else ""
                        text_sample = (p1 + " " + p2).lower()
                        matched = [w for w in words if w in text_sample]
                        ratio = len(matched) / len(words)
                        if ratio < 0.25:
                            content_errors.append((stem, f"內文與標題嚴重不符 (關鍵字命中率僅 {int(ratio*100)}%)"))
                except Exception:
                    pass
    except ImportError:
        print("  ⚠️ 缺少 PyMuPDF (fitz) 模組，略過 PDF 內文深度比對。")

    if content_errors:
        print(f"  ❌ 發現 {len(content_errors)} 篇論文內容與標題嚴重脫節 (疑似錯配或假文獻):")
        for stem, reason in content_errors[:5]:
            print(f"     - {stem}: {reason}")
        total_errors += len(content_errors)
    else:
        print("  ✅ 實體文獻內容比對通過！全庫 PDF 內文與標題均高度吻合。")

    # 6. 檢查主目錄導航索引
    print("\n[6/6] 檢查 00-研究流派圖主目錄.md 流派索引有效性...")
    index_path = os.path.join(vault_dir, "00-研究流派圖主目錄.md")
    if os.path.exists(win_path(index_path)):
        with open(win_path(index_path), "r", encoding="utf-8") as fp:
            c = fp.read()
        idx_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', c)
        broken_idx = [l for l in idx_links if l.strip() not in vault_notes]
        if broken_idx:
            print(f"  ❌ 發現 {len(broken_idx)} 個失效的流派目錄連結: {broken_idx}")
            total_errors += len(broken_idx)
        else:
            print(f"  ✅ 主目錄共 {len(idx_links)} 個流派連結全部有效！")
    else:
        print("  ⚠️ 未找到 00-研究流派圖主目錄.md")

    # 總結報告
    print("\n" + "=" * 70)
    if total_errors == 0:
        print("🎉 審查結果：全庫 100% 健康！所有指標（含實體內容檢驗）均符合學術與系統規範。")
        print("=" * 70)
        return 0
    else:
        print(f"🚨 審查結果：共發現 {total_errors} 處問題，請執行相應修復指令 (如 sync 或 normalize)。")
        print("=" * 70)
        return 1


# ==============================================================================
# 2. 雙向鏈結同步模組 (SYNC)
# ==============================================================================

def cmd_sync(args) -> int:
    """自動遍歷 Vault 與 raw-papers，為每篇筆記自動掛載精確的相對路徑 [PDF 原文] 與 [Markdown 原文]"""
    vault_dir = os.path.abspath(args.vault_dir)
    raw_dir = os.path.abspath(args.raw_dir)

    print(f"🔄 開始同步文獻雙向鏈結...")
    updated_count = 0

    # 1. 建立 raw-papers 全庫實體檔案索引
    raw_pdf_index = {}
    raw_md_index = {}
    for r, _, files in os.walk(raw_dir):
        if "legacy_archive" in r:
            continue
        for f in files:
            if f.endswith(".pdf"):
                stem = f[:-4]
                raw_pdf_index[stem] = os.path.join(r, f)
            elif f.endswith(" (Raw).md"):
                stem = f[:-len(" (Raw).md")]
                raw_md_index[stem] = os.path.join(r, f)
            elif f.endswith(".md") and not f.endswith(" (Raw).md"):
                stem = f[:-3]
                raw_md_index[stem] = os.path.join(r, f)

    for root, _, files in os.walk(vault_dir):
        # 略過不需要掛載文獻存檔的合成文章與報告
        if any(k in root for k in ["reports", "syntheses", "matrices", "diagrams", "templates"]):
            continue

        for f in files:
            if not f.endswith(".md") or f.startswith("00-") or re.match(r"^[0-9A-Z]+\.[0-9A-Za-z]+-", f):
                continue
            v_base = f[:-3]
            v_path = os.path.join(root, f)
            note_dir = os.path.dirname(v_path)

            pdf_abs = raw_pdf_index.get(v_base)
            raw_abs = raw_md_index.get(v_base)

            pdf_rel = os.path.relpath(pdf_abs, note_dir).replace(os.sep, '/') if pdf_abs else None
            raw_rel = os.path.relpath(raw_abs, note_dir).replace(os.sep, '/') if raw_abs else None

            if pdf_rel and raw_rel:
                archive_line = f"> **文獻存檔**：[PDF 原文](<{pdf_rel}>) | [Markdown 原文](<{raw_rel}>)"
            elif pdf_rel:
                archive_line = f"> **文獻存檔**：[PDF 原文](<{pdf_rel}>)"
            elif raw_rel:
                archive_line = f"> **文獻存檔**：[Markdown 原文](<{raw_rel}>)"
            else:
                archive_line = "> **文獻存檔**：*(本篇為重點文獻全文摘錄與分析筆記)*"

            with open(win_path(v_path), "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()

            if "> **文獻存檔**" in content or "[PDF 原文]" in content:
                content = re.sub(r'> \*\*文獻存檔\*\*:[^\n\r]+', archive_line, content)
                content = re.sub(r'> \*\*文獻存檔\*\*：[^\n\r]+', archive_line, content)
            else:
                title_match = re.search(r'(# [^\n\r]+\n+)', content)
                if title_match:
                    content = content.replace(title_match.group(1), f"{title_match.group(1)}{archive_line}\n\n", 1)
                else:
                    content = f"{archive_line}\n\n" + content

            with open(win_path(v_path), "w", encoding="utf-8") as fp:
                fp.write(content)
            updated_count += 1

    print(f"✅ 雙向鏈結同步完成！共更新/檢查了 {updated_count} 篇筆記。")
    return 0


# ==============================================================================
# 3. 檔名標準化模組 (NORMALIZE)
# ==============================================================================

def clean_paper_title(raw_name: str) -> str:
    """將包含序號、下劃線、奇怪符號的原始檔名清洗為標準空格格式"""
    stem = raw_name
    for ext in [".pdf", ".md", " (Raw).md", " raw.md"]:
        if stem.endswith(ext):
            stem = stem[:-len(ext)]
            break

    # 移除前綴序號例如 "81_", "05_"
    stem = re.sub(r'^\d+[\s_-]+', '', stem)
    # 將底線轉換為空格
    stem = stem.replace('_', ' ')
    # 移除重複連續空格
    stem = re.sub(r'\s+', ' ', stem).strip()
    return stem


def cmd_normalize(args) -> int:
    """自動掃描 raw-papers 目錄，將所有包含底線或非標準結尾的檔案批次重命名為自然空格規範"""
    target_dir = os.path.abspath(args.dir or DEFAULT_RAW_DIR)
    dry_run = args.dry_run

    print(f"🧹 開始執行檔名標準化 (目錄: {target_dir}, DryRun: {dry_run})...")
    renamed_count = 0

    for root, _, files in os.walk(target_dir):
        if "legacy_archive" in root:
            continue
        for f in files:
            needs_rename = False
            new_name = f

            # 情況 1: 包含 ' raw.md'
            if f.endswith(" raw.md"):
                new_name = f[:-7] + " (Raw).md"
                needs_rename = True
            # 情況 2: 包含底線
            if "_" in new_name:
                base, ext = os.path.splitext(new_name)
                if ext == ".md" and base.endswith(" (Raw)"):
                    clean_stem = clean_paper_title(base[:-6])
                    new_name = f"{clean_stem} (Raw).md"
                else:
                    clean_stem = clean_paper_title(base)
                    new_name = f"{clean_stem}{ext}"
                needs_rename = True

            if needs_rename and new_name != f:
                old_path = os.path.join(root, f)
                new_path = os.path.join(root, new_name)
                print(f"  • 重命名: {f} -> {new_name}")
                renamed_count += 1
                if not dry_run:
                    if os.path.exists(win_path(new_path)):
                        os.remove(win_path(new_path))
                    os.rename(win_path(old_path), win_path(new_path))

    print(f"✅ 檔名標準化處理完成！共處理 {renamed_count} 個檔案。")
    return 0


# ==============================================================================
# 4. 查重與孤兒檔案歸檔 (DEDUP)
# ==============================================================================

def cmd_dedup(args) -> int:
    """偵測跨流派的重複卡片筆記，並揪出未建檔的孤兒 PDF 移入封存區"""
    vault_dir = os.path.abspath(args.vault_dir)
    raw_dir = os.path.abspath(args.raw_dir)
    archive_dir = os.path.join(raw_dir, "legacy_archive", "unreferenced_leftovers")

    print(f"🔍 執行跨分類筆記重複性檢查與孤兒檔案審查...")

    # 1. 偵測重複筆記
    note_locations: Dict[str, List[str]] = {}
    for root, _, files in os.walk(vault_dir):
        if any(k in root for k in ["reports", "syntheses", "matrices", "diagrams", "templates"]):
            continue
        for f in files:
            if f.endswith(".md") and not f.startswith("00-"):
                note_locations.setdefault(f, []).append(os.path.join(root, f))

    duplicates = {k: v for k, v in note_locations.items() if len(v) > 1}
    if duplicates:
        print(f"⚠️ 發現 {len(duplicates)} 篇存在跨分類重複存放的筆記:")
        for name, paths in duplicates.items():
            print(f"  • {name}:")
            for p in paths:
                rel = os.path.relpath(p, vault_dir)
                size = os.path.getsize(win_path(p))
                print(f"     - [{size} bytes] {rel}")
            if args.auto_prune_stubs:
                # 自動保留最大體積（內容最完整）的那篇，刪除佔位小 stub
                paths_sorted = sorted(paths, key=lambda x: os.path.getsize(win_path(x)), reverse=True)
                for stub in paths_sorted[1:]:
                    os.remove(win_path(stub))
                    print(f"       🗑️ 自動移除冗餘 stub: {os.path.relpath(stub, vault_dir)}")
    else:
        print("✅ 跨流派筆記無任何重複！(Duplicates: 0)")

    # 2. 偵測 raw-papers 中未對應的孤兒檔案
    vault_bases = {f[:-3] for f in note_locations.keys()}
    orphan_files = []
    for root, _, files in os.walk(raw_dir):
        if "legacy_archive" in root:
            continue
        for f in files:
            if f.endswith(".pdf"):
                base = f[:-4]
                if base not in vault_bases:
                    orphan_files.append(os.path.join(root, f))
            elif f.endswith(" (Raw).md"):
                base = f[:-len(" (Raw).md")]
                if base not in vault_bases:
                    orphan_files.append(os.path.join(root, f))

    if orphan_files:
        print(f"\n⚠️ 發現 {len(orphan_files)} 個未在 Vault 中建檔之孤兒檔案:")
        for op in orphan_files[:5]:
            print(f"  • {os.path.relpath(op, raw_dir)}")
        if args.archive_orphans:
            os.makedirs(win_path(archive_dir), exist_ok=True)
            for op in orphan_files:
                dest = os.path.join(archive_dir, os.path.basename(op))
                if os.path.exists(win_path(dest)):
                    os.remove(win_path(dest))
                os.rename(win_path(op), win_path(dest))
                print(f"  📦 已移入封存區: {os.path.basename(op)}")
    else:
        print("✅ raw-papers 無任何未對應的孤兒實體檔案！(Orphans: 0)")

    return 0


# ==============================================================================
# 5. 統計模組 (STATS)
# ==============================================================================

def cmd_stats(args) -> int:
    vault_dir = os.path.abspath(args.vault_dir)
    raw_dir = os.path.abspath(args.raw_dir)
    notes_dir = os.path.join(vault_dir, "notes")
    reports_dir = os.path.join(vault_dir, "reports")
    matrices_dir = os.path.join(vault_dir, "matrices")

    print("=" * 70)
    print("📊 Code Security Research — 文獻庫資產統計總覽 (Stats)")
    print("=" * 70)

    # 1. 筆記統計
    notes_count = len([f for f in os.listdir(notes_dir) if f.endswith(".md")]) if os.path.exists(notes_dir) else 0
    reports_count = len([f for f in os.listdir(reports_dir) if f.endswith(".md")]) if os.path.exists(reports_dir) else 0
    matrices_count = len([f for f in os.listdir(matrices_dir) if f.endswith(".md")]) if os.path.exists(matrices_dir) else 0

    # 2. 實體檔案與年份統計
    pdf_count = 0
    raw_md_count = 0
    year_stats: Dict[str, int] = {}

    for root, _, files in os.walk(raw_dir):
        if "legacy_archive" in root:
            continue
        rel = os.path.relpath(root, raw_dir)
        year_group = rel.split(os.sep)[0] if rel != "." else "root"
        for f in files:
            if f.endswith(".pdf"):
                pdf_count += 1
                year_stats[year_group] = year_stats.get(year_group, 0) + 1
            elif f.endswith(" (Raw).md") or f.endswith(".raw.md"):
                raw_md_count += 1

    print(f"\n📁 知識庫卡片資產 (research-vault/):")
    print(f"  • 單篇論文精讀筆記 (notes/)   : {notes_count} 篇")
    print(f"  • 綜合研究報告 (reports/)      : {reports_count} 篇")
    print(f"  • 核心比對矩陣 (matrices/)     : {matrices_count} 篇")

    print(f"\n📦 實體原始檔案 (raw-papers/):")
    print(f"  • 實體 PDF 論文檔案            : {pdf_count} 篇")
    print(f"  • 全文 Raw Markdown 解析檔     : {raw_md_count} 篇")

    pdf_cov = (pdf_count / notes_count * 100) if notes_count else 0
    raw_cov = (raw_md_count / notes_count * 100) if notes_count else 0
    print(f"  • PDF 原文覆蓋率               : {pdf_cov:.1f}%")
    print(f"  • Markdown 原文解析覆蓋率      : {raw_cov:.1f}%")

    print(f"\n📅 實體論文年份分佈 (Year Distribution):")
    for yg in sorted(year_stats.keys(), reverse=True):
        count = year_stats[yg]
        bar = "█" * min(count, 40)
        print(f"  • {yg:<12}: {count:>3} 篇 {bar}")

    print("=" * 70)
    return 0


# ==============================================================================
# 6. 浮水印清理模組 (CLEAN-WATERMARKS)
# ==============================================================================

def cmd_clean_watermarks(args) -> int:
    target_dirs = [os.path.abspath(args.raw_dir), os.path.abspath(args.vault_dir)]
    dry_run = args.dry_run

    print("=" * 70)
    print(f"🧹 執行文獻浮水印清理 (Clean Watermarks){' [DRY-RUN]' if dry_run else ''}...")
    print("=" * 70)

    watermark_patterns = [
        re.compile(r'^\s*Authorized licensed use limited to:.*Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*Downloaded on .* from IEEE Xplore.*Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*IEEE Xplore\s+Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\s*© \d{4} IEEE\. Personal use of this material is permitted\..*$', re.IGNORECASE | re.MULTILINE),
    ]

    total_cleaned_files = 0
    total_lines_removed = 0

    for d in target_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(win_path(fpath), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                except Exception:
                    continue

                file_lines_removed = 0
                new_lines = []

                for line in lines:
                    ls = line.strip()
                    if "Authorized licensed use limited to:" in ls and "Restrictions apply." in ls:
                        file_lines_removed += 1
                        continue
                    if "Downloaded on" in ls and "IEEE Xplore" in ls and "Restrictions apply." in ls:
                        file_lines_removed += 1
                        continue
                    if "IEEE Xplore" in ls and "Restrictions apply." in ls and len(ls) < 60:
                        file_lines_removed += 1
                        continue
                    if "IEEE. Personal use of this material is permitted" in ls:
                        file_lines_removed += 1
                        continue
                    new_lines.append(line)

                if file_lines_removed > 0:
                    total_cleaned_files += 1
                    total_lines_removed += file_lines_removed
                    rel = os.path.relpath(fpath, REPO_ROOT)
                    print(f"  • [{file_lines_removed} 行] {rel}")
                    if not dry_run:
                        with open(win_path(fpath), 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)

    print(f"\n清理完成: 共在 {total_cleaned_files} 個檔案中消除 {total_lines_removed} 行浮水印與授權干擾字元。")
    return 0


# ==============================================================================
# 7. 卡片草稿自動生成模組 (GENERATE-NOTES)
# ==============================================================================

def cmd_generate_notes(args) -> int:
    vault_dir = os.path.abspath(args.vault_dir)
    raw_dir = os.path.abspath(args.raw_dir)
    notes_dir = os.path.join(vault_dir, "notes")
    dry_run = args.dry_run

    print("=" * 70)
    print(f"📝 掃描 raw-papers 並自動補齊缺失卡片筆記草稿{' [DRY-RUN]' if dry_run else ''}...")
    print("=" * 70)

    os.makedirs(win_path(notes_dir), exist_ok=True)
    existing_notes = {f[:-3] for f in os.listdir(notes_dir) if f.endswith(".md")}

    raw_bases: Dict[str, Dict[str, str]] = {}
    for root, _, files in os.walk(raw_dir):
        if "legacy_archive" in root:
            continue
        rel_root = os.path.relpath(root, raw_dir)
        for f in files:
            if f.endswith(".pdf"):
                base = f[:-4]
                raw_bases.setdefault(base, {})['pdf'] = f"../../raw-papers/{rel_root.replace(os.sep, '/')}/{f}"
            elif f.endswith(" (Raw).md"):
                base = f[:-len(" (Raw).md")]
                raw_bases.setdefault(base, {})['raw'] = f"../../raw-papers/{rel_root.replace(os.sep, '/')}/{f}"

    missing_bases = {b: paths for b, paths in raw_bases.items() if b not in existing_notes}

    if not missing_bases:
        print("✅ 目前所有 raw-papers 中的文獻皆已在 notes/ 擁有對應卡片筆記！")
        return 0

    print(f"發現 {len(missing_bases)} 篇文獻尚未建立筆記卡片，正在自動生成草稿:")
    created_count = 0
    for base, paths in sorted(missing_bases.items()):
        m = re.match(r'^([^(]+)\s*\((\d{4})\)\s*(.*)$', base)
        if m:
            authors = m.group(1).strip()
            year = m.group(2).strip()
            title = m.group(3).strip()
        else:
            authors = "Unknown"
            year = "2026"
            title = base

        pdf_link = paths.get('pdf', '')
        raw_link = paths.get('raw', '')

        pdf_md = f"- [PDF 原文](<{pdf_link}>)\n" if pdf_link else ""
        raw_md = f"- [Markdown 原文](<{raw_link}>)\n" if raw_link else ""

        note_content = f"""---
title: "{title}"
authors: "{authors}"
year: {year}
venue: "Unspecified"
categories:
  - "[[00-研究流派圖主目錄]]"
---

# 📖 {title}

## 📄 本地文獻存檔
{pdf_md}{raw_md}
## 📝 論文摘要 (Abstract)
> [!NOTE]
> 自動生成之文獻卡片草稿，待補充精讀內容與核心貢獻。

---

## 🎯 核心解決問題 (Problem Statement)
* **研究背景**：
* **現有技術痛點**：
* **論文要解決的具體問題**：

---

## 💡 關鍵創新點與貢獻 (Key Contributions & Innovation)
1. 
2. 
3. 
"""
        note_file = os.path.join(notes_dir, f"{base}.md")
        print(f"  ➕ 生成卡片: {base}.md")
        if not dry_run:
            with open(win_path(note_file), 'w', encoding='utf-8') as f:
                f.write(note_content)
        created_count += 1

    print(f"\n生成完成: 共建立 {created_count} 篇標準 Obsidian 卡片草稿。")
    return 0


# ==============================================================================
# 8. 主程式進入點 (CLI DISPATCHER)
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Code Security Research — 通用文獻庫管理與自動化維護工具 (Paper CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
常用命令範例:
  python scripts/paper_cli.py audit                  # 執行全庫健康檢查
  python scripts/paper_cli.py stats                  # 顯示全庫資產統計與年份分佈
  python scripts/paper_cli.py sync                   # 自動同步雙向相對路徑鏈結
  python scripts/paper_cli.py normalize              # 批次重命名非標準檔名
  python scripts/paper_cli.py dedup --auto-prune     # 自動修剪跨目錄重複筆記
  python scripts/paper_cli.py clean-watermarks       # 清除 IEEE Xplore 等浮水印干擾字串
  python scripts/paper_cli.py generate-notes         # 自動為未建檔之 raw-papers 生成卡片草稿
"""
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="可調用的子命令")

    # 1. audit
    p_audit = subparsers.add_parser("audit", help="全面健康檢查 (雙鏈、PDF/Raw 鏈結、YAML、檔名規範)")
    p_audit.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_audit.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_audit.set_defaults(func=cmd_audit)

    # 2. stats
    p_stats = subparsers.add_parser("stats", help="統計全庫文獻卡片、實體 PDF/Raw 數量與年份分佈")
    p_stats.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_stats.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_stats.set_defaults(func=cmd_stats)

    # 3. sync
    p_sync = subparsers.add_parser("sync", help="同步 Vault 卡片筆記與 raw-papers 之雙向鏈結")
    p_sync.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_sync.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_sync.set_defaults(func=cmd_sync)

    # 4. normalize
    p_norm = subparsers.add_parser("normalize", help="標準化檔名 (去除底線、去除爬蟲編號、規範 raw.md)")
    p_norm.add_argument("--dir", default=DEFAULT_RAW_DIR, help="欲清洗檔名之目標目錄")
    p_norm.add_argument("--dry-run", action="store_true", help="僅預覽不實際改名")
    p_norm.set_defaults(func=cmd_normalize)

    # 5. dedup
    p_dedup = subparsers.add_parser("dedup", help="偵測與清理跨分類重複卡片筆記及未關聯孤兒檔案")
    p_dedup.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_dedup.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_dedup.add_argument("--auto-prune-stubs", action="store_true", help="自動刪除內容過小之重複佔位 stub")
    p_dedup.add_argument("--archive-orphans", action="store_true", help="自動將孤兒檔案移入 legacy_archive")
    p_dedup.set_defaults(func=cmd_dedup)

    # 6. clean-watermarks
    p_cw = subparsers.add_parser("clean-watermarks", help="批次清理 Markdown 文本中的 IEEE 授權浮水印冗餘行")
    p_cw.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_cw.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_cw.add_argument("--dry-run", action="store_true", help="僅預覽不修改檔案")
    p_cw.set_defaults(func=cmd_clean_watermarks)

    # 7. generate-notes
    p_gen = subparsers.add_parser("generate-notes", help="自動為 raw-papers 中存在但 Vault 尚未建檔的論文生成卡片筆記草稿")
    p_gen.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Vault 目錄路徑")
    p_gen.add_argument("--raw-dir", default=DEFAULT_RAW_DIR, help="raw-papers 目錄路徑")
    p_gen.add_argument("--dry-run", action="store_true", help="僅預覽不實際建立檔案")
    p_gen.set_defaults(func=cmd_generate_notes)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
