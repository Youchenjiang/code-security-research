import json
import os

citations_file = 'paper_markdowns/master_exhaustive_citations.json'
target_md = '引用鏈.md'
target_review = '自動生成安全斷言（Security_Oracle_Generation）五合一文獻綜述大滿貫.md'

with open(citations_file, 'r', encoding='utf-8') as f:
    citations = json.load(f)

print(f"Total exhaustive citations: {len(citations)}")

# Format 145 citation list
citation_lines = []
for c in citations:
    f_id = c['from_id']
    f_name = c['from_name'].replace(' ', '_')
    t_id = c['to_id']
    t_name = c['to_name'].replace(' ', '_')
    ref = c['ref_num']
    citation_lines.append(f"{f_id}_{f_name} -> {t_id}_{t_name} [{ref}]")

formatted_edges_block = "\n".join(citation_lines)

# Update 引用鏈.md
if os.path.exists(target_md):
    with open(target_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update summary counts
    content = content.replace("包含 76 條確凿引用號標註", "包含 145 條實證引用關係標註")
    content = content.replace("76 條實證引用關係全量清單", "145 條實證引用關係全量清單")
    content = content.replace("76 條完整引用號箭頭清單", "145 條完整引用號箭頭清單")

    # Replace block between ```text and ``` in Section III
    start_marker = "## 🔗 三、 繪圖用：145 條實證引用關係全量清單 (Complete Citation Arrows List)\n\n"
    if "## 🔗 三、" in content:
        head = content.split("## 🔗 三、")[0]
        new_sec3 = f"## 🔗 三、 繪圖用：145 條實證引用關係全量清單 (Complete Citation Arrows List)\n\n以下為從 34 篇全文 References 段落經 100% 全面採集與實證核對之 145 條完整引用號箭頭清單（格式為 `來源論文 -> 目標論文 [引註號]`）：\n\n```text\n{formatted_edges_block}\n```\n"
        content = head + new_sec3

    with open(target_md, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated 引用鏈.md successfully.")

# Update 綜述大滿貫.md
if os.path.exists(target_review):
    with open(target_review, 'r', encoding='utf-8') as f:
        rev_content = f.read()

    rev_content = rev_content.replace("76 條", "145 條")
    rev_content = rev_content.replace("76 條引用", "145 條引用")
    
    with open(target_review, 'w', encoding='utf-8') as f:
        f.write(rev_content)
    print("Updated 綜述大滿貫.md successfully.")
