import os
import glob
import re
import json
import shutil

REPO_ROOT = "code-security-research"
RAW_PAPERS_DIR = os.path.join(REPO_ROOT, "raw-papers")
NOTES_DIR = os.path.join(REPO_ROOT, "research-vault", "notes")
VAULT_DIR = os.path.join(REPO_ROOT, "research-vault")
PLAN_FILE = "scratch/master_rename_plan.json"

def run_master_migration():
    print("======================================================================")
    print("[*] Starting Master Renaming Migration for 154 Papers (Rule A)")
    print("======================================================================\n")

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        master_plan = json.load(f)

    print(f"Loaded {len(master_plan)} paper rename rules from {PLAN_FILE}\n")

    pdf_renamed = 0
    raw_md_renamed = 0
    assets_renamed = 0
    notes_renamed = 0

    # Step 1: Rename PDF, Raw Markdown, and Assets folders
    print("[1/4] Renaming Physical PDFs, Raw Markdowns, and Asset Folders...")
    for old_base, new_base in master_plan.items():
        if old_base == new_base:
            continue

        # Extract year from new_base: e.g. "TaintDroid (2010)..." -> "2010"
        m_new_yr = re.search(r"\((\d{4})\)", new_base)
        new_year = m_new_yr.group(1) if m_new_yr else None

        # Find matching PDF in raw-papers
        pdf_matches = [
            p for p in glob.glob(f"{RAW_PAPERS_DIR}/**/{old_base}.pdf", recursive=True)
            if "legacy_archive" not in p
        ]
        for old_pdf in pdf_matches:
            cur_dir = os.path.dirname(old_pdf)
            target_dir = cur_dir
            if new_year and os.path.basename(cur_dir).isdigit() and os.path.basename(cur_dir) != new_year:
                target_dir = os.path.join(RAW_PAPERS_DIR, new_year)
                os.makedirs(target_dir, exist_ok=True)
            new_pdf = os.path.join(target_dir, f"{new_base}.pdf")
            if old_pdf != new_pdf:
                if os.path.exists(new_pdf):
                    os.remove(new_pdf)
                shutil.move(old_pdf, new_pdf)
                pdf_renamed += 1

        # Find matching Raw Markdown in raw-papers
        raw_md_matches = [
            p for p in glob.glob(f"{RAW_PAPERS_DIR}/**/{old_base} (Raw).md", recursive=True)
            if "legacy_archive" not in p
        ]
        for old_raw_md in raw_md_matches:
            cur_dir = os.path.dirname(old_raw_md)
            target_dir = cur_dir
            if new_year and os.path.basename(cur_dir).isdigit() and os.path.basename(cur_dir) != new_year:
                target_dir = os.path.join(RAW_PAPERS_DIR, new_year)
                os.makedirs(target_dir, exist_ok=True)
            new_raw_md = os.path.join(target_dir, f"{new_base} (Raw).md")
            if old_raw_md != new_raw_md:
                if os.path.exists(new_raw_md):
                    os.remove(new_raw_md)
                shutil.move(old_raw_md, new_raw_md)
                raw_md_renamed += 1

        # Check and rename assets folder if exists
        old_asset_dir = os.path.join(RAW_PAPERS_DIR, "assets", old_base)
        new_asset_dir = os.path.join(RAW_PAPERS_DIR, "assets", new_base)
        if os.path.exists(old_asset_dir):
            if os.path.exists(new_asset_dir) and old_asset_dir != new_asset_dir:
                shutil.rmtree(new_asset_dir)
            shutil.move(old_asset_dir, new_asset_dir)
            assets_renamed += 1

    print(f"  [OK] PDFs Renamed: {pdf_renamed}")
    print(f"  [OK] Raw Markdowns Renamed: {raw_md_renamed}")
    print(f"  [OK] Assets Folders Renamed: {assets_renamed}\n")

    # Step 2: Rename Notes in research-vault/notes and update internal references
    print("[2/4] Renaming and Updating Research Notes...")
    for old_base, new_base in master_plan.items():
        if old_base == new_base:
            continue

        old_note = os.path.join(NOTES_DIR, f"{old_base}.md")
        new_note = os.path.join(NOTES_DIR, f"{new_base}.md")

        if os.path.exists(old_note):
            with open(old_note, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Update title header: e.g. # old_base -> # new_base
            content = re.sub(
                rf"^#\s+{re.escape(old_base)}",
                f"# {new_base}",
                content,
                flags=re.MULTILINE
            )

            # Update source in YAML: source: "old_base.pdf" -> source: "new_base.pdf"
            content = re.sub(
                rf'source:\s*"{re.escape(old_base)}\.pdf"',
                f'source: "{new_base}.pdf"',
                content
            )

            # Update links to PDF / Raw Markdown in note
            # Find the new PDF path to build exact relative link
            new_pdf_matches = glob.glob(f"{RAW_PAPERS_DIR}/**/{new_base}.pdf", recursive=True)
            if new_pdf_matches:
                rel_pdf = os.path.relpath(new_pdf_matches[0], NOTES_DIR).replace("\\", "/")
                content = re.sub(
                    r"\[PDF 原文\]\(<[^>]+>\)",
                    f"[PDF 原文](<{rel_pdf}>)",
                    content
                )
                content = re.sub(
                    r"\[PDF 原文\]\([^)]+\)",
                    f"[PDF 原文](<{rel_pdf}>)",
                    content
                )

            new_raw_matches = glob.glob(f"{RAW_PAPERS_DIR}/**/{new_base} (Raw).md", recursive=True)
            if new_raw_matches:
                rel_raw = os.path.relpath(new_raw_matches[0], NOTES_DIR).replace("\\", "/")
                content = re.sub(
                    r"\[Markdown 原文\]\(<[^>]+>\)",
                    f"[Markdown 原文](<{rel_raw}>)",
                    content
                )
                content = re.sub(
                    r"\[Markdown 原文\]\([^)]+\)",
                    f"[Markdown 原文](<{rel_raw}>)",
                    content
                )

            # Write updated content to new_note
            with open(new_note, "w", encoding="utf-8") as f:
                f.write(content)

            if old_note != new_note and os.path.exists(old_note):
                os.remove(old_note)

            notes_renamed += 1

    print(f"  [OK] Research Notes Renamed & Internal Links Updated: {notes_renamed}\n")

    # Step 3: Rewrite all Wikilinks in research-vault
    print("[3/4] Rewriting Wikilinks across entire Vault...")
    all_vault_mds = glob.glob(f"{VAULT_DIR}/**/*.md", recursive=True)
    links_rewritten = 0

    # Sort substitutions by length of old_base descending to avoid prefix collision
    substitutions = sorted(
        [(k, v) for k, v in master_plan.items() if k != v],
        key=lambda x: len(x[0]),
        reverse=True
    )

    for md_path in all_vault_mds:
        with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        orig_text = text
        for old_base, new_base in substitutions:
            # Replace [[old_base]] -> [[new_base]]
            text = re.sub(
                rf"\[\[{re.escape(old_base)}\]\]",
                f"[[{new_base}]]",
                text
            )
            # Replace [[old_base|alias]] -> [[new_base|alias]]
            text = re.sub(
                rf"\[\[{re.escape(old_base)}\|([^\]]+)\]\]",
                rf"[[{new_base}|\1]]",
                text
            )

        if text != orig_text:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(text)
            links_rewritten += 1

    print(f"  [OK] Markdown files with rewritten Wikilinks: {links_rewritten}\n")

    # Step 4: Also update Raw Markdown internal image references if assets dir was renamed
    print("[4/4] Updating Raw Markdown image asset references...")
    all_raw_mds = glob.glob(f"{RAW_PAPERS_DIR}/**/*.md", recursive=True)
    raw_img_links_updated = 0
    for raw_md in all_raw_mds:
        with open(raw_md, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        orig_text = text
        for old_base, new_base in substitutions:
            if f"../assets/{old_base}/" in text:
                text = text.replace(f"../assets/{old_base}/", f"../assets/{new_base}/")
            if f"assets/{old_base}/" in text:
                text = text.replace(f"assets/{old_base}/", f"assets/{new_base}/")
        if text != orig_text:
            with open(raw_md, "w", encoding="utf-8") as f:
                f.write(text)
            raw_img_links_updated += 1
    print(f"  [OK] Raw Markdown files with updated image links: {raw_img_links_updated}\n")

    print("======================================================================")
    print("[SUCCESS] Master Migration Finished Successfully!")
    print("======================================================================")

if __name__ == "__main__":
    run_master_migration()
