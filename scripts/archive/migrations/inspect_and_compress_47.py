import re
import os

file_path = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\47_Intent_Redirection.md"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print(f"Total characters: {len(text):,}")

matches = list(re.finditer(r'!\[(.*?)\]\((data:image/([a-zA-Z]+);base64,([^\)]+))\)', text))
print(f"Found {len(matches)} base64 images!")

total_b64_bytes = 0
for i, m in enumerate(matches):
    alt = m.group(1)
    fmt = m.group(3)
    b64_str = m.group(4)
    size_approx = len(b64_str) * 3 // 4
    total_b64_bytes += size_approx
    print(f"Image {i+1}: format={fmt}, approx binary size={size_approx // 1024:,} KB, alt='{alt}'")

print(f"Total image payload size: {total_b64_bytes // (1024*1024):,} MB")
