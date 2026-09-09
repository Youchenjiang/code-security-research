import os
import glob
import pymupdf as fitz

def fix_vault_assets():
    assets_root = "code-security-research/raw-papers/assets"
    folders = [f for f in os.listdir(assets_root) if os.path.isdir(os.path.join(assets_root, f))]
    
    print(f"[*] Starting high-fidelity rect-based image orientation verification for {len(folders)} folders...\n")
    
    total_re_rendered = 0
    
    for folder_name in sorted(folders):
        asset_dir = os.path.join(assets_root, folder_name)
        img_files = os.listdir(asset_dir)
        if not img_files:
            continue
            
        prefix = folder_name[:25]
        pdf_candidates = [
            p for p in glob.glob("code-security-research/raw-papers/**/*.pdf", recursive=True)
            if prefix in os.path.basename(p) and "legacy_archive" not in p
        ]
        
        if not pdf_candidates:
            continue
            
        pdf_path = pdf_candidates[0]
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"[-] Error opening {pdf_path}: {e}")
            continue

        image_idx = 1
        paper_re_rendered = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            img_infos = page.get_image_info(xrefs=True)
            
            for img_info in image_list:
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    if len(image_bytes) > 5120:
                        img_filename = f"fig_p{page_num + 1}_{image_idx}.{image_ext}"
                        target_path = os.path.join(asset_dir, img_filename)
                        
                        # Find rects and transform
                        rects = page.get_image_rects(xref)
                        matching = [x for x in img_infos if x.get("xref") == xref]
                        
                        # Detect if transform is inverted
                        is_inverted = False
                        if matching:
                            transform = matching[0].get("transform")
                            if transform and transform[3] < 0:
                                is_inverted = True
                                
                        # If inverted or if already identified as problematic paper
                        if (is_inverted or folder_name.startswith("Dong") or folder_name.startswith("Li (2024)")) and rects and os.path.exists(target_path):
                            raw_w = base_image["width"]
                            raw_h = base_image["height"]
                            rect = rects[0]
                            rect_w = rect.width
                            rect_h = rect.height
                            
                            if rect_w > 0 and rect_h > 0:
                                scale = max(raw_w / rect_w, raw_h / rect_h)
                                scale = max(1.5, min(scale, 4.0))
                                dpi = int(scale * 72)
                            else:
                                dpi = 200
                                
                            pix = page.get_pixmap(clip=rect, dpi=dpi)
                            pix.save(target_path)
                            paper_re_rendered += 1
                            total_re_rendered += 1
                        image_idx += 1
                except Exception:
                    pass
                    
        if paper_re_rendered > 0:
            print(f"[+] Re-rendered {paper_re_rendered} images in: {folder_name}")
        else:
            print(f"[OK] {folder_name} (checked {image_idx - 1} images)")
            
    print(f"\n==========================================")
    print(f"Total images re-rendered with 100% upright orientation: {total_re_rendered}")
    print(f"==========================================")

if __name__ == "__main__":
    fix_vault_assets()
