import os
import sys
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
CHABLE = os.path.join(REPO, "chable")
VAULT_SYN = os.path.join(REPO, "research-vault", "syntheses")
LEGACY = os.path.join(REPO, "raw-papers", "legacy_archive")
SCRIPTS = os.path.join(REPO, "scripts")
CASE_STUDIES = os.path.join(REPO, "case-studies", "chable-business-empire")

os.makedirs(VAULT_SYN, exist_ok=True)
os.makedirs(LEGACY, exist_ok=True)
os.makedirs(CASE_STUDIES, exist_ok=True)

# 1. Academic syntheses to research-vault/syntheses/
syn_files = {
    "Android動態測試工具完整清單.md": "Android安全測試完整工具清單.md",
    "Android動態測試框架研究.md": "Android動態測試框架完整研究報告.md",
    "滲透測試方法論.md": "移動端後端滲透測試方法論.md",
    "三年度計畫整合與架構設計.md": "三年度計畫整合與架構設計.md",
    "Android_NonDAST_Papers.md": "Android安全相關論文-非DAST.md",
    "Android動態測試學術論文與研究資源.md": "Android動態測試學術論文與研究資源.md"
}

for src_name, dst_name in syn_files.items():
    src = os.path.join(CHABLE, src_name)
    if os.path.exists(src):
        dst = os.path.join(VAULT_SYN, dst_name)
        shutil.move(src, dst)
        print(f"Moved to syntheses: {src_name} -> {dst_name}")

# 2. Legacy draft to raw-papers/legacy_archive/
v13_src = os.path.join(CHABLE, "Android App 滲透測試 13.md")
if os.path.exists(v13_src):
    v13_dst = os.path.join(LEGACY, "Android_App_滲透測試_v13_draft.md")
    shutil.move(v13_src, v13_dst)
    print("Moved to legacy archive: Android App 滲透測試 13.md")

# 3. Scripts to scripts/
script_moves = {
    "dast": os.path.join(SCRIPTS, "dast_poc"),
    "bot": os.path.join(SCRIPTS, "api_bot"),
    "_tools": os.path.join(SCRIPTS, "tools")
}

for src_dir, dst_dir in script_moves.items():
    src = os.path.join(CHABLE, src_dir)
    if os.path.exists(src):
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        shutil.move(src, dst_dir)
        print(f"Moved directory: {src_dir} -> scripts/{os.path.basename(dst_dir)}")

# Move small helper script files
tools_legacy = os.path.join(SCRIPTS, "tools", "legacy")
os.makedirs(tools_legacy, exist_ok=True)
for f in ["_append.js", "_make_append.py", "1.txt"]:
    src = os.path.join(CHABLE, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(tools_legacy, f))
        print(f"Moved helper script: {f} -> scripts/tools/legacy/")

# 4. Move all remaining case-study files and dirs to case-studies/chable-business-empire/
if os.path.exists(CHABLE):
    remaining = os.listdir(CHABLE)
    for item in remaining:
        src = os.path.join(CHABLE, item)
        dst = os.path.join(CASE_STUDIES, item)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
        print(f"Moved case study item: {item} -> case-studies/chable-business-empire/")

    # Remove empty chable directory
    try:
        os.rmdir(CHABLE)
        print("Successfully removed empty chable directory!")
    except Exception as e:
        print(f"Note on chable dir: {e}")

print("\nReorganization of chable successfully completed!")
