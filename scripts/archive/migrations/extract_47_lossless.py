import re
import base64
import os

md_path = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\47_Intent_Redirection.md"
assets_dir = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\47_Intent_Redirection_assets"
os.makedirs(assets_dir, exist_ok=True)

with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

pattern = re.compile(r'!\[(.*?)\]\(data:image/([a-zA-Z]+);base64,([^\)]+)\)')

img_idx = 0
def replace_img(match):
    global img_idx
    img_idx += 1
    alt = match.group(1) or f"Figure {img_idx}"
    fmt = match.group(2).lower()
    b64_data = match.group(3)
    
    filename = f"fig_{img_idx}.{fmt}"
    out_img_path = os.path.join(assets_dir, filename)
    
    raw_data = base64.b64decode(b64_data)
    with open(out_img_path, "wb") as img_f:
        img_f.write(raw_data)
    
    size_kb = len(raw_data) // 1024
    print(f"Extracted {filename} ({size_kb:,} KB)")
    
    # Return relative markdown image reference
    return f"![{alt}](./47_Intent_Redirection_assets/{filename})"

new_text = pattern.sub(replace_img, text)

new_md_path = md_path
with open(new_md_path, "w", encoding="utf-8") as f:
    f.write(new_text)

print(f"Done! Markdown size reduced from ~400MB to {os.path.getsize(new_md_path):,} bytes.")
