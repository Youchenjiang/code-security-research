import re
import base64
import io
from PIL import Image

file_path = r"c:\Users\g1014\Documents\GitHub\Youchen\code-security-research\new\papers\category_A_sast_guided_verification\47_Intent_Redirection.md"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

matches = list(re.finditer(r'!\[(.*?)\]\(data:image/([a-zA-Z]+);base64,([^\)]+)\)', text))

for i, m in enumerate(matches):
    alt = m.group(1)
    fmt = m.group(2)
    b64_data = m.group(3)
    
    raw_bytes = base64.b64decode(b64_data)
    img = Image.open(io.BytesIO(raw_bytes))
    print(f"Image {i+1}: size={img.size}, mode={img.mode}, raw_bytes={len(raw_bytes):,} bytes")
    
    # Test lossless PNG compression
    buf_png = io.BytesIO()
    img.save(buf_png, format="PNG", optimize=True)
    png_bytes = buf_png.getvalue()
    
    # Test lossless WebP compression
    buf_webp = io.BytesIO()
    img.save(buf_webp, format="WEBP", lossless=True, quality=100)
    webp_bytes = buf_webp.getvalue()
    
    print(f"  -> Optimized PNG: {len(png_bytes):,} bytes ({len(png_bytes)/len(raw_bytes)*100:.1f}%)")
    print(f"  -> Lossless WebP: {len(webp_bytes):,} bytes ({len(webp_bytes)/len(raw_bytes)*100:.1f}%)")
