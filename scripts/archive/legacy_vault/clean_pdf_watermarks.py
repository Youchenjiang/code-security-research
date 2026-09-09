import os
import re

directories = ['paper_markdowns', 'research-vault/papers']

watermark_patterns = [
    re.compile(r'^\s*Authorized licensed use limited to:.*Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*Downloaded on .* from IEEE Xplore.*Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*IEEE Xplore\s+Restrictions apply\.\s*$', re.IGNORECASE | re.MULTILINE)
]

total_cleaned = 0
total_lines_removed = 0

for d in directories:
    if not os.path.exists(d):
        continue
    for fname in os.listdir(d):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(d, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original_content = content
        lines_removed_in_file = 0

        for pat in watermark_patterns:
            matches = pat.findall(content)
            if matches:
                lines_removed_in_file += len(matches)
                content = pat.sub('', content)

        # Clean up multi-empty lines resulting from removals
        content = re.sub(r'\n{3,}', '\n\n', content)

        if content != original_content:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_cleaned += 1
            total_lines_removed += lines_removed_in_file
            print(f"Cleaned {lines_removed_in_file} watermark lines in [{d}]: {fname}")

print(f"\nDone! Cleaned {total_lines_removed} watermark lines across {total_cleaned} files.")
