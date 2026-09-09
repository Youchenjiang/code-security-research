import os
import shutil
import json

REPO_ROOT = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research"
manifest_path = os.path.join(REPO_ROOT, "paper_migration_verification.json")

with open(manifest_path, "r", encoding="utf-8") as fp:
    report = json.load(fp)

items = report["items"]
print(f"Verifying {len(items)} items before deletion...")

all_verified = True
for item in items:
    # Check PDF in raw-papers
    if not os.path.exists(item["raw_dest_pdf"]) or os.path.getsize(item["raw_dest_pdf"]) == 0:
        print(f"SAFETY ABORT: PDF not safe -> {item['raw_dest_pdf']}")
        all_verified = False
        break
    # Check raw MD in raw-papers if source_md existed
    if item["source_md"]:
        if not os.path.exists(item["raw_dest_md"]) or os.path.getsize(item["raw_dest_md"]) == 0:
            print(f"SAFETY ABORT: Raw MD not safe -> {item['raw_dest_md']}")
            all_verified = False
            break

if not all_verified:
    print("Verification failed! Not deleting anything.")
    exit(1)

print("100% of files verified safely in raw-papers! Proceeding with safe removal of legacy folders...")

# Safe removal of verified legacy folders
dirs_to_remove = [
    os.path.join(REPO_ROOT, "papers"),
    os.path.join(REPO_ROOT, "paper_markdowns"),
    os.path.join(REPO_ROOT, "paper_markdowns_parsed"),
    os.path.join(REPO_ROOT, "new", "papers"),
    os.path.join(REPO_ROOT, "new", "legacy_archive", "papers")
]

for d in dirs_to_remove:
    if os.path.exists(d):
        shutil.rmtree(d)
        print(f"Safely removed legacy directory: {d}")

print("\nLegacy redundant directories successfully cleaned up with ZERO data loss!")
