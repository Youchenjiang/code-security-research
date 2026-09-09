import pypdf
import os

pdf_path = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\15_Roshanaei.pdf"
md_path = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\15_Roshanaei.md"

reader = pypdf.PdfReader(pdf_path)
print(f"Extracting {len(reader.pages)} pages...")

header = """---
title: "Enhancing Mobile Security through Comprehensive Penetration Testing"
author: "Maryam Roshanaei"
year: 2024
venue: "Journal of Information Security"
doi: "10.4236/jis.2024.152006"
pages: 24
source: "15_Roshanaei.pdf"
---

# Enhancing Mobile Security through Comprehensive Penetration Testing

> **總頁數**：24 頁
> **作者**：Maryam Roshanaei (Pennsylvania State University)
> **期刊**：Journal of Information Security, 2024, 15, 63-86

---
"""

pages_text = []
for i, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    pages_text.append(f"## Page {i+1}\n\n{text}")

full_md = header + "\n\n" + "\n\n".join(pages_text)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(full_md)

print(f"Saved {md_path}: {len(full_md)} characters, {os.path.getsize(md_path)} bytes.")
